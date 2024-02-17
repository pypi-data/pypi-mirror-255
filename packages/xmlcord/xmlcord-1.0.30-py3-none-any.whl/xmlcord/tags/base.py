import re

from abc import abstractmethod

from ..safeval import shunting_yard

# REFACTOR

TAGS = {}

class EmptyEntry(Exception):
    pass


class InvalidEntry(Exception):
    pass


class Optional:
    def __init__(self, _type, default=None):
        self._type = _type
        self.default = default


class Union:
    def __init__(self, *types):
        self.types = types


class TagArgs:
    def __init__(self):
        self.kwargs = {}

    def add(self, key, value):
        self.kwargs[key] = value

    def __getattr__(self, key):
        return self.kwargs.get(key)

    def __getitem__(self, key):
        return self.kwargs.get(key)

    def __iter__(self):
        return iter(self.kwargs)

    def keys(self):
        return self.kwargs.keys()


class TagConfig:

    def __init__(self, 
        name: str, 
        args: dict = None, 
        singleton: bool = False,
        content: bool = True
    ):
        self.name = name
        self.args = args or {} 
        self.singleton = singleton
        self.content = content


def try_converting_var(val, _type):
    try:
        val = _type(val)
    except TypeError:
        raise Exception(f"Incorrect data type, got: {type(val)}, expected: {_type}")

    return val


def get_value(self, arg_name, arg_type):
    if arg_name in self._static_kwargs:
        value = self._static_kwargs[arg_name]
    
    elif arg_name in self._dynamic_kwargs:
        ref = self._dynamic_kwargs[arg_name]
        value = shunting_yard(self, ref)

    else:
        if isinstance(arg_type, Optional):
            value = arg_type.default
        else:
            raise Exception(f"Missing required argument: {arg_name}")

    return value


def validate_value(value, arg_type):
    if type(arg_type) == Optional:
        if type(value) != arg_type._type and value:
            value = try_converting_var(value, arg_type._type)

    elif type(arg_type) == Union:
        if type(value) not in arg_type.types:
            raise Exception("Incorrect data type")

    else:
        if type(value) != arg_type:
            value = try_converting_var(value, arg_type)

    return value

# handles argument calculation and type annotations 
#
# too much is happening here, BAD
#
# args should be parsed and resolved on init,
# and passed as args object on render for convenience
def on_render():
    def wrapper(func):
        async def inner(self, *args, **kwargs):
            args_to_pass = TagArgs()

            for arg_name, arg_type in self._config.args.items():

                val = get_value(self, arg_name, arg_type)

                # val can be 0, so this must be None
                if val is None:
                    args_to_pass.add(arg_name, None)
                    continue

                val = validate_value(val, arg_type)
                
                args_to_pass.add(arg_name, val)

            return await func(self, args_to_pass)
        return inner
    return wrapper


class MetaTag(type):

    def __new__(cls, class_name, bases, attrs):
        new_class = type.__new__(cls, class_name, bases, attrs)

        config = attrs['_config']

        TAGS[config.name] = new_class

        return new_class
        

# need to return 'get_arg' back
class Tag(metaclass=MetaTag):

    _config = TagConfig(
        name="base"
    )

    def __init__(self, kwargs: str, parent = None):
        self.parent = parent
        self.children = []

        self._content = None
        self._state_vars = {}

        # holds {key: value} pairs
        self._static_kwargs = {
            k: v for k,v in re.findall(
                r"([a-zA-Z0-9]*?)=[\"](.*?)[\"]", kwargs
            )
        }
        # holds {key: reference} pairs
        # only available at render time
        self._dynamic_kwargs = {
            k: r for k,r in re.findall(
                r"([a-zA-Z0-9]*?)={(.*?)}", kwargs
            )
        }

    @classmethod
    @property
    def name(cls):
        return cls._config.name

    @classmethod
    @property
    def singleton(cls):
        return cls._config.singleton

    @property
    def root(self):
        tag = self
        while (parent := tag.parent):
            tag = parent
        return tag

    @property
    def ui(self):
        return self.root._ui

    def first_ancestor(self, name):
        tag = self.parent
        while tag and tag.name != name:
            tag = tag.parent
        return tag

    def get_state(self, key, default=None):
        return self._state_vars.get(key, default)

    def update_state(self, _dict: dict=None, **kwargs):
        if _dict:
            kwargs = {**_dict, **kwargs}
        self._state_vars = {**self._state_vars, **kwargs}

    def parse_text(self, text):

        # this doesn't need to be here
        def repl(match):
            if (result := shunting_yard(self, match[1])) is None:
                return ""

            return str(result)

        return re.sub(r"{([^\{\}]+?)}", repl, text)

    async def render_content(self):
        return self.content.format(*(await self.render_children()))

    # might not be necessary
    @property
    def content(self):
        return self.parse_text(self._content)

    def set_content(self, content):
        if not content:
            self._content = ''
        start = 0
        end = None
        self._content = content[start:end]

    async def render_children(self) -> list:
        children_contents = []

        for child in self.children:

            content = await child.render()

            if not child.singleton:
                children_contents.append(
                    # without this we would have 'None' whenever
                    # a child does not return any content
                    content or ''
                )

        return children_contents

    @abstractmethod
    async def render(self, *_):
        ...

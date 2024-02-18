import re

from .base import TAGS 

from .root import RootTag
from .base import *
from .control import *


def new_tag(name, *args, **kwargs):
    if cls := TAGS.get(name):
        return cls(*args, **kwargs)

    raise Exception(f"Unknown tag '{name}'")


# removes leading and trailing whitespaces and tabs
def normalize_form(form) -> str:

    lines = []

    for line in form.split('\n'):

        match = re.fullmatch(r"[ \t]*(.*?)[ \t]*", line)

        lines.append(match.group(1))

    return '\n'.join(lines)


def parse(form: str) -> RootTag:
    # stacks opening tags and pops them using closing tags 
    stack = []

    # we are changing form during iteration so we need to
    # keep track of how many characters have been offset
    offset = 0

    form = normalize_form(form)
    
    # matches either opening or closing tag
    # cannot handle newlines here bc tags would "compete" for the newline
    for match in re.finditer(r"(\n?)<(/?)([a-zA-Z0-9]+)(.*?)(/?)>", form):

        # singleton tags should be explicitly defined in TagConfig
        # this would simplify the algorithm a lot
        br, closing, name, kwargs, contentless = match.groups()

        # avoids matching discord formatting elements such as <t:timestamp>
        if kwargs:
            if kwargs[0] == ':':
                continue
        
        # adds opening tags to stack along with its match start and end
        if not closing:
            tag = new_tag(name, kwargs, stack[-1][0] if stack else None)

            singleton = tag.singleton
            contentless = contentless or (not tag._config.content)
            # singletons will also be appened to stack, but are popped immediatelly
            stack.append((tag, match.start() - offset, match.end() - offset))

        # handles the tag closing
        if closing or singleton:
            top, start, end = stack.pop()

            # ensures the form is valid by checking if the closing tag matches the
            # top of the stack
            if top.name != name:
                raise SyntaxError(
                    f"Incompatible opening tag {top.name} with closing tag /{name}"
                )

            # the content of the tag is the string between match end of the opening tag
            # and the match start of the closing tag, while accounting for offset
            content = form[end:match.start() - offset]

            # strips leading and trailing newlines if present
            # to sanitize tag content
            # if not contentless and content:
            #     if content[0] == '\n':
            #         content = content[1:]

            #     if content[-1] == '\n':
            #         content = content[:-1]

            top.set_content(content)

            # the original form is stripped of the tag and it's content
            # and replaced with {} which will later be formatted by the 
            # tag itself at render time to produce dynamic content
            form = form[:start] + \
                ("" if contentless else "{}") + \
                form[match.end()-offset:]

            # offset keeps track of how many characters were removed from the form
            # by taking the index of the end of the closing tag and decrementing the
            # start index of the opening tag, then adding 2 if the tag isn't contentless
            # since we add 2 characters, 
            # but since the start and end indexes aren't dynamic
            # and do not account for the form changes we need to decrement offset here
            # to account for form changes manually 
            offset += match.end() - offset - start - (0 if contentless else 2)
            
            # if the stack isn't empty the current tag
            # will be appended to the top of the stack as child
            if stack:
                stack[-1][0].children.append(top)
            # if the stack is empty we are currently handling the closing part
            # of the root element and we can return it and finish parsing
            else:
                return top

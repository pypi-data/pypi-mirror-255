from .base import Tag, on_render, TagConfig
from ..hooks import MessageHook, ActionHook


# suppresses registering of hooks
class BlankUi:

    def __getattribute__(self, name):
        return lambda *_, **__: None

# REFACTOR

class RootTag(Tag):

    _config = TagConfig(name="root")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ui = None

        self.entry_index = 0
        self.current_entry = None
        self.used_entry_chars = []
        
        self.rerender = False
        self.config = {}
        self.empty_entry = None

    def inject_ui(self, ui):
        self._ui = ui

        return self

    def double_render(self):
        self.rerender = True

    # convenient hooks that all templates will have by default
    def default_hooks(self):
        
        # might not need an async wrapper
        async def wrapper(trigger):
            self.ui.discard()

        self.ui.register_hook(
            MessageHook("-del", checks=[
                lambda trigger: trigger.user.id == self.ui.renderer.author.id
            ]),
            func=wrapper
        )

        self.ui.register_hook(
            ActionHook("delete", checks=[
                lambda trigger: True
            ]),
            func=wrapper
        )

    # special case, doesn't need decorator
    async def render(self):

        self.entry_count = 0
        self.used_entry_chars = []

        await self.render_children()

        # we want to avoid adding hooks to non-interactive templates,
        # might be a little hacky
        if self.ui.input_hooks:
            self.default_hooks()
        
        # this could get dangerous
        if self.rerender:
            self.rerender = False
            await self.render()
        
        return self

    def next_entry(self):
        if self.entry_count > self.entry_index + 1:
            self.entry_index += 1

    def previous_entry(self):
        if self.entry_index > 0:
            self.entry_index -= 1

    def message_tags(self):

        messages = []
        stack = self.children

        while stack:
            child = stack.pop()

            if child.name == "message":
                messages.insert(0, child)

            else:
                stack += child.children

        return messages
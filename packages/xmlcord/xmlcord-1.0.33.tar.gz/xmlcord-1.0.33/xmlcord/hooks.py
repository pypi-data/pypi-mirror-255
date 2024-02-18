from __future__ import annotations

import discord
import re

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.hooks import HookTrigger


class Hook:

    def __init__(self, *_, checks=[lambda _: True]):
        self.checks = checks

    def matches(self, trigger: HookTrigger):
        if trigger.type != type(self):
            return False

        for check in self.checks:
            if not check(trigger):
                return False

        return True


class ReactionHook(Hook):

    def __init__(self, emoji: str, *_, **kwargs):
        super().__init__(**kwargs)

        self.emoji = emoji

    def matches(self, trigger: HookTrigger):
        if not super().matches(trigger):
            return

        # print(self.emoji, trigger.data, type(trigger.data))

        if self.emoji == trigger.data:
            return True


class MessageHook(Hook):

    def __init__(self, expression: str, *_, **kwargs):
        super().__init__(**kwargs)

        self.expression = expression

    def matches(self, trigger: HookTrigger):
        if not super().matches(trigger):
            return None

        # print(self.expression, trigger.data, type(trigger.data))

        if match := re.fullmatch(self.expression, trigger.data, re.DOTALL):

            # this might not even be needed

            trigger.set_match(match)

            return match


class ActionHook(Hook):

    def __init__(self, action: str, *_, **kwargs):
        super().__init__(**kwargs)

        self.action = action

    def matches(self, trigger: HookTrigger):
        if not super().matches(trigger):
            return None

        if self.action == trigger.data:
            return True


class HookTrigger:

    def __init__(self, type: Hook, data: str, user: discord.User):
        self.type = type
        self.data = data
        self.user = user

        self.response = {}
        self.resolved = False
        self.match: re.Match = None

    # API for setting a match object in the case of regex match
    def set_match(self, match: re.Match):
        self.match = match

    def delete_input(self):
        return self.response.get('delete_input', True)

    def resolve(self, response=None):
        self.resolved = True
        if response:
            self.response = response

    def is_resolved(self) -> bool:
        return self.resolved

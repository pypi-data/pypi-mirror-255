import asyncio
import discord

from discord import Embed

from .listener import DiscordListener

from .tags.base import Tag

from .hooks import HookTrigger
from .hooks import ReactionHook, MessageHook


class TemplateDisplay:

    def __init__(self, context):
        self.context = context

        self.messages: [discord.Message] = []
        # discord.py returns empty list when attempting to retrieve message reactions,
        # so we need to manually keep track of all the reactions;
        # the issue with this approach is that if someone were to manually
        # delete the bot reaction it wouldn't be automatically repaired
        self.reactions: {int: [str]} = {}

    # returns all message tags from root;
    # should be handled in root
    def message_tags(self, root) -> [Tag]:
        return [t for t in root.children if t.name == 'message']
        # return root.message_tags()

    def get_message_ids(self) -> [int]:
        return [message.id for message in self.messages]

    async def update_reactions(self, message, reactions):
        # check if reactions need updating
        if reactions == (curr_reactions := self.reactions.get(message.id, [])):
            return

        if curr_reactions:
            await message.clear_reactions()
        # manually keeping track of the reactions we are adding
        self.reactions[message.id] = reactions

        for emoji in reactions:
            await message.add_reaction(emoji)

    # creates and publishes a new message object while adding
    # it to the messages list
    async def new_message(self, tag) -> discord.Message:
        message = await self.context.channel.send(content=tag.message, embed=tag.embed)

        self.messages.append(message)

        return message

    # retrieves message object from messages list
    def get_message(self, index) -> discord.Message:
        message = None

        if index <= len(self.messages) - 1:
            message = self.messages[index]

        return message

    # checks if there are any leftover message objects 
    # that do not match to any message tags and deletes them
    async def message_leftover_cleanup(self, root):
        del_message_tasks = []

        # deletes all the messages with index of len(tags) and higher
        for message in self.messages[len(self.message_tags(root)):]:
            del_message_tasks.append(asyncio.create_task(message.delete()))

            self.messages.pop(index + 1)

        if del_message_tasks:
            await asyncio.gather(*del_message_tasks)

    # first post all embeds then add reactions
    async def construct(self, root):
        reactions = []

        for tag in self.message_tags(root):

            message = await self.new_message(tag)

            reactions.append(asyncio.create_task(
                self.update_reactions(message, tag.reactions)
            ))

        await asyncio.gather(*reactions)

    # updates the message objects with new content and embed data
    # and also updates the reactions if needed
    async def update(self, root):
        reactions = []

        for index, tag in enumerate(self.message_tags(root)):

            if message := self.get_message(index):
                await message.edit(content=tag.message, embed=tag.embed)
            else:
                message = await self.new_message(tag)
        
            reactions.append(asyncio.create_task(
                self.update_reactions(message, tag.reactions)
            ))

        await self.message_leftover_cleanup(root)
        await asyncio.gather(*reactions)

    # deletes all messages
    async def discard(self):
        tasks = []

        for message in self.messages:
            tasks.append(asyncio.create_task(message.delete()))

        await asyncio.gather(*tasks)

    # deletes all reactions; redundant?
    async def deactivate(self):
        for message in self.messages:
            await self.update_reactions(message, [])


class DiscordRenderer:

    def __init__(self, context):
        self.context = context

        # might rename this to event_receiver?
        self.trigger_matcher = None
        self.trigger_resolver = None
        
        self.display = TemplateDisplay(context)
        self.listener = DiscordListener()

        self.swap = False
        self.queued_error = None
        self.error_message = None

    @property
    def server(self) -> discord.Guild:
        return self.context.guild

    @property
    def channel(self) -> discord.TextChannel:
        return self.context.channel

    @property
    def author(self) -> discord.Member:
        return self.context.author

    @property
    def messages(self) -> [int]:
        return self.display.get_message_ids()

    # meh, would be best to find a way around this
    def inject_trigger_matcher(self, matcher):
        self.trigger_matcher = matcher

    def inject_trigger_resolver(self, resolver):
        self.trigger_resolver = resolver

    def match_trigger(self, trigger):
        return self.trigger_matcher(trigger)

    # pushes the trigger into interface's receive_event loop
    # and waits for a response; 
    async def resolve_trigger(self, trigger) -> HookTrigger:
        # if event_dispatcher returns it indicates 
        # that the event loop has ended 
        if await self.trigger_resolver():
            # returning None signals to listener that the template
            # was disabled and clean-up is not to be attempted
            #
            # this will however prevent messages from getting cleaned up,
            # if we ever try to terminate the template with message input
            return

        # trigger should change to ResolvedTrigger to indicate
        # that it has been resolved
        if trigger.is_resolved():
            return trigger

    # eh
    def send_error(self, error):
        self.queued_error = self.context.channel.send(
            embed=discord.Embed(description=error, color=int('cc2040', 16))
        )

    # gets the dm_channel with the author,
    # creates a new channel if it doesn't exist
    async def get_dm_channel(self) -> discord.TextChannel:
        if not self.context.author.dm_channel:
            await self.context.author.create_dm()

        return self.context.author.dm_channel

    async def construct(self, root, register_listener=True):
        # this is stupid
        if root.config.get('channel') == 'dm' and not self.swap:
            # this is even stupider
            self.context.channel = await self.get_dm_channel()

        await self.display.construct(root)

        if register_listener:
            self.listener.add_renderer(self)

    # needs to be capable of swiching channels 
    async def update(self, root):

        # meh, refactoring still needed
        if self.error_message:
            try:
                await self.error_message.delete()
            # people are dumb and manually delete the
            # error message sometimes
            except discord.errors.NotFound:
                pass
            self.error_message = None

        if self.queued_error:
            self.error_message = await self.queued_error
            self.queued_error = None

        if root.config.get('refresh') == 'resend':
            await self.display.construct(root)
        else:
            await self.display.update(root)

    def swap_channel(self, channel_id):
        self.swap = True
        channel = self.context.guild.get_channel(int(channel_id))

        # BAD, NO
        self.context.channel = channel

        self.display = TemplateDisplay(self.context)

    async def deactivate(self):
        self.listener.remove_renderer(self)
        await self.display.deactivate()

        self.display = None

    async def discard(self):
        self.listener.remove_renderer(self)
        await self.display.discard()

        self.display = None

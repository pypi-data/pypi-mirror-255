import discord

from discord import Embed
from datetime import datetime

from .base import Tag, on_render, TagConfig, Optional

from ..hooks import ReactionHook, HookTrigger


EMOJIS = {
    'up': "⬆",
    'down': "⬇",
    'checkmark': "✅",
    'cross': "<:red_cross_5:744249221011472444>",
    'file': "📁"
}


class Message(Tag):

    _config = TagConfig(name="message")

    def add_reaction(self, emoji, event=None):
        self.reactions.append(emoji)

    @on_render()
    async def render(self, args):
        self.embed = None
        self.reactions = []
        self.message = await self.render_content()


class EmbedTag(Tag):

    _config = TagConfig(
        name="embed",
        content=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # this might eventually cause issues,
        # might be best to create separate API for managing embeds
        self.embed = discord.Embed()

    @on_render()
    async def render(self, args):
        self.embed.clear_fields()
        self.reactions = []
        await self.render_children()
        
        self.first_ancestor('message').embed = self.embed

        return ""


class DescriptionTag(Tag):

    _config = TagConfig(name="description", content=False)

    @on_render()
    async def render(self, args):
        descption = await self.render_content()
        self.first_ancestor("embed").embed.description = descption 


class TitleTag(Tag):

    _config = TagConfig(name="title", content=False)

    @on_render()
    async def render(self, args):
        title = await self.render_content()  
        self.first_ancestor("embed").embed.title = title
        

class ColorTag(Tag):

    _config = TagConfig(
        name="color",
        args={
            "value": str
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.color = int(args.value, 16)


class FieldTag(Tag):

    _config = TagConfig(
        name="field",
        args={
            "name":   str,
            "inline": Optional(bool, False)
        }
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.add_field(
            name=args.name, 
            inline=args.inline, 
            value=await self.render_content()
        )


class ImageTag(Tag):

    _config = TagConfig(
        name="image",
        args={
            "url":   str,
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.set_image(url=args.url)


class ThumbnailTag(Tag):

    _config = TagConfig(
        name="thumbnail",
        args={
            "url":   str,
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.set_thumbnail(url=args.url)


class FooterTag(Tag):

    _config = TagConfig(
        name="footer",
        args={
            "url": Optional(str, ""),
        }
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.set_footer(
            icon_url=args.url, 
            text=await self.render_content()
        )


class TimestampTag(Tag):

    _config = TagConfig(
        name="timestamp",
        args={
            "value": int
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):
        if args.value:
            ts = datetime.fromtimestamp(args.value)
            self.first_ancestor("embed").embed.timestamp = ts


class CodeTag(Tag):

    _config = TagConfig(
        name="code", 
        args={
            "lang": Optional(str, "")
        }
    )

    @on_render()
    async def render(self, args):
        content = await self.render_content()

        return f"```{args.lang}\n{content}```"


class ReactionTag(Tag):

    _config = TagConfig(
        name="r",
        args={
            "emoji": str
        }
    )
    
    async def on_reaction(self, trigger: HookTrigger):
        self.update_state({
            'value': 1,
            'user': trigger.user.id
        })
        
        self.rendered_content = await self.render_content()

        trigger.resolve()

    @on_render()
    async def render(self, args):

        emoji = EMOJIS[args.emoji]
        
        self.first_ancestor('message').add_reaction(emoji)

        self.ui.register_hook(
            ReactionHook(
                emoji,
                checks=[lambda t: t.user.id == self.ui.renderer.author.id]
            ), 
            func=self.on_reaction
        )

        if self.get_state('value') == 1:

            self.update_state(value=0)

            return self.rendered_content


class ClassifiedTag(Tag):

    _config = TagConfig(
        name="c",
        args={
            "role": str
        }
    )

    @on_render()
    async def render(self, args):
        context = self.ui.renderer.context
        member = context.author

        if int(args.role) in [r.id for r in member.roles]:
            return await self.render_content()
        else:
            return '\n[ REDACTED ]'


# refactoring still needed here 
class UserContextTag(Tag):

    _config = TagConfig(
        name="user",
        args={
            "id": str,
            # don't render if no user object
            "strict": Optional(bool, False),
            "reqPresence": Optional(bool, False)
        }
    )

    def get_member_info(cls, member):
        return [
            member.name + '#' + member.discriminator,
            member.nick or member.name,
            [r.id for r in member.roles],
            str(member.avatar_url)
        ]

    @on_render()
    async def render(self, args):
        context = self.ui.renderer.context

        if user_id := args.id:

            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                return ''

            context = self.ui.renderer.context
            member_info = []

            if fetchUsers := self.first_ancestor('fetchUsers'):
                
                # member is not guaranteed to exist here
                if member := fetchUsers.get_state(user_id):
                    # saves the member info in root for future use,
                    # in case the member leaves the server
                    self.root.update_state({
                        user_id: self.get_member_info(member)
                    })

                    member_info = self.get_member_info(member)

            elif member := await context.guild.fetch_member(user_id):
                member_info = self.get_member_info(member)

            elif mi := self.root.get_state(user_id) and not args.reqPresence:
                member_info = mi

            if member_info:
                self.update_state({
                    'name':        member_info[0],
                    'nick':        member_info[1] or member_info[0],
                    'roles':       member_info[2],
                    'avatar_url':  member_info[3],
                    'user_object': member if type(member) is discord.Member else None
                })

                if args.reqPresence:
                    self.update_state({
                        'user': member
                    })

            elif args.strict:
                return ""

            else:
                self.update_state({
                    'name':        f"<@{user_id}>",
                    'nick':        f"<@{user_id}>",
                    'roles':       [],
                    'avatar_url':  None,
                    'user_object': None
                })

            return await self.render_content()
            
        return ''


class FetchMembers(Tag):

    _config = TagConfig(name="fetchUsers")

    @on_render()
    async def render(self, args):
        context = self.ui.renderer.context

        members = []

        async for member in context.guild.fetch_members():
            members.append(member)

            self.update_state({member.id: member})

        return await self.render_content()


class ChannelContext(Tag):

    _config = TagConfig(
        name="channelContext",
        args={
            "id": int
        }
    )

    @on_render()
    async def render(self, args):

        context = self.ui.renderer.context

        if not (channel := context.guild.get_channel(channel_id=args.id)):
            return

        members = []
        roles   = []

        for target, overwrite in channel.overwrites.items():

            if type(target) is discord.Member:
                members.append(target.id)

            elif type(target) is discord.Role:
                roles.append(target.id)

        self.update_state({
            "channel": channel,
            "hashtag": f"<#{args.id}>" if id else None,
            "ch_members": members,
            "ch_roles":   roles
        })

        return await self.render_content()


class SetChannelPerms(Tag):

    _config = TagConfig(
        name="chSetPerms",
        args={
            "channel": discord.TextChannel,
            "overwrite": int,
            "member": Optional(discord.Member),
            "role": Optional(discord.Role)
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):

        if args.member:
            target = args.member

        elif args.role:
            target = args.role

        else:
            raise Exception("Either member or role must be specified.")

        if target:
            await args.channel.set_permissions(
                target, 
                overwrite=discord.PermissionOverwrite(
                    # gotta do this hacky shit because discord.py
                    **{k:v for k,v in discord.Permissions(args.overwrite)}
                )
            )
        
from .base import Tag, on_render, TagConfig, Optional


    
class MoveTag(Tag):

    _config = TagConfig(
        name='move',
        args={
            'dir': str,
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):
        if args.dir == 'up':
            self.root.previous_entry()

        elif args.dir == 'down':
            self.root.next_entry()

        # there might be a cleaner way to handle this
        # self.root.double_render()


class DiscardTag(Tag):

    _config = TagConfig(
        name='discard',
        singleton=True
    )

    @on_render()
    async def render(self, args):
        self.ui.discard()


class CleanupTag(Tag):

    _config = TagConfig(
        name='cleanup',
        singleton=True
    )

    @on_render()
    async def render(self, args):
        self.ui.clean_up()


class ForwardTag(Tag):

    _config = TagConfig(
        name="forward",
        args={
            "channel": int,
            "mode":    Optional(str, "view")
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):
        self.ui.forward(args.channel, args.mode)
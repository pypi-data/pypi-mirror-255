from .base import Tag, on_render, TagConfig, Optional


def md(*mds):
    return f"\u001B[{';'.join(str(md) for md in mds)}m"

END = "\u001B[0m"

colors = { 
    "gray":   30,
    "red":    31,
    "green":  32,
    "yellow": 33,
    "blue":   34,
    "pink":   35,
    "cyan":   36,
    "white":  37,
}

backgrounds = {
    "darkblue": 40,
    "organe":   41,
    "gray3":    42,
    "gray2":    43,
    "gray1":    44,
    "indigo":   45,
    "gray0":    46,
    "white":    47,
}


class Bold(Tag):

    _config = TagConfig(name="b")

    @on_render()
    async def render(self, args):
        return md(1) + await self.render_content() + END


class Underline(Tag):

    _config = TagConfig(name="u")

    @on_render()
    async def render(self, args):
        return md(4) + await self.render_content() + END


class Tab(Tag):

    _config = TagConfig(
        name="t",
        args={
            "i": Optional(int, 1)
        },
        singleton=True
    )

    @on_render()
    async def render(self, args):
        return "    " * args.i


class StyleTag(Tag):

    _config = TagConfig(
        name="style",
        args={
            "color": Optional(str),
            "background": Optional(str),
        }
    )

    @on_render()
    async def render(self, args):
        mds = []

        if (clr := args.color) != None:
            mds.append(colors[clr])
        if (bkg := args.background) != None:
            mds.append(backgrounds[bkg])

        self.md = md(*mds)

        # allows for nesting sytles without losing 
        # effects by a nested END terminator
        cont = None
        if (style := self.first_ancestor('style')):
            cont = style.md

        return self.md + await self.render_content() + (cont or END)
            
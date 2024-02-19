# PaperTools

![](https://avatars.githubusercontent.com/u/159441854?s=200&v=4)

[![GPL](https://img.shields.io/github/license/paper-devs/papertools?color=2f2f2f)](https://github.com/paper-devs/papertools/blob/main/LICENSE) ![](https://img.shields.io/pypi/pyversions/papertools?color=2f2f2f) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Discord](https://img.shields.io/discord/991705424866852977?color=%237289DA&label=Paper%20Devs&logo=discord&logoColor=white)](https://discord.gg/JV8CmQM7ma) [![Read the Docs](https://readthedocs.org/projects/papertools/badge/?version=latest)](https://papertools.readthedocs.io/en/latest/)

PaperTools is a module which offers tons of usefull features for [discord.py](https://github.com/Rapptz/discord.py) bots.

## Quick Links
- [Discord Server](https://discord.gg/JV8CmQM7ma)
- [Read the Docs](https://papertools.readthedocs.io/en/latest/)
- [PyPI Homepage](https://pypi.org/project/papertools/)

# Install
To install the library, you need the latest version of pip and minimum Python 3.9

> Stable version
```
pip install papertools
```

> Unstable version (this one gets more frequent changes)
```
pip install git+https://github.com/paper-devs/papertools
```

# Examples
In-depth examples are located in the [examples folder](https://github.com/paper-devs/papertools/tree/main/examples)

Here's a quick example:

```py
import papertools

import discord

converter = papertools.Converter()
timetools = papertools.TimeTools()
pg = papertools.paginator

class MyBot(commands.Bot):

    def __init__(self) -> None:
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def on_ready(self) -> None:
        print("I'm online!")


class ExampleCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context):
        embeds = pg.embed_creator("Very long text"*10000, 1995, prefix='```\n', suffix='\n```')
        paginator = pg.Paginator(bot, embeds, ctx, invoker=ctx.author.id)
        paginator.default_pagination()
        await paginator.start()

    @commands.command()
    async def fromsuffix(self, ctx: commands.Context, string: str) -> None:
        fromsuffix_string = converter.fromsuffix(string)
        await ctx.send(fromsuffix_string)

    @commands.command()
    async def tosuffix(self, ctx: commands.Context, number: int) -> None:
        tosuffix_string = converter.fromsuffix(number)
        await ctx.send(tosuffix_string)

    @commands.command()
    async def humanize_time(self, ctx: commands.Context, number: int, short: bool) -> None:
        humanized_time = timetools.humanize(number, short)
        await ctx.send(humanized_time)

bot = MyBot()
bot.run("token here")
```
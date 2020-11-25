import io
import os
import re
import json
import logging
import textwrap
import contextlib
from traceback import format_exception

import discord
from discord.ext import commands

from utils.util import clean_code, Pag

with open("conf.json", "r") as f:
    config = json.load(f)


intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=".",
    case_insensitive=True,
    description="The bot powering the DPY Anti-Spam community.",
    intents=intents,
)

logger = logging.getLogger(__name__)

# Use regex to parse mentions, much better than only supporting
# nickname mentions (<@!1234>)
# This basically ONLY matches a string that only consists of a mention
mention = re.compile(r"^<@!?(?P<id>\d+)>$")

bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with guild security."))

    print(f"{bot.user.name} is now ready\n-----")


@bot.event
async def on_message(message):
    # Ignore messages sent by bots
    if message.author.bot:
        return

    # Whenever the bot is tagged, respond with its prefix
    if mention.match(message.content):
        await message.channel.send(f"My prefix here is `.`", delete_after=15)

    await bot.process_commands(message)


@bot.command(description="Log the bot out.")
@commands.is_owner()
async def logout(ctx):
    await ctx.send("Cya :wave:")
    await bot.logout()


@bot.command(name="eval", aliases=["exec"])
@commands.is_owner()
async def _eval(ctx, *, code):
    """
    Evaluates given code.
    """
    code = clean_code(code)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
    }

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}",
                local_variables,
            )

            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"

    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    pager = Pag(
        timeout=180,
        use_defaults=True,
        entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
        length=1,
        prefix="```py\n",
        suffix="```",
    )

    await pager.start(ctx)


# Load all extensions
if __name__ == "__main__":
    for ext in os.listdir("./cogs/"):
        if ext.endswith(".py") and not ext.startswith("_"):
            try:
                bot.load_extension(f"cogs.{ext[:-3]}")
            except Exception as e:
                print(
                    "An error occurred while loading ext cogs.{}: {}".format(
                        ext[:-3], e
                    )
                )

    bot.run(config["token"])
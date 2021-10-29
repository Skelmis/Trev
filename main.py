import io
import os
import re
import logging
import textwrap
import contextlib
from traceback import format_exception

import aiohttp
import discord
from antispam import AntiSpamHandler, Options
from discord.ext import commands, tasks

from utils.util import clean_code, Pag

token = os.getenv("TOKEN")
patch = os.getenv("UPTIME_PATCH")

intents = discord.Intents.all()

PREFIX = "py."


async def get_prefix(bot, message):
    prefix = PREFIX
    if message.content.casefold().startswith(prefix.casefold()):
        # The prefix matches, now return the one the user used
        # such that dpy will dispatch the given command
        prefix_length = len(prefix)
        prefix = message.content[:prefix_length]

    return commands.when_mentioned_or(prefix)(bot, message)


bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    description="The bot powering the DPY Anti-Spam community",
    intents=intents,
    help_command=None,
    activity=discord.Game(name="with guild security"),
)

options = Options()
options.ban_threshold = 1
options.delete_spam = True
options.ignored_members.add(271612318947868673)
bot.handler = AntiSpamHandler(bot, options=options)

logger = logging.getLogger(__name__)

# Use regex to parse mentions, much better than only supporting
# nickname mentions (<@!1234>)
# This basically ONLY matches a string that only consists of a mention
mention = re.compile(r"^<@!?(?P<id>\d+)>$")


@bot.event
async def on_ready():
    print(f"{bot.user.name} is now ready\n-----")

    await bot.handler.add_guild_log_channel(903695242455298058, 780784732484141077)


@bot.event
async def on_message(message):
    # Ignore messages sent by bots
    if message.author.bot:
        return

    await bot.handler.propagate(message)

    # Whenever the bot is tagged, respond with its prefix
    if match := mention.match(message.content):
        if int(match.group("id")) == bot.user.id:
            await message.channel.send(f"My prefix here is `{PREFIX}`", delete_after=15)

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    if member.id == 493937661044719626:
        dev_role = member.guild.get_role(780788829917151263)
        await member.add_roles(dev_role)
        return

    channel = bot.get_channel(780817944728174632)
    start_chan = bot.get_channel(780784732966879233)
    await channel.send(
        f"Welcome {member.mention}!\nPlease check out {start_chan.mention} before continuing. Otherwise, enjoy the "
        f"server! "
    )


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
        entries=[result[i : i + 2000] for i in range(0, len(result), 2000)],
        length=1,
        prefix="```py\n",
        suffix="```",
    )

    await pager.start(ctx)


@tasks.loop(minutes=10)
async def update_uptime():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=f"https://betteruptime.com/api/v1/heartbeat/{patch}"
        ):
            pass


@update_uptime.before_loop
async def before_update_uptime():
    await bot.wait_until_ready()


# Load all extensions
if __name__ == "__main__":
    update_uptime.start()

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

    bot.run(token)

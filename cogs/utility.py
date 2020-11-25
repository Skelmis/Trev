import asyncio

import discord
from discord.ext import commands

from utils.util import get_message


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command()
    @commands.has_role(780785638244876309)
    async def release(self, ctx):
        """Create & send a new release notif"""
        release_role_id = 780792539761999912
        release_ping_str = f"<@&{release_role_id}>"

        questions = [
            [
                "What type of release is this?",
                "1 | Regular Release\n2 | Security Release",
            ],
            ["What version are you releasing?", "\u2009"],
            ["What is the content for this release?", "\u2009"],
        ]
        answers = [
            await get_message(self.bot, ctx, question[0], question[1])
            for question in questions
        ]

        color_enum = {
            "1": 0x2C3E50,  # Midnight grey
            "2": 0xFF2800,  # Vibrant red
        }
        color = color_enum.get(answers[0], 0x2C3E50)

        tag = answers[1]
        if "v" not in tag.lower():
            tag = f"V{tag}"
        tag = tag.capitalize()
        tag = tag.replace(" ", "")

        desc = answers[2]
        desc += "\n\n------------\nGet it with:\n`pip install -U Discord-Anti-Spam`"

        embed = discord.Embed(
            title=f"**Release:** `{tag}`",
            description=desc,
            color=color,
        )
        m = await ctx.send("Preview:\nDo you want to send this?", embed=embed)
        await m.add_reaction("👍")

        def check(reaction, user):
            return user.id == ctx.author.id and str(reaction.emoji) == '👍'

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('👎')
        else:
            await ctx.send('👍')

            channel = await self.bot.fetch_channel(780786972859564043)
            await channel.send(release_ping_str, embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))

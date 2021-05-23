import asyncio

import discord
from discord.ext.buttons import Paginator


class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass


def clean_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


async def get_message(
    bot, ctx, content_one="Default Message", content_two="\uFEFF", timeout=100
):
    """
    This function sends an embed containing the params and then waits for a message to return
    """
    embed = discord.Embed(
        title=f"{content_one}",
        description=f"{content_two}",
    )
    await ctx.send(embed=embed)
    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if msg:
            return msg.content
    except asyncio.TimeoutError:
        return False


async def review_embed(bot, ctx, embed) -> bool:
    """Given an embed, send it and wait for a review"""
    m = await ctx.send("Preview:\nYes | No", embed=embed, delete_after=35)
    await m.add_reaction("👍")
    await m.add_reaction("👎")

    def check(reaction, user):
        return user.id == ctx.author.id and str(reaction.emoji) in ["👍", "👎"]

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
    except asyncio.TimeoutError:
        return False
    else:
        if str(reaction.emoji) == "👍":
            return True
        return False

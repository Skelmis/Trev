import datetime
import logging

import disnake
from disnake import TextInputStyle
from disnake.ext import commands

from utils.util import get_message, review_embed

log = logging.getLogger(__name__)


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"{self.__class__.__name__} Cog has been loaded")

    @commands.slash_command(
        dm_permission=False,
        default_member_permissions=disnake.Permissions(manage_guild=True),
    )
    async def release(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        package=commands.Param(
            choices=["discord-anti-spam", "alaric", "function-cooldowns"],
            description="Which package this release is for",
        ),
    ):
        """Notify people of a new release"""
        release_role_id = 780792539761999912
        release_ping_str = f"<@&{release_role_id}>"

        custom_id = f"release_modal:{interaction.id}"
        await interaction.response.send_modal(
            title="Release notes",
            custom_id=custom_id,
            components=[
                disnake.ui.TextInput(label="Release version", custom_id="version"),
                disnake.ui.TextInput(
                    label="Notable changes",
                    custom_id="changes",
                    style=TextInputStyle.long,
                ),
                # disnake.ui.Select(
                #     custom_id="package",
                #     options=["discord-anti-spam", "alaric", "function-cooldowns"],
                # ),
            ],
        )
        modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == custom_id
            and i.author.id == interaction.author.id,
            timeout=300,
        )

        tag = modal_inter.text_values["version"]
        if "v" not in tag.lower():
            tag = f"V{tag}"
        tag = tag.capitalize().replace(" ", "")

        desc = (
            f"Package: `{package}`\n"
            f"New Version: `{tag}`\n------------\n\n"
            f"{modal_inter.text_values['changes']}"
            f"\n\n------------\nGet it with:\n`pip install -U {package}`"
        )

        embed = disnake.Embed(
            title=f"**Package Release**",
            description=desc,
            timestamp=datetime.datetime.now(),
        )
        embed.set_footer(
            text=interaction.author.name, icon_url=interaction.author.display_avatar
        )
        await modal_inter.send("Thanks!")

        channel = await self.bot.fetch_channel(780786972859564043)
        await channel.send(release_ping_str, embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))

import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


roles = config["roles"]


class RoleSelect(discord.ui.Select):
    def __init__(self):
        options = []

        for role in roles:
            options.append(
                discord.SelectOption(
                    label=role[0],
                    value=role[1],
                    emoji=role[2]
                )
            )

        super().__init__(
            placeholder="Vyber si svoju rolu...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        chosen_role = int(self.values[0])

        role = interaction.guild.get_role(chosen_role)

        if role is None:
            await interaction.response.send_message(
                "❌ Táto rola neexistuje.",
                ephemeral=True
            )
            return


        current_roles = [
            r.id for r in interaction.user.roles
        ]

        available_roles = [
            int(r[1]) for r in roles
        ]


        if any(r in current_roles for r in available_roles):
            await interaction.response.send_message(
                "⚠️ Už máš jednu z týchto rolí.",
                ephemeral=True
            )
            return


        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            f"✅ Dostal si rolu **{role.name}**!",
            ephemeral=True
        )


class RoleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleSelect())


@bot.event
async def on_ready():

    await bot.tree.sync()

    print(
        f"Bot online ako {bot.user}"
    )


@bot.tree.command(
    name="ping",
    description="Skontroluje či bot funguje"
)
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        f"🏓 Pong! {round(bot.latency * 1000)}ms"
    )


@bot.tree.command(
    name="sendroles",
    description="Pošle menu rolí"
)
async def sendroles(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎭 Výber role",
        description=
        "Vyber si svoju rolu z menu nižšie.\n\n"
        "⚠️ Každý si môže vybrať iba jednu.",
        color=discord.Color.blurple()
    )

    embed.set_footer(
        text="Role systém"
    )

    await interaction.channel.send(
        embed=embed,
        view=RoleView()
    )

    await interaction.response.send_message(
        "✅ Menu rolí bolo odoslané.",
        ephemeral=True
    )


bot.run(TOKEN)

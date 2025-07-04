import re
import secrets
import json
import discord
from discord.ext import commands
from discord import app_commands

#config shit
with open("config.json", "r") as file:
        config = json.load(file)


#json configs to help simplify creation process.
BOT_TOKEN = config["BOT_TOKEN"]
GUILD_ID = config["GUILD_ID"]
HIDDEN_CHANNEL_ID = config["HIDDEN_CHANNEL_ID"]

# Magic Mikes Numbers
VALID_SIDES = {4, 6, 8, 10, 12, 20}
MAX_AMOUNT = 25


class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.synced = False  # Prevent multiple sync attempts

    async def on_ready(self):
        if not self.synced:
            print(f'Logged on as {self.user}!')

            try:
                guild = discord.Object(id=int(GUILD_ID))
                self.tree.copy_global_to(guild=guild)  # Optional, but useful
                synced = await self.tree.sync(guild=guild)
                print(f'Synced {len(synced)} commands to guild {guild.id}')
                for cmd in self.tree.get_commands():
                    print(f"  - {cmd.name}")
                self.synced = True
            except Exception as e:
                print(f'Error syncing commands: {e}')

intents = discord.Intents.default()
intents.message_content = True
bot = Client(command_prefix="!", intents=intents)



"""This is the place for mathmatical equations for this bot. 
        Only involve Daggerheart related die rolls.
    
"""
# Solution to roll two 1-12 integer via secrets for hope and fear.
def roll_hope_fear():
    hope_roll = secrets.randbelow(12) + 1
    fear_roll = secrets.randbelow(12) + 1
    return hope_roll, fear_roll

# Solutions for all rolls required
def roll_die(sides: int) -> int:
    return secrets.randbelow(sides) + 1



#===========================================================================================
#a /command Center.

"""


    Commands strictly for roll /commands


"""


@bot.tree.command(name="dd", description="Rolls Hope and Fear (Duality Dice)")
@app_commands.describe(hide="Be a bitch, ion care...")
async def dd_command(interaction: discord.Interaction, hide: bool = False):
    await interaction.response.defer()

# from return
    hope_roll, fear_roll = roll_hope_fear()
    total = hope_roll + fear_roll

    user_name = interaction.user.display_name
    if hope_roll > fear_roll:
        outcome_text = f"{user_name} rolled {total} with Hope."
    elif fear_roll > hope_roll:
        outcome_text = f"{user_name} rolled {total} with Fear."
    else:
        outcome_text = f"{user_name} rolled {total}. A Critical Success!"
    embed = discord.Embed(title=outcome_text,color=discord.Color.gold())
    embed.add_field(name="Hope Roll",value=str(hope_roll),inline=True)
    embed.add_field(name="Fear Roll",value=str(fear_roll),inline=True)
    if hide:
        # Try to fetch the hidden channel
        hidden_channel = bot.get_channel(HIDDEN_CHANNEL_ID)
        if hidden_channel is None:
            # If get_channel failed (invalid ID or bot lacks access)
            await interaction.followup.send(
                "❌ Could not find the hidden channel. "
                "Please check that 'hidden_channel_id' in config.json is correct, "
                "and that I have permission to view/send messages there.",
                ephemeral=True
            )
            return

        # Send the embed into the hidden channel
        try:
            await hidden_channel.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don’t have permission to send messages in the hidden channel.",
                ephemeral=True
            )
            return

        # Acknowledge ephemerally in the original channel
        await interaction.followup.send(
            "Your roll has been sent to the hidden channel.",
            ephemeral=True
        )
    else:
        # Public roll in the invoking channel, posted as an embed
        await interaction.followup.send(embed=embed)



# Command to request a die to roll, then shows who rolled, what was rolled,then: total.
@bot.tree.command(name="roll", description="Rolls any die that is requested.")
@app_commands.describe(dice="Amount of rolls and what kind of dice is rolled.", hide="Ig if u want..")
async def roll_command(interaction: discord.Interaction, dice: str, hide: bool = False):

    match = re.fullmatch(r"(\d{1,2})d(\d{1,3})", dice.lower())
    if not match:
        await interaction.response.send_message("Learn how to type ginger.")
        return


    amount = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    if sides  < 2 or sides not in VALID_SIDES:
        await interaction.response.send_message(f"Don't be sorry, be better. {VALID_SIDES} only.") # f = format
        return

    if not (1<= amount <= MAX_AMOUNT):
        await interaction.response.send_message(f"Greedy fuck, how many you need? only {MAX_AMOUNT} is allowed, the FuCk...")
        return


    await interaction.response.defer(ephemeral=hide)
    results = [roll_die(sides) for _ in range(amount)]
    total = sum(results)
    rolls_str = ', '.join(str(r) for r in results)
    user_name = interaction.user.display_name
    if amount ==1:
        description = f"TOTAL: **{total}**"
    else:
        description = f"Rolls: {rolls_str}\nTOTAL: **{total}**"
    embed = discord.Embed(
        title=f"{user_name} rolled {amount}d{sides}", 
        description=description,
        color=discord.Color.blurple()
    )
    if hide:
        # Try to fetch the hidden channel
        hidden_channel = bot.get_channel(HIDDEN_CHANNEL_ID)
        if hidden_channel is None:
            # If get_channel failed (invalid ID or bot lacks access)
            await interaction.followup.send(
                "❌ Could not find the hidden channel. "
                "Please check that 'hidden_channel_id' in config.json is correct, "
                "and that I have permission to view/send messages there.",
                ephemeral=True
            )
            return

        # Send the embed into the hidden channel
        try:
            await hidden_channel.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don’t have permission to send messages in the hidden channel.",
                ephemeral=True
            )
            return

        # Acknowledge ephemerally in the original channel
        await interaction.followup.send(
            "Your roll has been sent to the hidden channel.",
            ephemeral=True
        )
    else:
        # Public roll in the invoking channel, posted as an embed
        await interaction.followup.send(embed=embed)



bot.run(BOT_TOKEN)
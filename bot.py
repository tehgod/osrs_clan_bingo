import os
import discord
from dotenv import load_dotenv
from discord import app_commands
from google_sheets import *

load_dotenv("./config/required/.env")
token = os.getenv('DISCORD_TOKEN')
my_guild = os.getenv('DISCORD_GUILD')
my_guild_id = os.getenv('DISCORD_GUILD_ID')
admin_discord_id = os.getenv('DISCORD_ADMIN_ID')
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)



def approver_status(discord_id):
    groups = []
    if not os.path.isfile("./config/required/teams.json"):
        print("missing required file for teams information")
        return False
    with open("./config/required/teams.json") as my_file:
        team_information = json.load(my_file)
    for team in team_information:
        if discord_id in team_information[team]["approvers"]:
            return {
                "approver":True,
                "sheet_url":team_information[team]["googlesheetname"],
                "team_name":team
            }
    return {
        "approver":False,
        "sheet_url":None,
        "team_name":None
    }

print(my_guild_id)

@tree.command(name = "update-xp", description = "Updates teams xp and scores", guild=discord.Object(id=my_guild_id)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction):
    await interaction.response.send_message("Running updates now.")
    await interaction.followup.send("Finished.")

@tree.command(name = "complete-tile", guild=discord.Object(id=my_guild_id))
async def first_command(interaction, tile: str):
    requestor_info = approver_status(interaction.user.id)
    if requestor_info["approver"]==True:
        with open(f"./config/generated/{requestor_info['team_name']}/board_layout.json") as myfile:
            board_layout=json.load(myfile)
        team_sheet = google_sheets("./config/required/credentials.json", requestor_info["sheet_url"])
        team_sheet.complete_tile(board_layout,tile)
        await interaction.response.send_message(f"Completed tile {tile}")
    else:
        await interaction.response.send_message(f"Incorrect permissions. You need admin permissions for this command")

@tree.command(name = "reveal-tile", guild=discord.Object(id=my_guild_id))
async def first_command(interaction, tile: str):
    requestor_info = approver_status(interaction.user.id)
    if requestor_info["approver"]==True:
        await interaction.response.send_message(f"Revealing tile {tile}")
        with open(f"./config/generated/{requestor_info['team_name']}/board_layout.json") as myfile:
            board_layout=json.load(myfile)
        team_sheet = google_sheets("./config/required/credentials.json", requestor_info["sheet_url"])
        team_sheet.write_to_scoreboard(board_layout,tile)
        await interaction.followup.send(f"Finished")
    else:
        await interaction.response.send_message(f"Incorrect permissions. You need admin permissions for this command")

@tree.command(name = "run-setup", guild=discord.Object(id=my_guild_id))
async def first_command(interaction, tile: str):
    if interaction.user.id == admin_discord_id:
        await interaction.response.send_message(f"Revealing tile {tile}")
    else:
        await interaction.response.send_message(f"Incorrect permissions. You need admin permissions for this command")

#mark as completed
#storing starting values


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=my_guild_id))
    for guild in client.guilds:
        print(guild)
        if guild.name == my_guild:
            break
    print(f'{client.user} is now connected to {guild.name}(id: {guild.id}).')
    text_channel_list = []
    for guild in client.guilds:
        if guild.name == my_guild:
            for channel in guild.text_channels:
                text_channel_list.append(channel)

client.run(token)
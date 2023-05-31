import os
import discord
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
my_guild = os.getenv('DISCORD_GUILD')
my_guild_id = os.getenv('DISCORD_GUILD_ID')
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "update-xp", description = "Updates teams xp and scores", guild=discord.Object(id=12417128931)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction):
    await interaction.response.send_message("Ayyy still working on it.")


# @client.event
# async def on_ready():
#     await tree.sync(guild=discord.Object(id=my_guild_id))
#     for guild in client.guilds:
#         print(guild)
#         if guild.name == my_guild:
#             break
#     print(f'{client.user} is now connected to {guild.name}(id: {guild.id}).')
#     text_channel_list = []
#     for guild in client.guilds:
#         if guild.name == my_guild:
#             for channel in guild.text_channels:
#                 text_channel_list.append(channel)

# @tree.command(name = "commandname", description = "My first application Command", guild=discord.Object(id=12417128931)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
# async def first_command(interaction):
#     await interaction.response.send_message("Hello!")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=my_guild_id))
    print("Ready!")


client.run(token)
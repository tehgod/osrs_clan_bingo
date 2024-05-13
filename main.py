import json
import os, os.path
from dotenv import load_dotenv
from google_sheets import *
import discord
from discord import app_commands

load_dotenv()

def open_json(filepath:str):
    with open (filepath) as myfile:
        return json.load(myfile)
    

class Team:
    def __init__(self, db_conn, team_number) -> None:
        self.members = db_conn.load_team_members(team_number)
        self.layout = db_conn.load_board_layout(team_number)
        try:
            self.template_number = self.layout[0]["Template"]
        except:
            print("Unable to determine template number")
            self.template_number=None
        self.template = db_conn.load_template(self.template_number)
        self.creds = db_conn.load_team_credentials(team_number)[0]
        self.googleSheets = google_sheets(json.loads(self.creds["GoogleSheetAuth"]), self.creds["Name"])
    
    def load_scoreboard(self):
        self.googleSheets.create_scoreboard(self.members, self.template)
        if len(self.template) == 0:
            print(f"No active board template found for {self.creds['Name']}")
        for cell in self.template:
            if cell["Difficulty"]=="Start":
                self.googleSheets.complete_tile(self.layout, cell["Cell"])
        for cell in self.layout:
            if cell["Status"] == 1:
                self.googleSheets.write_to_scoreboard(self.layout, cell["Cell"])
                self.googleSheets.complete_tile(self.layout, cell["Cell"])
        print(f"Finished loading Scoreboard for team {self.creds['Name']}")
        


if __name__ == "__main__":
    #connect to database
    my_db = database_connection()

    #get list of teams
    team_ids = []
    team_members = my_db.load_team_members()
    for user in team_members:
        if user.Team not in team_ids:
            team_ids.append(user.Team)
    

    #build team objects
    teams = []
    for team_number in team_ids:
        teams.append(Team(my_db, team_number))
    
    #load each team's scoreboard
    for team in teams:
        team.load_scoreboard()

    #prepare for discord initiation
    token = os.getenv('DISCORD_TOKEN')
    my_guild = os.getenv('DISCORD_GUILD')
    my_guild_id = os.getenv('DISCORD_GUILD_ID')
    admin_discord_id = os.getenv('DISCORD_ADMIN_ID')
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    #building commands for bot
    
    #perform initial team layout generation
    @tree.command(name = "reveal-tile", guild=discord.Object(id=my_guild_id))
    async def first_command(interaction, tile: str):
        print([interaction.user.id])
        for team in teams:
            team_channel_id = int(team.creds["DiscordChannelId"])
            for user in team.members:
                if int(user.DiscordUserId)==interaction.user.id:
                    if user.Approver==1:
                        if team_channel_id==interaction.channel_id:
                            await interaction.response.send_message(f"Revealing tile {tile}")
                            team.googleSheets.write_to_scoreboard(team.layout, tile)
                            my_db.update_task_progress(team.creds["Id"], tile, 1)
                            new_tiles = team.googleSheets.complete_tile(team.layout, tile)
                            for tile in team.layout:
                                if tile["Cell"] in new_tiles:
                                    ruleset = my_db.get_rules(tile["TaskId"])
                                    if len(ruleset)>0:
                                        finished_string = f"**The rules for {tile['Cell']} are as follows:**"
                                        i = 0
                                        for rule in ruleset:
                                            i+=1
                                            finished_string += f"\n{i}: {rule['Rule']}"
                                            await interaction.followup.send(finished_string)
                        else:
                            await interaction.response.send_message(f"Incorrect Channel. Please post this in your proper team channel.")
                    else:
                        await interaction.response.send_message(f"Incorrect permissions. You do not have approver status.")
                    break


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
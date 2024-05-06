import json
import os, os.path
from dotenv import load_dotenv
from google_sheets import *

load_dotenv()

def open_json(filepath:str):
    with open (filepath) as myfile:
        return json.load(myfile)
    

class Team:
    def __init__(self, db_conn, team_number) -> None:
        self.members = db_conn.load_team_members(team_number)
        self.layout = db_conn.load_board_layout(team_number)
        self.template = db_conn.load_template(team_number)
        self.creds = db_conn.load_team_credentials(team_number)[0]
        self.googleSheets = google_sheets(json.loads(self.creds["GoogleSheetAuth"]), self.creds["Name"])
    
    def load_scoreboard(self):
        self.googleSheets.create_scoreboard(self.members, self.template)
        for cell in self.template:
            if cell["Difficulty"]=="Start":
                self.googleSheets.complete_tile(self.layout, cell["Cell"])
        for cell in self.layout:
            if cell["Status"] == 1:
                self.googleSheets.write_to_scoreboard(self.layout, cell["Cell"])
                self.googleSheets.complete_tile(self.layout, cell["Cell"])
        print(f"Finished loading Scoreboard for team {self.creds['Name']}")
        


if __name__ == "__main__":
    my_db = database_connection()

    team_ids = []
    team_members = my_db.load_team_members(1)
    for user in team_members:
        if user["Team"] not in team_ids:
            team_ids.append(user["Team"])
            
    teams = []
    for team_number in team_ids:
        teams.append(Team(my_db, team_number))
        
    for team in teams:
        team.load_scoreboard()




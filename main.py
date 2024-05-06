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
        self.creds = db_conn.load_team_credentials(team_number)
        self.googleSheets = google_sheets(json.loads(self.creds[0]["GoogleSheetAuth"]), self.creds[0]["Name"])
        
def initial_setup():
    
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
        team.googleSheets.create_scoreboard(team.members, team.template)
        for cell in team.template:
            if cell["Difficulty"]=="Start":
                team.googleSheets.complete_tile(team.layout, cell["Cell"])
        for cell in team.layout:
            if cell["Status"] == 1:
                team.googleSheets.write_to_scoreboard(team.layout, cell["Cell"])
                team.googleSheets.complete_tile(team.layout, cell["Cell"])

        
    # team_1_sheets.complete_tile(board_layout, "i10")
    # team_1_sheets.complete_tile(board_layout)












    # if not (os.path.isfile("./config/required/.env") and
    # os.path.isfile("./config/required/tasks.json") and
    # os.path.isfile("./config/required/board_template.json") and
    # os.path.isfile("./config/required/credentials.json") and
    # os.path.isfile("./config/required/categories.json")):
    #     print("Required config files missing.")
    #     exit()
    # else:
    #     load_dotenv("./config/required/.env")
    #     categories = open_json("./config/required/categories.json")
    #     google_credentials = open_json("./config/required/credentials.json")
    #     categories_filename = "./config/required/categories.json"
    #     tasks_file = open_json("./config/required/tasks.json")
    #     board_template = open_json("./config/required/board_template.json")
    #     teams_info = open_json("./config/required/teams.json")
    #     unique_team_boards = True
    #     if unique_team_boards:
    #         for team in teams_info:
    #             if not (os.path.isfile(f"./config/generated/{team}/board_layout.json")):
    #                 generate_board_layout(board_template, tasks_file, f"./config/generated/{team}/")
    #             else:
    #                 print('dab')
    #     else:
    #         generate_board_layout(board_template,tasks_file, [f"/config/generated/{team}/" for team in teams_info])


            #check if board(s) need initiated
            #if boards need initiated, check if sheets need created with initial setup


        #board_layout = open_json("./config/generated/board_layout.json")
            

if __name__ == "__main__":
    initial_setup()




import gspread
import json
import random

def open_json(filepath:str):
    with open (filepath) as myfile:
        return json.load(myfile)
    
def generate_board_layout(board_layout: dict, task_list: dict):
    generated_layout = {}
    used_tasks = []
    for task_difficulty in board_layout:
        for tile in board_layout[task_difficulty]:
            task = False
            while task == False:
                random_task = random.choice(task_list[task_difficulty])
                if random_task not in used_tasks:
                    used_tasks.append(random_task)
                    task = random_task
            generated_layout[tile]=task
    with open("new_board_layout.json", "w") as myfile:
        json.dump(generated_layout, myfile)

class google_sheets:
    def __init__(self, google_credentials_filepath:str, spreadsheet_name:str):
        self.gspread_client = gspread.service_account(filename=google_credentials_filepath)
        self.worksheet = self.gspread_client.open(spreadsheet_name)
        self.current_sheet = self.worksheet.get_worksheet(0)

    def change_to_sheet(self, sheet_name:str):
        self.current_sheet = self.worksheet(sheet_name)

    def create_scoreboard_sheet(self, board_layout:dict):
        try:
            self.change_to_sheet("Scoreboard2")
        except TypeError:
            self.current_sheet = self.worksheet.add_worksheet(title="Scoreboard2", rows=100, cols=20)
        #need to include formatting to make it look pretty going forwards.
        





if __name__ == "__main__":
    board_layout = open_json("./config/board_layout.json")
    tasks = open_json("./config/tasks.json")
    generate_board_layout(board_layout, tasks)
    team_1_sheets = google_sheets("./credentials.json", "Team 1")
    team_1_sheets.create_scoreboard_sheet()
import gspread
import json
import random
from gspread.cell import Cell
import string
from time import sleep

def open_json(filepath:str):
    with open (filepath) as myfile:
        return json.load(myfile)
    
def generate_board_layout(board_layout:dict, task_list: dict, board_layout_filename:str="board_layout.json"):
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
    with open(board_layout_filename, "w") as myfile:
        json.dump(generated_layout, myfile)

def col2num(col):
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num

class google_sheets:
    def __init__(self, google_credentials_filepath:str, spreadsheet_name:str):
        self.gspread_client = gspread.service_account(filename=google_credentials_filepath)
        self.worksheet = self.gspread_client.open(spreadsheet_name)
        self.current_sheet = self.worksheet.get_worksheet(0)

    def change_to_sheet(self, sheet_name:str):
        self.current_sheet = self.worksheet.worksheet(sheet_name)

    def create_scoreboard(self):
        if self.current_sheet.title != "Scoreboard":
            try:
                self.change_to_sheet("Scoreboard")
            except gspread.exceptions.WorksheetNotFound:
                self.current_sheet = self.worksheet.add_worksheet(title="Scoreboard", rows=100, cols=20)

    def format_scoreboard(self, board_template:dict, board_layout:dict):
        cell_formats = []
        cell_formats.append(
            #bolden member names
            {
                "range": "a1:a2",
                "format": {
                    "textFormat": {
                        "bold": True
                    },
                },
            }
        )
        for cell in board_layout:
            if board_layout[cell]=="START":
                cell_formats.append(
                    {
                        "range": cell,
                        "format": {
                            "backgroundColor": {
                                "red": 0.0,
                                "green": 1.0,
                                "blue": 0.0
                            },
                            "borders": {
                                "top": {
                                    "style": "SOLID",
                                },
                                "bottom": {
                                    "style": "SOLID",
                                },
                                "left": {
                                    "style": "SOLID",
                                },
                                "right": {
                                    "style": "SOLID",
                                }
                            },
                            "textFormat": {
                                "bold": True,
                                "fontSize": 20
                            },
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    }
                )
            else:
                cell_formats.append(
                    {
                        "range": cell,
                        "format": {
                            "borders": {
                                "top": {
                                    "style": "SOLID",
                                },
                                "bottom": {
                                    "style": "SOLID",
                                },
                                "left": {
                                    "style": "SOLID",
                                },
                                "right": {
                                    "style": "SOLID",
                                }
                            },
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "wrapStrategy": "WRAP"
                        }
                    }
                )
        self.current_sheet.batch_format(cell_formats)
        pass

    def format_width_and_height(self):
        body = {
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 100
                        },
                        "properties": {
                            "pixelSize": 120
                        },
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "ROWS",
                            "startIndex": 0,
                            "endIndex": 100
                        },
                        "properties": {
                            "pixelSize": 90
                        },
                        "fields": "pixelSize"
                    }
                }
            ]
        }
        self.worksheet.batch_update(body)

    def write_to_scoreboard(self, board_layout:dict, individual_tile:str=None):
        if self.current_sheet.title != "Scoreboard":
            try:
                self.change_to_sheet("Scoreboard")
            except gspread.exceptions.WorksheetNotFound:
                print("No scoreboard located to write value to.")
                return False
        cells = []
        tiles_to_update = []
        if individual_tile==None:
            tiles_to_update = [tile for tile in board_layout]
        elif individual_tile in [tile for tile in board_layout]:
            tiles_to_update.append(individual_tile)
        else:
            print("Inavlid tile selected")
            return False
        for tile in tiles_to_update:
            row = []
            column = []
            for letter in tile:
                if letter.isnumeric():
                    row.append(letter)
                else:
                    column.append(letter)
            row = int("".join(row))
            column = col2num("".join(column))
            cells.append(Cell(row, column, board_layout[tile]))
        self.current_sheet.update_cells(cells)
        print("Successfully updated tiles.")
        return True

    def create_xp_tables(self, team_list):
        for user in team_list:
            pass

if __name__ == "__main__":
    
    board_template = open_json("./config/board_template.json")
    tasks = open_json("./config/tasks.json")
    generate_board_layout(board_template, tasks)
    board_layout = open_json("./board_layout.json")
    team_1_sheets = google_sheets("./credentials.json", "Team 1")
    team_1_sheets.change_to_sheet("Scoreboard")
    # team_1_sheets.create_scoreboard()
    # #team_1_sheets.write_to_scoreboard(board_layout, "f7")
    # # team_1_sheets.write_to_scoreboard(board_layout, "f10")
    # team_1_sheets.format_scoreboard(board_template,board_layout)
    # team_1_sheets.write_to_scoreboard(board_layout)
    team_1_sheets.format_scoreboard_2()
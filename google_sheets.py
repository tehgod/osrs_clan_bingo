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

    def change_to_sheet(self, sheet_name:str, create_if_missing=False):
        if self.current_sheet.title != sheet_name:
            try:
                self.current_sheet = self.worksheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                if create_if_missing == True:
                    self.current_sheet = self.worksheet.add_worksheet(title=sheet_name, rows=100, cols=20)

    def format_scoreboard_step_2(self, board_template:dict):
        cell_formats = []
        #format all scoreboard cells and background colors
        for category in board_template:
            base_cell_format ={
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
            match category:
                case "start":
                    base_cell_format["backgroundColor"]={
                        "red": 0.0,
                        "green": 1.0,
                        "blue": 0.0
                    }
                    base_cell_format["textFormat"]={
                        "bold": True,
                        "fontSize": 20
                    }
                case "beginner":
                    base_cell_format["backgroundColor"]={
                        "red": 204/255,
                        "green": 204/255,
                        "blue": 204/255
                    }
                case "easy":
                    base_cell_format["backgroundColor"]={
                        "red": 217/255,
                        "green": 234/255,
                        "blue": 211/255
                    }
                case "medium":
                    base_cell_format["backgroundColor"]={
                        "red": 207/255,
                        "green": 226/255,
                        "blue": 243/255
                    }
                case "hard":
                    base_cell_format["backgroundColor"]={
                        "red": 234/255,
                        "green": 209/255,
                        "blue": 220/255
                    }
                case "elite":
                    base_cell_format["backgroundColor"]={
                        "red": 252/255,
                        "green": 229/255,
                        "blue": 205/255
                    }
                case "master":
                    base_cell_format["backgroundColor"]={
                        "red": 230/255,
                        "green": 184/255,
                        "blue": 175/255
                    }
            for cell in board_template[category]:
                cell_formats.append(
                    {
                        "range": cell,
                        "format": base_cell_format
                    }
                )
        #Bolden usernames and mvp points headers
        cell_formats.append(
            {
                "range": "B6:C6",
                "format": {
                    "textFormat":{
                        "bold": True,
                        "fontSize": 10
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                    "wrapStrategy": "WRAP"
                }
            }
        )
        #bolden tasks and points values headers
        cell_formats.append(
            {
                "range": "E2:E4",
                "format": {
                    "textFormat":{
                        "bold": True,
                        "fontSize": 10
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                    "wrapStrategy": "WRAP"
                }
            }
        )
        #bolden team name
        cell_formats.append(
            {
                "range": "B2:C4",
                "format": {
                    "textFormat":{
                        "bold": True,
                        "fontSize": 28
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                    "wrapStrategy": "WRAP"
                }
            }
        )
        #Push all changes
        self.current_sheet.batch_format(cell_formats)
        pass

    def format_scoreboard_step_1(self):
        body = {
            "requests": [
                #update scoreboard columns width
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 4,
                            "endIndex": 100
                        },
                        "properties": {
                            "pixelSize": 120
                        },
                        "fields": "pixelSize"
                    }
                },
                #update scoreboard rows height
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "ROWS",
                            "startIndex": 5,
                            "endIndex": 100
                        },
                        "properties": {
                            "pixelSize": 90
                        },
                        "fields": "pixelSize"
                    }
                },
                #update vertical black lines
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 1
                        },
                        "properties": {
                            "pixelSize": 9
                        },
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 3,
                            "endIndex": 4
                        },
                        "properties": {
                            "pixelSize": 9
                        },
                        "fields": "pixelSize"
                    }
                },
                #update horizontal black lines
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "ROWS",
                            "startIndex": 0,
                            "endIndex": 1
                        },
                        "properties": {
                            "pixelSize": 9
                        },
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.current_sheet.id,
                            "dimension": "ROWS",
                            "startIndex": 4,
                            "endIndex": 5
                        },
                        "properties": {
                            "pixelSize": 9
                        },
                        "fields": "pixelSize"
                    }
                },
                #merge and center top left team name
                {
                    "mergeCells": {
                        "mergeType": "MERGE_ALL",
                        "range": {  # In this sample script, all cells of "A1:C3" of "Sheet1" are merged.
                            "sheetId": self.current_sheet.id,
                            "startRowIndex": 1,
                            "endRowIndex": 4,
                            "startColumnIndex": 1,
                            "endColumnIndex": 3
                        }
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

    def format_memberlist(self):
        pass
    def create_xp_tables(self, team_list):
        for user in team_list:
            pass

if __name__ == "__main__":
    
    board_template = open_json("./config/board_template.json")
    tasks = open_json("./config/tasks.json")
    generate_board_layout(board_template, tasks)
    board_layout = open_json("./board_layout.json")
    team_1_sheets = google_sheets("./credentials.json", "Team 1")
    team_1_sheets.change_to_sheet("Scoreboard", True)
    #member_list = open_json("./config/all_members.json")
    # team_1_sheets.create_scoreboard()
    #team_1_sheets.write_to_scoreboard(board_layout, "f7")
    # # team_1_sheets.write_to_scoreboard(board_layout, "f10")
    # team_1_sheets.format_scoreboard(board_template,board_layout)
    # team_1_sheets.write_to_scoreboard(board_layout)
    team_1_sheets.format_scoreboard_step_1()
    team_1_sheets.format_scoreboard_step_2(board_template)
    #print(team_1_sheets.current_sheet.acell("d7"))
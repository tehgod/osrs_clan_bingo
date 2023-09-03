
import requests
from datetime import date, timedelta, datetime
import json
from statistics import mean
import os, os.path
from dotenv import load_dotenv
from time import sleep
import gspread
from gspread.cell import Cell
from google_sheets import *

def open_json(filepath:str):
    with open (filepath) as myfile:
        return json.load(myfile)
    
def generate_board_layout(board_layout:dict, task_list: dict, output_filepath):
    generated_layout = {}
    used_tasks = []
    for task_difficulty in board_layout:
        for tile in board_layout[task_difficulty]:
            task = False
            while task == False:
                random_task = random.choice(task_list[task_difficulty])
                if random_task not in used_tasks:
                    if task_difficulty!="start":
                        used_tasks.append(random_task)
                    task = random_task
            generated_layout[tile]=task
    if type(output_filepath)==str:
        os.makedirs(output_filepath, exist_ok=True)
        with open(f"{output_filepath}board_layout.json", "w+") as myfile:
            json.dump(generated_layout, myfile)
            print('board generated')
    if type(output_filepath)==list:
        for filepath in output_filepath:
            with open(f"{filepath}board_layout.json", "w+") as myfile:
                json.dump(generated_layout, myfile)
                print('board generated')


class clan:
    def __init__(self, members_list):
        self.clan_list = []
        for member in members_list:
            new_member = clan_member(member)
            self.clan_list.append(new_member)
        pass

    def clan_stats_to_file(self, filename, filetype):
        if filetype == "json":
            dataset = {}
            for member in self.clan_list:
                current_member = member.convert_to_json()
                dataset[current_member["username"]] = current_member["data_set"]
            with open(f"./config/daily_stats/{filename}.{filetype}", "w") as my_file:
                json.dump(dataset, my_file)
                my_file.close()
        elif filetype == "csv":
            dataset = []
            for member in self.clan_list:
                dataset.append(member.convert_to_csv())
            with open(f"./config/daily_stats/{filename}.{filetype}", "w") as my_file:
                my_file.write("\n".join(dataset))
                my_file.close()
        pass

class clan_member:
    def __init__(self, username):
        original_username = username
        while (current_stats:= requests.get(f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={username}")).status_code != 200:
            match current_stats.status_code:
                case 404:
                    how_to_proceed = input(f"Invalid username: {username}, how would you like to proceed?\n1:Update Username\n2:Remove member\n3:Exit\n").replace(" ", "_")
                    match how_to_proceed:
                        case "1":
                            username = input("Please enter updated username.\n")
                        case "2":
                            username = False
                            break
                        case _:
                            username = False
                            break
                case 503:
                    print("Server receiving too many requests, trying again.")
                case _:
                    print(f"Receiveed unknown status code when retrieving highscores for {username}; status code {current_stats.status_code}")
                    return False
        if original_username != username: #now need to update json with updated username
            with open(members_list_filename) as my_file:
                members_list = json.load(my_file)
            if username != False:
                previous_usernames = members_list[original_username]
                previous_usernames.append(original_username)
                members_list[username] = previous_usernames
            del members_list[original_username]
            with open(members_list_filename, "w") as my_file:
                json.dump(members_list, my_file)
                my_file.close()
        if username != False: 
            self.username = username
            self.parse_hiscores_request(current_stats.text)

    def parse_hiscores_request(self, request_text):
        current_stats = request_text.splitlines()
        with open(categories_filename) as my_file:
            skills_list = json.load(my_file)["All"]
        item_number = 0
        for item in skills_list:
            skill_name = item
            try:
                skill_stats = current_stats[item_number].split(',')
            except IndexError:
                print(f"error pulling data for {self.username}")
                break
            if len(skill_stats) == 2:
                skill_rank = int(skill_stats[0])
                skill_score = int(skill_stats[1])
                setattr(self, skill_name.replace(" ", "_").lower(), {"rank" : skill_rank, "score": skill_score})
            else:
                skill_rank = int(skill_stats[0])
                skill_level = int(skill_stats[1])
                skill_xp = int(skill_stats[2])
                setattr(self, skill_name.replace(" ", "_").lower(), {"rank" : skill_rank, "level": skill_level, "xp": skill_xp})
            item_number+=1
        print(f"Successfully pulled stats for username: {self.username}")
        pass

    def convert_to_csv(self):
        data_set = []
        for attr, value in self.__dict__.items():
            if attr != "username":
                data_set.append(f"{self.username},{attr}, {value}")
        return "\n".join(data_set)

    def convert_to_json(self):
        data_set = {}
        for attr, value in self.__dict__.items():
            if attr != "username":
                data_set[attr] = value
        return {"username": self.username, "data_set": data_set}

    def print_skills(self):
        for attr, value in self.__dict__.items():
            print(f"{attr}:{value}")
        pass

class clan_json:
    def __init__(self, json_filepath):
        with open(json_filepath) as my_file:
            self.full_dataset = json.load(my_file)
        with open(categories_filename) as my_file:
            self.skills_list = json.load(my_file)
        self.members_list = []
        for username in self.full_dataset:
            self.members_list.append(username)
        pass

    def get_average(self, skill=None, remove_noattempts=True):
        if skill in self.skills_list["Skills"]:
            group_ranks = []
            group_xps = []
            group_levels = []
            for username in self.full_dataset:
                rank = int(self.full_dataset[username][skill]['rank'])
                if rank == -1:
                    rank = 0
                group_ranks.append(rank)
                group_xps.append(int(self.full_dataset[username][skill]['xp']))
                group_levels.append(int(self.full_dataset[username][skill]['level']))
            group_ranks = round(mean(group_ranks))
            group_xps = round(mean(group_xps))
            group_levels = round(mean(group_levels))
            return {'rank': group_ranks, 'level': group_levels, 'xp': group_xps}
        elif (skill in self.skills_list["Bosses"]) or (skill in self.skills_list["Minigames"]) or (skill in self.skills_list["Clue Scrolls"]):
            group_ranks = []
            group_scores = []
            for username in self.full_dataset:
                rank = int(self.full_dataset[username][skill]['rank'])
                if rank == -1:
                    rank = 0
                if rank != 0:
                    group_ranks.append(rank)
                score = int(self.full_dataset[username][skill]['score'])
                if score == -1:
                    score = 0
                if (remove_noattempts == False) or (score != 0):
                    group_scores.append(score)
            group_ranks = round(mean(group_ranks))
            group_scores = round(mean(group_scores))
            return {'rank':group_ranks,'score':group_scores}
        elif skill == None:
            full_dataset = {}
            for skill_dataset in self.skills_list:
                match skill_dataset:
                    case "Skills":
                        for skill in self.skills_list[skill_dataset]:
                            group_ranks = []
                            group_xps = []
                            group_levels = []
                            for username in self.full_dataset:
                                rank = int(self.full_dataset[username][skill]['rank'])
                                if rank == -1:
                                    rank = 0
                                group_ranks.append(rank)
                                group_xps.append(int(self.full_dataset[username][skill]['xp']))
                                group_levels.append(int(self.full_dataset[username][skill]['level']))
                            group_ranks = round(mean(group_ranks))
                            group_xps = round(mean(group_xps))
                            group_levels = round(mean(group_levels))
                            full_dataset[skill] = {"rank": group_ranks, "level": group_levels, "xp": group_xps}
                    case "Bosses" | "Minigames" | "Clue Scrolls":
                        for skill in self.skills_list[skill_dataset]:
                            group_ranks = []
                            group_scores = []
                            for username in self.full_dataset:
                                rank = int(self.full_dataset[username][skill]['rank'])
                                if rank == -1:
                                    rank = 0
                                if rank != 0:
                                    group_ranks.append(rank)
                                score = int(self.full_dataset[username][skill]['score'])
                                if score == -1:
                                    score = 0
                                if (remove_noattempts == False) or (score != 0):
                                    group_scores.append(score)
                            if len(group_ranks)>0:
                                group_ranks = round(mean(group_ranks))
                            else:
                                group_ranks = 0
                            if len(group_scores)>0:
                                group_scores = round(mean(group_scores))
                            else:
                                group_scores = 0
                            full_dataset[skill] = {"rank":group_ranks,"score":group_scores}
                    case _:
                        pass
            return full_dataset
        else:
            print(f"{skill} is not a valid score to check.")
        pass

    def top_members(self, skill_group, selection=None, amount=False):
        match skill_group:
            case "Skills":
                if amount==False:
                    amount = len(self.members_list)*24
                if selection == None:
                    skill_list = self.skills_list[skill_group]
                elif type(selection)==str:
                    skill_list = [selection]
                else:
                    skill_list = selection
                results = []
                for item in skill_list:
                    scores = []
                    for username in self.members_list:
                        user_score = {
                            "username":username,
                            "skill":item,
                            "rank":self.full_dataset[username][item]["rank"],
                            "level":self.full_dataset[username][item]["level"],
                            "xp":self.full_dataset[username][item]["xp"],
                        }
                        if user_score["xp"]==-1:
                            user_score["xp"]=0
                        scores.append(user_score)
                    scores = sorted(scores, key=lambda d: d['xp'], reverse=True)[:amount]
                    for item in scores:
                        results.append(item)
                if len(results) == amount:
                    return results
                else:
                    results = sorted(results, key=lambda d: d['xp'], reverse=True)[:amount]
                    return results
            case "Bosses" | "Minigames" | "Clue Scrolls":
                if amount==False:
                    amount = len(self.members_list)
                if selection == None:
                    skill_list = self.skills_list[skill_group]
                elif type(selection)==str:
                    skill_list = [selection]
                else:
                    skill_list = selection
                results = []
                for item in skill_list:
                    scores = []
                    for username in self.members_list:
                        user_score = {
                            "username":username,
                            "skill":item,
                            "score":self.full_dataset[username][item]["score"],
                            "rank":self.full_dataset[username][item]["rank"]
                            }
                        if user_score["score"]==-1:
                            user_score["score"]=0
                        scores.append(user_score)
                    scores = sorted(scores, key=lambda d: d['score'], reverse=True)[:amount]
                    #scores = scores[:amount]
                    for item in scores:
                        results.append(item)
                if len(results) == amount:
                    return results
                else:
                    results = sorted(results, key=lambda d: d['score'], reverse=True)[:amount]
                    return results
            case _:
                pass

def generate_daily_datasheet(clan_members_list_filepath, filetype="json"):
    with open(clan_members_list_filepath) as my_json:
        clan_members = json.load(my_json)
    my_clan = clan(clan_members)
    todays_date = date.today().strftime("%b-%d-%Y")
    if filetype in ["json","csv"]:
        my_clan.clan_stats_to_file(todays_date, filetype)
    return True

def generate_sheets_dump(datasheet=f'./config/daily_stats/{date.today().strftime("%b-%d-%Y")}.json'):
    with open(datasheet) as my_file:
        data_dump = json.load(my_file)
    with open(categories_filename) as my_file:
        tracked_skills = json.load(my_file)["Tracked_Skills"]
    with open(categories_filename) as my_file:
        tracked_bosses = json.load(my_file)["Tracked_Bosses"]
    username_list = [username for username in data_dump]
    csv_contents = []
    csv_contents.append(",".join(["Username"]+username_list))
    for skill in tracked_skills:
        xp_totals=[]
        for user in username_list:
            xp_totals.append(str(data_dump[user][skill]['xp']))
        csv_contents.append(",".join([skill]+xp_totals))
    for boss in tracked_bosses:
        kc_totals=[]
        for user in username_list:
            kc_totals.append(str(data_dump[user][boss]['score']).replace("-1","0"))
        csv_contents.append(",".join([boss]+kc_totals))
    with open("output.csv", "w") as my_file:
        my_file.write("\n".join(csv_contents))
        my_file.close()
    print("Finished writing to CSV file.")
    return

def update_google_sheet(spreadsheet_name, sheet_name, start_row, start_column, google_credentials, datasheet=f'./config/daily_stats/{date.today().strftime("%b-%d-%Y")}.json'):
    with open(datasheet) as my_file:
        data_dump = json.load(my_file)
    with open(categories_filename) as my_file:
        tracked_skills = json.load(my_file)["Tracked_Skills"]
    with open(categories_filename) as my_file:
        tracked_bosses = json.load(my_file)["Tracked_Bosses"]
    cells = []
    username_list = [username for username in data_dump]
    gspread_client = gspread.service_account(filename=google_credentials)
    worksheet= gspread_client.open(spreadsheet_name)
    sheet = worksheet.worksheet(sheet_name)
    current_row = start_row
    current_column = start_column
    cells.append(Cell(row=current_row, col=current_column, value='Username'))
    #sheet.update_cell(current_row, current_column, "Username")
    for username in username_list:
        current_column+=1
        cells.append(Cell(row=current_row, col=current_column, value=username))
        #sheet.update_cell(current_row, current_column, username)
    current_column = start_column
    current_row +=1
    for skill in tracked_skills:
        cells.append(Cell(row=current_row, col=current_column, value=skill))
        #sheet.update_cell(current_row, current_column, skill)
        for user in username_list:
            current_column+=1
            cells.append(Cell(row=current_row, col=current_column, value=data_dump[user][skill]['xp']))
            #sheet.update_cell(current_row, current_column, data_dump[user][skill]['xp'])
        current_column=start_column
        current_row+=1
    for boss in tracked_bosses:
        cells.append(Cell(row=current_row, col=current_column, value=boss))
        #sheet.update_cell(current_row, current_column, boss)
        for user in username_list:
            current_column+=1
            value=int(str(data_dump[user][boss]['score']).replace("-1","0"))
            cells.append(Cell(row=current_row, col=current_column, value=value))
            #sheet.update_cell(current_row, current_column, data_dump[user][boss]['score'].replace("-1","0"))
        current_column=start_column
        current_row+=1
    sheet.update_cells(cells)
    print('Done')

# teams = [
#     {"team_json_location":team1,"xp_grild_location":(37,2)},
#     {"team_json_location":team2,"xp_grild_location":(37,11)},
#     {"team_json_location":team3,"xp_grild_location":(37,19)}
# ]

def main_loop():
    if not (os.path.isfile("./config/required/.env") and
    os.path.isfile("./config/required/tasks.json") and
    os.path.isfile("./config/required/board_template.json") and
    os.path.isfile("./config/required/credentials.json") and
    os.path.isfile("./config/required/categories.json")):
        print("Required config files missing.")
        exit()
    else:
        load_dotenv("./config/required/.env")
        categories = open_json("./config/required/categories.json")
        google_credentials = open_json("./config/required/credentials.json")
        categories_filename = "./config/required/categories.json"
        tasks_file = open_json("./config/required/tasks.json")
        board_template = open_json("./config/required/board_template.json")
        teams_info = open_json("./config/required/teams.json")
        unique_team_boards = True
        if unique_team_boards:
            for team in teams_info:
                if not (os.path.isfile(f"./config/generated/{team}/board_layout.json")):
                    generate_board_layout(board_template, tasks_file, f"./config/generated/{team}/")
                else:
                    print('dab')
        else:
            generate_board_layout(board_template,tasks_file, [f"/config/generated/{team}/" for team in teams_info])
        
            #check if board(s) need initiated
            #if boards need initiated, check if sheets need created with initial setup


        #board_layout = open_json("./config/generated/board_layout.json")
if __name__ == "__main__":
    main_loop()




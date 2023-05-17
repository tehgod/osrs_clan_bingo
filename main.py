
import requests
from datetime import date, timedelta, datetime
import json
from statistics import mean
import os, os.path
from dotenv import load_dotenv
from time import sleep

load_dotenv("./config/.env")
time_to_run = {"hour":4, "minute":0}
clan_memberlist_1 = "./config/members_list.json"
categories_filename = "./config/categories.json"

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

var = f"my s{time_to_run}tirng"

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


generate_daily_datasheet(clan_memberlist_1)
generate_sheets_dump()


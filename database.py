import os, os.path
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class database_connection:
    def __init__(self):
        pass

    def load_engine (self, 
                    db_username = os.getenv('db_username'),
                    db_password = os.getenv('db_password'),
                    db_hostname = os.getenv('db_hostname'),
                    schema_name="Runescape"):
        self.engine = create_engine(f"mysql+pymysql://{db_username}:{db_password}@{db_hostname}/{schema_name}")
        return True

    def df_to_db(self, df, table_name):
        self.load_engine()
        df.to_sql(table_name, con = self.engine, if_exists = 'append',index = False)
        self.engine.dispose()
        return True

    @staticmethod
    def df_to_dict(df):
        return df.to_dict(orient='records')
    
    def load_template(self, template_number):
        self.load_engine()
        result = pd.read_sql(f"""SELECT bbt.Cell, lbd.Name as Difficulty  from BingoBoardTemplate bbt inner join LookupBingoDifficulty lbd on bbt.Difficulty =lbd.Id WHERE Template ={template_number}""", self.engine)
        self.engine.dispose()
        return result
    
    def load_team_members(self, team_number:int = None):
        base_query = """SELECT * from BingoTeams bt"""
        if team_number != None:
            base_query += f" WHERE Team = {team_number}"
        self.load_engine()
        result = pd.read_sql(base_query, self.engine)
        self.engine.dispose()
        return result 
    
    def load_tasks(self):
        self.load_engine()
        result = pd.read_sql(f"""SELECT bt.Id, lbd.Name AS Difficulty, bt.Task FROM BingoTasks bt INNER JOIN LookupBingoDifficulty lbd ON bt.Difficulty = lbd.Id""", self.engine)
        self.engine.dispose()
        return result
    
    def generate_board_layout(self, template_number, team_number=0):
        try:
            self.load_engine()
            with self.engine.connect() as con:
                con.execute(text(f"""Call `Bingo.GenerateLayout`({template_number}, {team_number})"""))
                con.commit()
            return True
        except:
            return False

# my_db = database_connection()
# print(database_connection.df_to_dict(my_db.load_template(1)))
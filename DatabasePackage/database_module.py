import time
import mysql.connector
from _cred import Credentials

mydb = mysql.connector.connect(
  host      = Credentials["host"],
  user      = Credentials["user"],
  password  = Credentials["password"],
  database  = Credentials["database"]
)

myCursor = mydb.cursor()


class DbModule:
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host      = Credentials["host"],
            user      = Credentials["user"],
            password  = Credentials["password"],
            database  = Credentials["database"]
        )

        self.cursor = self.mydb.cursor()

    def LogStartJob(self):
        sql = """
            INSERT INTO GlobalLogging_TH (
                ApplicationName, 
                ActivityDate,
                ActivityType,
                Description
            ) VALUES ('TokpedEngine', %s, 'Interval Data Collection', 'JOB START')"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(sql, val)
        self.mydb.commit()

    def LogEndJob(self):
        sql = """
            INSERT INTO GlobalLogging_TH (
                ApplicationName, 
                ActivityDate,
                ActivityType,
                Description
            ) VALUES ('TokpedEngine', %s, 'Interval Data Collection', 'JOB END')"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(sql, val)
        self.mydb.commit()

    def Logging(self, msg:str):
        sql = """
            INSERT INTO GlobalLogging_TH (
                ApplicationName, 
                ActivityDate,
                ActivityType,
                Description
            ) VALUES ('TokpedEngine', %s, 'Interval Data Collection', %s)"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'), msg)

        self.cursor.execute(sql, val)
        self.mydb.commit()
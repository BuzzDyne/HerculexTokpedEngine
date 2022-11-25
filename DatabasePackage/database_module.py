import time
import mysql.connector
from _cred import Credentials
from DataModel.db_model import Order, OrderItem

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

    def insertOrder(self, data:Order):
        sql = """
            INSERT INTO TPOrder_TM (
                order_id, buyer_id, invoice_ref_num, order_status,
                ts_created, ts_acc_by, ts_ship_by,
                insert_ts, last_updated_ts
            ) VALUES (
                %s, %s, %s, %s,
                FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),
                %s, %s
            )
        """
        
        param = (
            data.order_id, data.buyer_id, data.invoice_ref_num, data.order_status,
            data.ts_created, data.ts_acc_by, data.ts_ship_by,
            time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')
        )

        self.cursor.execute(sql, param)
        self.mydb.commit()

    def insertOrderItem(self, data:OrderItem):
        sql = """
            INSERT INTO TPOrderItem_TM (
                order_id, product_id, product_name, quantity, product_price
            ) VALUES (%s, %s, %s, %s, %s)
        """
        
        param = (data.order_id, data.product_id, data.product_name, data.quantity, data.product_price)

        self.cursor.execute(sql, param)
        self.mydb.commit()
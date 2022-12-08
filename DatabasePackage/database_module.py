import time
import mysql.connector
from typing import Tuple, Dict, List

from _cred import Credentials
from DataModel.db_model import Order, OrderItem

class DbModule:
    def __init__(self):
        self.cnx = mysql.connector.connect(
            host      = Credentials["host"],
            user      = Credentials["user"],
            password  = Credentials["password"],
            database  = Credentials["database"]
        )

        self.cursor = self.cnx.cursor()
    #region Logging
    def TokpedLogActivity(self, activityType, desc):
        sql = """
            INSERT INTO GlobalLogging_TH (
                ApplicationName, 
                ActivityDate,
                ActivityType,
                Description
            ) VALUES ('TokpedEngine', %s, %s, %s)"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'), activityType, desc)

        self.cursor.execute(sql, val)
        self.cnx.commit()

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
        self.cnx.commit()

    def LogEndJob(self):
        sql = """
            INSERT INTO GlobalLogging_TH (
                ApplicationName, 
                ActivityDate,
                ActivityType,
                Description
            ) VALUES ('TokpedEngine', FROM_UNIXTIME(%s), 'Interval Data Collection', 'JOB END')"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(sql, val)
        self.cnx.commit()

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
        self.cnx.commit()
    #endregion

    def insertOrder(self, data:Order):
        sql = """
            INSERT INTO TPOrder_TM (
                order_id, buyer_id, invoice_ref_num, order_status,
                ts_created, ts_acc_by, ts_ship_by,
                insert_ts
            ) VALUES (
                %s, %s, %s, %s,
                FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),
                %s
            )
        """
        
        param = (
            data.order_id, data.buyer_id, data.invoice_ref_num, data.order_status,
            data.ts_created, data.ts_acc_by, data.ts_ship_by,
            time.strftime('%Y-%m-%d %H:%M:%S')
        )

        self.cursor.execute(sql, param)
        self.cnx.commit()

    def insertOrderItem(self, data:OrderItem):
        sql = """
            INSERT INTO TPOrderItem_TM (
                order_id, product_id, product_name, quantity, product_price
            ) VALUES (%s, %s, %s, %s, %s)
        """
        
        param = (data.order_id, data.product_id, data.product_name, data.quantity, data.product_price)

        self.cursor.execute(sql, param)
        self.cnx.commit()

    def getAllOrderID(self) -> List[str]:
        """Returns list of OrderIDs already in DB"""
        sql = """
            SELECT DISTINCT order_id 
            FROM TPOrder_TM
        """

        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        listOfOrderIDs = []

        for x in res:
            listOfOrderIDs.append(x[0])

        return listOfOrderIDs

    def getTokpedProcessSyncDate(self) -> Dict:
        sql = """
            SELECT 
                UNIX_TIMESTAMP(initial_sync), 
                UNIX_TIMESTAMP(last_synced)
            FROM HCXProcessSyncStatus_TM
            WHERE platform_name = "TOKOPEDIA"
            LIMIT 1
        """

        self.cursor.execute(sql)
        res = self.cursor.fetchall()[0]

        return {
            "initial_sync"      : res[0],
            "last_synced"       : res[1]
        }
    
    def setTokpedLastSynced(self, dt):
        sql = """
            UPDATE HCXProcessSyncStatus_TM
            SET
                last_synced = %s
            WHERE platform_name = "TOKOPEDIA"
        """

        val = (dt.strftime('%Y-%m-%d %H:%M:%S'),) if dt is not None else (dt,)

        self.cursor.execute(sql, val)
        self.cnx.commit()

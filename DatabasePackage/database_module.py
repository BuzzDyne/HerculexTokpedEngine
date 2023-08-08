import time
import mysql.connector
from typing import Tuple, Dict, List

from _cred import Credentials
from DatabasePackage.constants import ORDER_STATUS_MESSAGES
from DataModel.db_model import Order, OrderItem

from datetime import datetime as dt
from datetime import timezone as tz

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
            INSERT INTO globallogging_th (
                application_name, 
                activity_date,
                activity_type,
                description
            ) VALUES ('TokpedEngine', %s, %s, %s)"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'), activityType, desc)

        self.cursor.execute(sql, val)
        self.cnx.commit()

    def LogStartJob(self):
        sql = """
            INSERT INTO globallogging_th (
                application_name, 
                activity_date,
                activity_type,
                description
            ) VALUES ('TokpedEngine', %s, 'Interval Data Collection', 'JOB START')"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(sql, val)
        self.cnx.commit()

    def LogEndJob(self):
        sql = """
            INSERT INTO globallogging_th (
                application_name, 
                activity_date,
                activity_type,
                description
            ) VALUES ('TokpedEngine', FROM_UNIXTIME(%s), 'Interval Data Collection', 'JOB END')"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(sql, val)
        self.cnx.commit()

    def Logging(self, msg:str):
        sql = """
            INSERT INTO globallogging_th (
                application_name, 
                activity_date,
                activity_type,
                description
            ) VALUES ('TokpedEngine', %s, 'Interval Data Collection', %s)"""
        
        val = (time.strftime('%Y-%m-%d %H:%M:%S'), msg)

        self.cursor.execute(sql, val)
        self.cnx.commit()
    #endregion

    def insertNewOrder(self, data:Order):
        order_id = self._insertOrder(data)
        self._insertOrderTracking(order_id, "Inserted data from Tokped to system")
  
    def _insertOrder(self, data:Order):
        sql = """
            INSERT INTO order_tm (
                ecommerce_code, ecom_order_id, buyer_id, invoice_ref, ecom_order_status,
                pltf_deadline_dt, feeding_dt
            ) VALUES (
                %s, %s, %s, %s, %s,
                FROM_UNIXTIME(%s),%s
            )
        """
        
        param = (
            data.ecommerce_code, data.ecom_order_id, data.buyer_id, data.invoice_ref, data.ecom_order_status,
            data.pltf_deadline_dt, time.strftime('%Y-%m-%d %H:%M:%S')
        )

        self.cursor.execute(sql, param)
        self.cnx.commit()

        return self.cursor.lastrowid

    def insertOrderItem(self, data:OrderItem):
        sql = """
            INSERT INTO orderitem_tr (
                ecom_order_id, ecom_product_id, product_name, quantity, product_price
            ) VALUES (%s, %s, %s, %s, %s)
        """
        
        param = (data.order_id, data.product_id, data.product_name, data.quantity, data.product_price)

        self.cursor.execute(sql, param)
        self.cnx.commit()

    def getAllOrderID(self) -> List[str]:
        """Returns list of OrderIDs already in DB"""
        sql = """
            SELECT DISTINCT order_id 
            FROM order_tm
        """

        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        listOfOrderIDs = []

        for x in res:
            listOfOrderIDs.append(x[0])

        return listOfOrderIDs

    def getOrderDetailsByIDs(self, listOfIDs, ecommerce_code) -> List[Tuple[str]]:
        """Returns list of Tuples(OrderID, Status) already in DB"""
        format_string = (','.join(['%s'] * len(listOfIDs)), ecommerce_code)

        sql = """
            SELECT ecom_order_id, ecom_order_status
            FROM order_tm
            WHERE ecom_order_id IN (%s) AND ecommerce_code = "%s"
        """ % format_string

        self.cursor.execute(sql, tuple(listOfIDs))
        res = self.cursor.fetchall()

        return res

    def getOrderDetailsByNeedToUpdated(self, listOfStatuses) -> List[Tuple[str]]:
        """Returns list of Tuples(OrderID, Status) that needs to be updated in DB"""
        format_string = ','.join(['%s'] * len(listOfStatuses))

        sql = """
            SELECT ecom_order_id, ecom_order_status
            FROM order_tm
            WHERE ecom_order_status NOT IN (%s)
        """ % format_string

        self.cursor.execute(sql, tuple(listOfStatuses))
        res = self.cursor.fetchall()

        return res

    def getTokpedProcessSyncDate(self) -> Dict:
        sql = """
            SELECT 
                initial_sync, 
                last_synced
            FROM hcxprocessSyncStatus_TM
            WHERE platform_name = "TOKOPEDIA"
            LIMIT 1
        """

        self.cursor.execute(sql)
        res = self.cursor.fetchall()[0]

        return {
            "initial_sync"      : res[0],
            "last_synced"       : res[1]
        }
    
    def setTokpedLastSynced(self, input_unixTS):
        sql = """
            UPDATE hcxprocessSyncStatus_TM
            SET
                last_synced = %s
            WHERE platform_name = "TOKOPEDIA"
        """
        
        val = (input_unixTS,)

        self.cursor.execute(sql, val)
        self.cnx.commit()

    def setBatchUpdateOrdersStatus(self, listOfDicts_UpdatedOrderData):
        ts = dt.now(tz.utc)
        FINISHED_ORDER_STATUSES = ['500','501','520','530','540','550','600','601','690','700']

        for order_data in listOfDicts_UpdatedOrderData:
            if order_data["order_status"] in FINISHED_ORDER_STATUSES :
                sql = """
                    UPDATE order_tm
                    SET
                        ecom_order_status = %s,
                        last_updated_ts = %s,
                        shipped_dt = %s
                    WHERE ecom_order_id = %s
                """
                shipped_date = ts.strftime('%Y-%m-%d %H:%M:%S')

                if order_data["shipping_date"]: #'2023-08-08T09:13:14.681548Z'
                    shipped_date = dt.strptime(order_data["shipping_date"], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%Y-%m-%d %H:%M:%S')

                val = (order_data["order_status"], ts.strftime('%Y-%m-%d %H:%M:%S'), shipped_date, order_data["order_id"])
            else:
                sql = """
                    UPDATE order_tm
                    SET
                        ecom_order_status = %s,
                        last_updated_ts = %s
                    WHERE ecom_order_id = %s
                """
                val = (order_data["order_status"], ts.strftime('%Y-%m-%d %H:%M:%S'), order_data["order_id"])

            self.cursor.execute(sql, val)
                                
            # Insert order tracking entry
            order_db_id = self._getOrderTmIdByEcomOrderId(order_data["order_id"])
            status_message = ORDER_STATUS_MESSAGES.get(order_data['order_status'], 'Unknown')
            activity_msg = f"Order #{order_db_id} status updated to {order_data['order_status']} ({status_message})"
            self._insertOrderTracking(order_db_id, activity_msg)

        self.cnx.commit()

    def _insertOrderTracking(self, order_id, activity_msg):
        sql = """
            INSERT INTO ordertracking_th (
                order_id, activity_msg, user_id
            ) VALUES (
                %s, %s, %s
            )
        """
        
        param = (
            order_id, activity_msg, "1"
        )

        self.cursor.execute(sql, param)
        self.cnx.commit()

    def _getOrderTmIdByEcomOrderId(self, ecom_order_id):
        sql = """
            SELECT id
            FROM order_tm
            WHERE ecom_order_id = %s
            ORDER BY id ASC
            LIMIT 1
        """

        val = (ecom_order_id,)

        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()

        if result:
            order_tm_id = result[0]
            return order_tm_id
        else:
            return None
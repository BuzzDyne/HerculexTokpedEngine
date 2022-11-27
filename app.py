import time
from typing import List

from datetime import datetime as dt
from datetime import timezone as tz

from DatabasePackage.database_module import DbModule
from TokpedPackage.tokped_module import TokpedModule
from DataModel.db_model import createOrder, Order

class App:
    def __init__(self):
        self.db = DbModule()
        self.tp = TokpedModule()

    def syncTokpedNewOrderData(self):
        # Logging
        self.db.LogActivity("Sync Orders", "Process BEGIN")

        # Get start sync date
        sync_info = self.db.getProcessSyncDate("TOKOPEDIA")
        start_period    = sync_info["initial_sync_ts"] if sync_info["last_synced"] is None else sync_info["last_synced"]
        end_period      = int(dt.now(tz.utc).timestamp())

        if start_period > end_period:
            self.db.LogActivity("Sync Orders", "initial/last sync time is bigger than current time")
        else:
            # Get existing OrderID
            listOfIDs = self.db.getAllOrderID()
            THREE_DAYS_IN_SEC = (60 * 60 * 24 * 3)

            # Iterate API to get OrderIDs based on period
            resultList = []

            start_query = start_period
            end_query   = end_period

            while start_query <= end_period:
                if end_query - start_query > THREE_DAYS_IN_SEC:
                    end_query = start_query + THREE_DAYS_IN_SEC

                res = self._getOrderObjectBetweenTS(start_query, end_query)
                resultList.append(res)

                start_query = None
                #TODO



            # Insert New Orders to DB

        # Logging
        self.db.LogActivity("Sync Orders", "Process END")

        return

    def _getOrderObjectBetweenTS(self, from_date, to_date) -> List[Order]:
        jsonOfOrders = self.tp.getOrderBetweenTS(from_date, to_date)
        
        listOfOrders: List[Order] = []

        for o in jsonOfOrders:
            listOfOrders.append(createOrder(o))

        return listOfOrders

    def _testBlindPushOrderToDB(self):
        # Get Orders from Tokped
        now_unix = int(dt.now(tz.utc).timestamp())
        start_unix = now_unix - (60 * 60 * 24 * 3)

        jsonOfOrders = self.tp.getOrderBetweenTS(start_unix, now_unix)

        listOfOrders: List[Order] = []

        for o in jsonOfOrders:
            listOfOrders.append(createOrder(o))

        # Push to DB
        for o in listOfOrders:
            for item in o.list_of_items:
                self.db.insertOrderItem(item)
            self.db.insertOrder(o)

    def _testCheckMaxQuery(self, iter):
        # Get Orders from Tokped
        now_unix    = int(time.time())  - (86400 * iter)
        start_unix  = now_unix          - (86400 * 3)

        jsonOfOrders = self.tp.getOrderBetweenTS(start_unix, now_unix)

        listOfOrders: List[Order] = []


        for o in jsonOfOrders or []:
            listOfOrders.append(createOrder(o))
        
        return len(listOfOrders)
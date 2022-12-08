import time
from typing import List, Tuple

from datetime import datetime as dt
from datetime import timezone as tz

from DatabasePackage.database_module import DbModule
from TokpedPackage.tokped_module import TokpedModule
from DataModel.db_model import createOrder, Order

class App:
    def __init__(self):
        self.db = DbModule()
        self.tp = TokpedModule()

    def _cleanListOfOrder(self, listOfOrders: List[Order]) -> Tuple[List[Order]]:
        # Remove Duplicate OrderID
        uniqueList = {o.order_id: o for o in listOfOrders}.values()

        # Get existing OrderID
        listOfExistingIDs = self.db.getAllOrderID()

        # Remove Existing OrderID
        cleanList   = [x for x in uniqueList if x.order_id not in listOfExistingIDs]
        dupeList    = [x for x in uniqueList if x.order_id in listOfExistingIDs]
        return (cleanList, dupeList)

    def _getOrderObjectBetweenTS(self, from_date, to_date) -> List[Order]:
        jsonOfOrders = self.tp.getOrderBetweenTS(from_date, to_date)
        
        if jsonOfOrders is None:
            return None

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
    
    def syncTokpedNewOrderData(self):
        currTime = dt.now(tz.utc)

        # Logging
        self.db.TokpedLogActivity("Sync Orders", "Process BEGIN")

        # Get start sync date
        sync_info = self.db.getTokpedProcessSyncDate()
        start_period    = sync_info["initial_sync"] if sync_info["last_synced"] is None else sync_info["last_synced"]
        end_period      = int(currTime.timestamp())
        self.db.TokpedLogActivity("Sync Orders", f"StartPeriod : {start_period} | EndPeriod : {end_period}")


        if start_period > end_period:
            self.db.TokpedLogActivity("Sync Orders", "initial/last sync time is bigger than current time")
            self.db.TokpedLogActivity("Sync Orders", "Process END")
            return

        # Iterate API to get OrderIDs based on period
        resultList = []
        THREE_DAYS_IN_SEC = (60 * 60 * 24 * 3)

        start_time  = start_period
        end_time    = 0

        while end_time < end_period:
            temp = start_time + THREE_DAYS_IN_SEC
            end_time = temp if temp < end_period else end_period
            
            res = self._getOrderObjectBetweenTS(start_time, end_time)
            if res:
                resultList += res

            start_time += THREE_DAYS_IN_SEC

        countData = len(resultList) if resultList else 0
        self.db.TokpedLogActivity("Sync Orders", f"Got {countData} Orders from TokpedAPI")

        if(resultList):
            # Clean ListOfOrder (Remove Duplicate and Separate Existing IDs)
            cleanList, dupeList = self._cleanListOfOrder(resultList)
            self.db.TokpedLogActivity("Sync Orders", f"Pushing {len(cleanList)} Orders to DB (Cleaning Process Done)")

            # Insert ListOfOrder to DB
            for o in cleanList:
                for item in o.list_of_items:
                    self.db.insertOrderItem(item)
                self.db.insertOrder(o)
            
            

        # Update LastSynced
        self.db.setTokpedLastSynced(currTime)

        # Logging
        self.db.TokpedLogActivity("Sync Orders", "Process END")

        return
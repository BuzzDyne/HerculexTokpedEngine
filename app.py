import time
from typing import List

from DatabasePackage.database_module import DbModule
from TokpedPackage.tokped_module import TokpedModule
from DataModel.db_model import createOrder, Order

class App:
    def __init__(self):
        self.db = DbModule()
        self.tp = TokpedModule()

    def syncTokpedNewOrderData(self):
        # Get start sync date
        sync_info = self.db.getProcessSyncDate("TOKOPEDIA")

        start_period = sync_info["initial_sync_ts"] if sync_info["last_synced"] is None else sync_info["last_synced"]
 
        return

    def _testBlindPushOrderToDB(self):
        # Get Orders from Tokped
        now_unix = int(time.time())
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
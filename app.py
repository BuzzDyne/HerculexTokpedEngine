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
    
    #region Private Functions
    def _findOrderStatusFromListByID(self, list_of_orders, order_id):
        for x in list_of_orders:
            if x.order_id == order_id:
                return x.order_status

    def _cleanListOfOrder(self, list_of_new_orders: List[Order]) -> Tuple[List[Order]]:
        '''returns tuple of two elements, new_list (list) and update_list (dictionary)'''
        # Remove Duplicate OrderID
        unique_list_of_new_orders     = {o.order_id: o for o in list_of_new_orders}.values()
        listOfOrderIDs  = [o.order_id for o in unique_list_of_new_orders]

        # Get existing OrderDetail
        list_of_existing_order_detail   = self.db.getOrderDetailsByIDs(listOfOrderIDs)
        list_of_existing_order_id       = [o[0] for o in list_of_existing_order_detail]
        dict_of_order_existing          = dict(list_of_existing_order_detail)


        # Remove Existing OrderID
        new_list    = [x for x in unique_list_of_new_orders if x.order_id not in list_of_existing_order_id]
        dupe_list   = [x for x in unique_list_of_new_orders if x.order_id in list_of_existing_order_id]

        # Find Order with Updated Status from Existing Orders
        update_list = {}
        for id, status in dict_of_order_existing.items():
            newStatus = self._findOrderStatusFromListByID(dupe_list, id)

            if status != newStatus:
                update_list[id] = newStatus

        return (new_list, update_list)

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
    #endregion
    
    def syncTokpedExsOrderData(self):
        listStatusNotNeedToUpdate = ['0','3','5','6','10','15','520','550','700']

        # Logging
        self.db.TokpedLogActivity("Sync Existing Orders", "Process BEGIN")

        # Ambil list order_id yang harus diupdate
        listOldOrderDetails = self.db.getOrderDetailsByNeedToUpdated(listStatusNotNeedToUpdate)
        self.db.TokpedLogActivity("Sync Existing Orders", f"Found {len(listOldOrderDetails)} Orders from DB to be updated.")

        # Hit API Tokped
        listNewOrderDetails = self.tp.getBatchOrderDetailByIDs([x[0] for x in listOldOrderDetails])
        self.db.TokpedLogActivity("Sync Existing Orders", f"Got {len(listNewOrderDetails)} Orders from Tokped.")

        # Clean listNewOrderDetails TODO
        dictOldOrderDetails = {}

        for x in listOldOrderDetails:
            dictOldOrderDetails[x[0]] = x[1]

        dictNewOrderDetails = {}

        for x in listNewOrderDetails:
            if dictOldOrderDetails[str(x[0])] != str(x[1]):
                dictNewOrderDetails[str(x[0])] = str(x[1])

        # Push updates
        self.db.setBatchUpdateOrdersStatus(dictNewOrderDetails)
        self.db.TokpedLogActivity("Sync Existing Orders", f"Updated {len(dictNewOrderDetails)} Orders.")

        self.db.TokpedLogActivity("Sync Existing Orders", "Process END")

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
            cleanList, update_dict = self._cleanListOfOrder(resultList)
            self.db.TokpedLogActivity("Sync Orders", f"Pushing {len(cleanList)} Orders to DB (Cleaning Process Done)")

            # Insert ListOfOrder to DB
            for o in cleanList:
                for item in o.list_of_items:
                    self.db.insertOrderItem(item)
                self.db.insertOrder(o)
            
            # Update status
            self.db.TokpedLogActivity("Sync Orders", f"Updating statuses of {len(update_dict)} Orders to DB")
            self.db.setBatchUpdateOrdersStatus(update_dict)
            

        # Update LastSynced
        self.db.setTokpedLastSynced(currTime)

        # Logging
        self.db.TokpedLogActivity("Sync Orders", "Process END")

        return
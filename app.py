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

    # region Private Functions
    def _findOrderStatusFromListByID(self, list_of_orders: List[Order], order_id):
        for x in list_of_orders:
            if str(x.ecom_order_id) == order_id:
                return str(x.ecom_order_status)

    def _cleanListOfOrder(self, list_of_new_orders: List[Order]) -> Tuple[List[Order]]:
        """returns tuple of two elements, new_list (list) and update_list (dictionary)"""
        # Remove Duplicate OrderID
        unique_list_of_new_orders = {
            o.ecom_order_id: o for o in list_of_new_orders
        }.values()
        listOfOrderIDs = [o.ecom_order_id for o in unique_list_of_new_orders]

        # Get existing OrderDetail
        list_of_existing_order_detail = self.db.getOrderDetailsByIDs(listOfOrderIDs)
        list_of_existing_order_id = [o[0] for o in list_of_existing_order_detail]
        dict_of_order_existing = dict(list_of_existing_order_detail)

        # Remove Existing OrderID
        new_list = [
            x
            for x in unique_list_of_new_orders
            if str(x.ecom_order_id) not in list_of_existing_order_id
        ]
        dupe_list = [
            x
            for x in unique_list_of_new_orders
            if str(x.ecom_order_id) in list_of_existing_order_id
        ]

        # Find Order with Updated Status from Existing Orders
        update_list = {}
        for id, status in dict_of_order_existing.items():
            newStatus = self._findOrderStatusFromListByID(dupe_list, id)

            if status != newStatus and newStatus != None:
                update_list[id] = newStatus

        return (new_list, update_list)

    def _getOrderObjectBetweenTS(self, from_date, to_date) -> List[Order]:
        jsonOfOrders = self.tp.getOrderBetweenTS(from_date, to_date)

        if jsonOfOrders is None:
            return None

        listOfOrders: List[Order] = []

        for o in jsonOfOrders:
            listOfOrders.append(createOrder(o, "T"))

        return listOfOrders

    # endregion

    def syncTokpedExsOrderData(self):
        PROCESS_NAME = "Sync Existing Orders"

        # Logging
        self.db.TokpedLogActivity(PROCESS_NAME, "Process BEGIN")

        # Get list of order IDs that need to be updated
        listOldOrderDetails = self.db.getOrderDetailsByNeedToUpdated()
        self.db.TokpedLogActivity(
            PROCESS_NAME,
            f"Found {len(listOldOrderDetails)} Orders from DB to be updated.",
        )

        # Hit API Tokped
        order_ids = [x[0] for x in listOldOrderDetails]
        listNewOrderDetails = self.tp.getBatchOrderDetailByIDs(order_ids)
        self.db.TokpedLogActivity(
            PROCESS_NAME, f"Got {len(listNewOrderDetails)} Orders from Tokped."
        )

        dictOldOrderDetails = {x[0]: x[1] for x in listOldOrderDetails}
        listOfDicts_NewOrderDetails = []

        for order_data in listNewOrderDetails:
            order_id = order_data["order_id"]
            if order_id in dictOldOrderDetails:
                old_status = dictOldOrderDetails[order_id]
                new_status = order_data["order_status"]
                if old_status != new_status:
                    listOfDicts_NewOrderDetails.append(
                        {
                            "order_id": order_id,
                            "order_status": new_status,
                            "shipping_date": order_data["shipping_date"],
                        }
                    )

        # Push updates
        self.db.setBatchUpdateOrdersStatus(listOfDicts_NewOrderDetails)
        self.db.TokpedLogActivity(
            PROCESS_NAME, f"Updated {len(listOfDicts_NewOrderDetails)} Orders."
        )

        self.db.TokpedLogActivity(PROCESS_NAME, "Process END")

    def syncTokpedNewOrderData(self):
        SEVEN_HOURS_IN_SEC = 7 * 60 * 60
        currUnixTS = int(dt.now(tz.utc).timestamp()) + SEVEN_HOURS_IN_SEC
        PROCESS_NAME = "Sync New Orders"

        # Logging
        self.db.TokpedLogActivity(PROCESS_NAME, "Process BEGIN")

        # Get start sync date
        sync_info = self.db.getTokpedProcessSyncDate()
        start_period = (
            sync_info["initial_sync"]
            if sync_info["last_synced"] is None
            else sync_info["last_synced"]
        )
        end_period = currUnixTS
        self.db.TokpedLogActivity(
            PROCESS_NAME,
            f"StartPeriod : {start_period} | EndPeriod : {end_period} (GMT+7 Time)",
        )

        if start_period > end_period:
            self.db.TokpedLogActivity(
                PROCESS_NAME, "initial/last sync time is bigger than current time"
            )
            self.db.TokpedLogActivity(PROCESS_NAME, "Process END")
            return

        # Iterate API to get OrderIDs based on period
        resultList = []
        THREE_DAYS_IN_SEC = 60 * 60 * 24 * 3

        start_time = start_period
        end_time = 0

        while start_time < end_period:
            temp = start_time + THREE_DAYS_IN_SEC
            end_time = temp if temp < end_period else end_period

            res = self._getOrderObjectBetweenTS(start_time, end_time)
            if res:
                resultList += res

            start_time += THREE_DAYS_IN_SEC

        countData = len(resultList) if resultList else 0
        self.db.TokpedLogActivity(
            PROCESS_NAME, f"Got {countData} Orders from TokpedAPI"
        )

        if resultList:
            # Clean ListOfOrder (Remove Duplicate and Separate Existing IDs)
            cleanList, update_dict = self._cleanListOfOrder(resultList)
            self.db.TokpedLogActivity(
                PROCESS_NAME,
                f"Pushing {len(cleanList)} Orders to DB (Cleaning Process Done)",
            )

            # Insert ListOfOrder to DB
            for o in cleanList:
                for item in o.list_of_items:
                    self.db.insertOrderItem(item)  # TODO Pickup From here
                self.db.insertNewOrder(o)

            # Update status
            self.db.TokpedLogActivity(
                PROCESS_NAME, f"Updating statuses of {len(update_dict)} Orders to DB"
            )
            self.db.setBatchUpdateOrdersStatus(update_dict)

        # Update LastSynced
        self.db.setTokpedLastSynced(currUnixTS)

        # Logging
        self.db.TokpedLogActivity(PROCESS_NAME, "Process END")

        return


def create():
    app = App()
    app.syncTokpedNewOrderData()


def update():
    app = App()
    app.syncTokpedExsOrderData()

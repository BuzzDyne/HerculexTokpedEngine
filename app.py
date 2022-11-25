import time
from typing import List

from DatabasePackage.database_module import DbModule
from TokpedPackage.tokped_module import TokpedModule
from DataModel.db_model import createOrder, Order

class App:
    def __init__(self):
        self.db = DbModule()
        self.tp = TokpedModule()

    def _testBlindPushOrderToDB(self):
        # Get Orders from Tokped
        jsonOfOrders = self.tp._testFnGetOrders(int(time.time()) - (3600 * 24), int(time.time()))

        listOfOrders: List[Order] = []

        for o in jsonOfOrders:
            listOfOrders.append(createOrder(o))

        # Push to DB
        for o in listOfOrders:
            for item in o.list_of_items:
                self.db.insertOrderItem(item)
            self.db.insertOrder(o)

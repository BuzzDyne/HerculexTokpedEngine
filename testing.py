# from DatabasePackage.database_module import DbModule

# myDB = DbModule()

# listOfIDs = ['1402294529', '700']

# dictOfO = {
#     '1402294529': '700'
# }

# myDB.setBatchUpdateOrdersStatus(dictOfO)

#################################################################################

# import time
# from TokpedPackage.tokped_module import TokpedModule

# myTokped = TokpedModule()

# myTokped._getOrderDetailByID(1402294529)

# start_ts    = int(time.time()) - (3600 * 3)
# end_ts      = int(time.time())

# myTokped.getOrderBetweenTS(start_ts, end_ts)

#################################################################################

from app import App

a = App()
a.syncTokpedExsOrderData()
a.syncTokpedNewOrderData()

# print("Finsihed")

from DatabasePackage.database_module import DbModule

# myDB = DbModule()

# myDB.setTokpedLastSynced(None)

#################################################################################

# import time
# from TokpedPackage.tokped_module import TokpedModule

# myTokped = TokpedModule()

# start_ts    = int(time.time()) - (3600 * 3)
# end_ts      = int(time.time())

# myTokped.getOrderBetweenTS(start_ts, end_ts)

#################################################################################

from app import App

a = App()
a.syncTokpedNewOrderData()

print("Finsihed")
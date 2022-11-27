# from DatabasePackage.database_module import DbModule

# myDB = DbModule()

# myDB.Logging("Start Job")
# myDB.Logging("End Job")

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
# a._testBlindPushOrderToDB()
# a._testCheckMaxQuery(59)

# l = []

# for x in range(1334,2000):
#     count = a._testCheckMaxQuery(x)
#     l.append(count)
#     print(f'{x} = {count}')

# print(f'Max Count = {max(l)}')

x = a.db.getProcessSyncDate("TOKOPEDIA")
#####################################

print()
import sys
from datetime import datetime

# # argv[0] is name of program parameters start from index 1
# timestamp = float(sys.argv[1])
# dt = datetime.fromtimestamp(timestamp) #conversion to datetime

# print(f"recieved time : {dt}")


from datetime import datetime
from local_agent import get_open_apps
from db.app_logger import log_app

apps = get_open_apps()
timestamp = datetime.now()

for app in apps:
    log_app(app, timestamp)

print("Apps logged:", len(apps))

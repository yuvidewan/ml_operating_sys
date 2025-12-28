import sys
import json
from db.app_logger import log_app
import unicodedata
import time

# # argv[0] is name of program parameters start from index 1
raw = sys.stdin.read()
data = json.loads(raw)
timestamp = time.time()
processes = data["processes"]

cleaned_processes = []
for p in processes:
    p = unicodedata.normalize("NFKC", p).strip()
    if p:
        cleaned_processes.append(p)

# print(cleaned_processes)   
for p in cleaned_processes:
    log_app(p,timestamp)


import time
import subprocess

# # datetime uses local pc time so coyld lead to issues
# # time is pc independant; datetime conversion on server side
# timestamp = str(time.time())

# result = subprocess.run(
#     ["python","decision_engine.py",timestamp],
#     capture_output=True,
#     text=True
# )

# print(result.stdout)

import psutil

def get_open_apps():
    apps = set()

    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name:
            apps.add(name)

    return list(apps)

if __name__ == "__main__":
    data = get_open_apps()
    print(data)

import time
import psutil
import platform
import pygetwindow as gw
from db.app_logger import log_app   

POLL_INTERVAL = 1.0

def get_running_processes():
        return set([w.title for w in gw.getAllWindows() if w.title and w.title.strip()])


def main():
    try:
        prev = get_running_processes()

        while True:
            time.sleep(POLL_INTERVAL)
            curr = get_running_processes()

            opened = curr - prev
            closed = prev - curr

            ts = time.time()

            for app in opened:
                log_app(app, "OPEN", ts)

            for app in closed:
                log_app(app, "CLOSE", ts)

            prev = curr
            print("data logged")
    except Exception as e:
         print(e)
         
if __name__ == "__main__":
    main()

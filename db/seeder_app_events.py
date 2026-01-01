import random
import time
from db_engine import get_connection

APPS = [
    "chrome",
    "vscode",
    "terminal",
    "spotify",
    "explorer",
    "whatsapp"
]

TRANSITIONS = {
    "chrome": ["vscode", "spotify", "whatsapp"],
    "vscode": ["terminal", "chrome", "explorer"],
    "terminal": ["vscode", "chrome"],
    "spotify": ["chrome"],
    "explorer": ["vscode"],
    "whatsapp": ["vscode", "chrome"]
}

def seed(days=14, sessions_per_day=15):
    conn = get_connection()
    cursor = conn.cursor()

    now = time.time()
    base_time = now - days * 24 * 3600

    for d in range(days):
        current_time = base_time + d * 24 * 3600 + random.randint(8, 10) * 3600
        current_app = random.choice(APPS)

        for _ in range(sessions_per_day):
            open_ts = current_time
            duration = random.randint(120, 900)  # 2–15 min
            close_ts = open_ts + duration

            cursor.execute("""
                INSERT INTO app_events (app_name, event_type, ts)
                VALUES (%s, 'open', %s)
            """, (current_app, open_ts))

            cursor.execute("""
                INSERT INTO app_events (app_name, event_type, ts)
                VALUES (%s, 'close', %s)
            """, (current_app, close_ts))

            # gap logic
            gap_type = random.choices(
                ["normal", "idle", "session"],
                weights=[70, 20, 10]
            )[0]

            if gap_type == "normal":
                gap = random.randint(5, 30)
            elif gap_type == "idle":
                gap = random.randint(90, 600)          # > IDLE_THRESHOLD
            else:
                gap = random.randint(4*3600, 8*3600)   # > SESSION_THRESHOLD

            current_time = close_ts + gap
            current_app = random.choice(TRANSITIONS.get(current_app, APPS))

    conn.commit()
    cursor.close()
    conn.close()
    print("app_events seeding complete")


if __name__ == "__main__":
    seed()

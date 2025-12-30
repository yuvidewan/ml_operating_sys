from db.db_engine import get_connection

# canonical_name : substrings that may appear in real app_name
APP_MAP = {
    "chrome": ["chrome", "google chrome"],
    "vscode": ["vscode", "visual studio code"],
    "terminal": ["terminal", "cmd", "powershell"],
    "spotify": ["spotify"],
    "explorer": ["explorer", "file explorer"],
    "whatsapp": ["whatsapp"]
}

def normalise(name: str):
    name = name.lower()
    for canonical, patterns in APP_MAP.items():
        for p in patterns:
            if p in name:
                return canonical
    return None


def clean_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE app_sessions")

    cursor.execute("""
        SELECT app_name, event_type, ts
        FROM app_events
        ORDER BY ts
    """)
    events = cursor.fetchall()

    last_app = None
    last_ts = None

    for app_name, event_type, ts in events:
        if event_type.lower() != "open":
            continue

        app = normalise(app_name)
        if not app:
            continue

        if last_app and app != last_app:
            duration = ts - last_ts
            if duration > 0:
                cursor.execute(
                    """
                    INSERT INTO app_sessions
                    (app_name, opened_at, closed_at, duration)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (last_app, last_ts, ts, duration)
                )

        last_app = app
        last_ts = ts

    # flush last session
    if last_app and last_ts:
        cursor.execute(
            """
            INSERT INTO app_sessions
            (app_name, opened_at, closed_at, duration)
            VALUES (%s, %s, %s, %s)
            """,
            (last_app, last_ts, last_ts + 1, 1)
        )

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    clean_data()

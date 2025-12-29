from db.db_engine import get_connection

ALLOW_LIST = {
    "google",
    "visual studio code",
    "whatsapp"
}

def normalise(name):
    name = name.lower()
    for j in ALLOW_LIST:
        if j in name:
            return j
    return None

def clean_data():
    conn = get_connection()
    cursor = conn.cursor()

    # rebuild clean sessions every run
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
        # we ONLY care about focus events
        if event_type.lower() != "open":
            continue

        normalised_name = normalise(app_name)
        if not normalised_name:
            continue

        # if focus switched from one app to another
        if last_app and normalised_name != last_app:
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

        # update current focus
        last_app = normalised_name
        last_ts = ts

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    clean_data()

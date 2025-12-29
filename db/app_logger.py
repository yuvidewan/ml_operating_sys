from db.db_engine import get_connection

def log_app(app_name, event, timestamp):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO app_events (app_name, event_type, ts)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (app_name, event, timestamp))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)

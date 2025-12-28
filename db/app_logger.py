from db.db_engine import get_connection

def log_app(app_name, timestamp):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO app_logs (app_name, opened_at)
            VALUES (%s, %s)
        """
        cursor.execute(query, (app_name, timestamp))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)

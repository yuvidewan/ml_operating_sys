import mysql.connector

def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="os_server_db"
        )
    except Exception as e:
        print(e)

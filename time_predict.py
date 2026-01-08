from db.db_engine import get_connection
from collections import defaultdict

# 0-6 -> Late night
# 6-10 -> Morning
# 10-13 -> Late morning
# 13-17 -> Afternoon
# 17-21 -> Evening
# 21-24 -> Night

HOUR_BUCKET = [
    "late_night",  # 0
    "late_night",  # 1
    "late_night",  # 2
    "late_night",  # 3
    "late_night",  # 4
    "late_night",  # 5
    "morning",     # 6
    "morning",     # 7
    "morning",     # 8
    "morning",     # 9
    "late_morning",# 10
    "late_morning",# 11
    "late_morning",# 12
    "afternoon",   # 13
    "afternoon",   # 14
    "afternoon",   # 15
    "afternoon",   # 16
    "evening",     # 17
    "evening",     # 18
    "evening",     # 19
    "evening",     # 20
    "night",       # 21
    "night",       # 22
    "night"        # 23
]


BUCKET = defaultdict(list)

def create_bucket():
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT app_name,opened_dt from app_sessions"
    cur.execute(query)
    rows = cur.fetchall()

    for i in rows:
        hour = i[1].hour

        time_of_day = HOUR_BUCKET[hour]
        BUCKET[time_of_day].append(i[0])
        
        # for i in BUCKET:
        #     print(f"{i} - {BUCKET[i]}")

def find_prob(app_name,hour):
    time_of_day = HOUR_BUCKET[hour]
    app_count = BUCKET[time_of_day].count(app_name)
    total_count = len(BUCKET[time_of_day])
    if total_count == 0:
        return None
    prob = app_count/total_count

    return prob

if __name__ == "__main__":
    create_bucket()
    p = find_prob("chrome",12)
    print(p)

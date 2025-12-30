from db.db_engine import get_connection
from collections import defaultdict

def buildchain():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT app_name, opened_at FROM app_sessions ORDER BY opened_at")
    sessions = cursor.fetchall()

    transitions = defaultdict(int)

    for i in range(len(sessions)-1):
        prev_app = sessions[i][0]
        curr_app = sessions[i+1][0]

        if prev_app != curr_app:
            transitions[(prev_app,curr_app)] += 1
    
    cursor.close()
    conn.close()
    return transitions

# MARKOV MODEL
def build_transition_probs(transitions):
    totals = defaultdict(int)
    probs = {}

    for (prev,curr),count in transitions.items():
        totals[prev] += count

    for (prev,curr),count in transitions.items():
        probs[(prev,curr)] = count / totals[prev]
    
    return probs

if __name__ == "__main__":
    chains = buildchain()
    for i,j in chains.items():
        print(i," -> ",j)
    probs = build_transition_probs(chains)
    for i,j in probs.items():
        print(i," -> ",j)

from db.db_engine import get_connection
from collections import defaultdict

#could be made dynamic later depending on time of day or other factors
IDLE_THRESHOLD = 60 # 1 min
SESSION_THRESHOLD = 10800 # 3 hrs

def buildchain():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT app_name, opened_at, closed_at FROM app_sessions ORDER BY opened_at")
    sessions = cursor.fetchall()

    transitions = []

    for i in range(len(sessions)-1):
        prev_app = sessions[i][0]
        curr_app = sessions[i+1][0]

        prev_closed = sessions[i][2]
        curr_opened = sessions[i+1][1]

        if prev_closed is None:#edge case if not closed prev app
            continue
        
        if curr_opened - prev_closed > SESSION_THRESHOLD:
            transitions.append((prev_app,"__EMPTY__",prev_closed))
            transitions.append(("__EMPTY__",curr_app,curr_opened))

        elif curr_opened - prev_closed > IDLE_THRESHOLD:
            transitions.append((prev_app,"__IDLE__",prev_closed))
            
        elif prev_app != curr_app:
            transitions.append((prev_app,curr_app,curr_opened))
    
    cursor.close()
    conn.close()
    return transitions

# MARKOV MODEL
def build_transition_probs(transitions):
    counts = defaultdict(int)
    totals = defaultdict(int)
    probs = {}

    for prev,curr, _  in transitions:
        counts[(prev,curr)] += 1
        totals[prev] += 1

    for (prev,curr),count in counts.items():
        probs[(prev,curr)] = count / totals[prev]
    
    return probs

if __name__ == "__main__":
    chains = buildchain()
    print("---CHAINS (events)---")
    for prev, curr, t in chains:
        print(prev, "->", curr, "@", t)


    probs = build_transition_probs(chains)
    print("\n---PROBABILTIES---")
    for i,j in probs.items():
        print(i," -> ",j)

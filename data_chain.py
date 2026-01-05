from db.db_engine import get_connection
from collections import defaultdict

#could be made dynamic later depending on time of day or other factors
IDLE_THRESHOLD = 60 # 1 min
SESSION_THRESHOLD = 10800 # 3 hrs
OCCURENCE_THRESHOLD = 7 
CONFIDENCE_GAP = 0.15

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

#for 2d markov model
def buildchain_2():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT app_name, opened_at, closed_at
        FROM app_sessions
        ORDER BY opened_at
    """)
    sessions = cursor.fetchall()

    # Step 1: build a normalized sequence (apps + EMPTY/IDLE)
    sequence = []

    for i in range(len(sessions)):
        curr_app, curr_opened, curr_closed = sessions[i]

        if not sequence:
            sequence.append((curr_app, curr_opened))
            continue

        prev_app, prev_opened = sequence[-1]
        prev_closed = sessions[i - 1][2]

        gap = curr_opened - prev_closed

        if gap > SESSION_THRESHOLD:
            sequence.append(("__EMPTY__", prev_closed))
        elif gap > IDLE_THRESHOLD:
            sequence.append(("__IDLE__", prev_closed))

        sequence.append((curr_app, curr_opened))

    # Step 2: build pure 2nd-order transitions
    transitions = []

    for i in range(2, len(sequence)):
        prev_prev_app = sequence[i - 2][0]
        prev_app = sequence[i - 1][0]
        curr_app = sequence[i][0]
        curr_time = sequence[i][1]

        if prev_app != curr_app:
            transitions.append(
                (prev_prev_app, prev_app, curr_app, curr_time)
            )

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
    
    return probs,totals

def build_2d_transition_probs(transitions):
    totals = defaultdict(int)
    counts = defaultdict(int)
    probs = {}

    for prev_prev,prev,curr,_ in transitions:
        counts[(prev_prev,prev,curr)] += 1
        totals[(prev_prev,prev)] += 1

    for (prev_prev,prev,curr),count in counts.items():
        probs[(prev_prev,prev,curr)] = count / totals[prev_prev,prev]
    
    return probs,totals

def inference_layer(probs_1d, probs_2d, totals_1d, totals_2d):
    """
    Returns a predictor function that decides:
    - use 2D Markov
    - or fallback to 1D Markov
    """
    def predict(prev_prev, prev):
        # ---------- STEP 1: occurrence check ----------
        total_2d = totals_2d.get((prev_prev, prev), 0)

        if total_2d < OCCURENCE_THRESHOLD:
            # fallback to 1D
            candidates_1d = [
                (curr, p)
                for (p_prev, curr), p in probs_1d.items()
                if p_prev == prev
            ]
            if not candidates_1d:
                return None
            return max(candidates_1d, key=lambda x: x[1])[0]

        # ---------- STEP 2: collect 2D candidates ----------
        candidates_2d = [
            (curr, p)
            for (pp, p, curr), p in probs_2d.items()
            if pp == prev_prev and p == prev
        ]

        if not candidates_2d:
            # safety fallback
            return None

        # ---------- STEP 3: confidence check ----------
        candidates_2d.sort(key=lambda x: x[1], reverse=True)

        best_app, best_prob = candidates_2d[0]

        if len(candidates_2d) == 1:
            return best_app  # only one option → confident

        second_prob = candidates_2d[1][1]

        if (best_prob - second_prob) < CONFIDENCE_GAP:
            # fallback to 1D
            candidates_1d = [
                (curr, p)
                for (p_prev, curr), p in probs_1d.items()
                if p_prev == prev
            ]
            if not candidates_1d:
                return None
            return max(candidates_1d, key=lambda x: x[1])[0]

        # ---------- STEP 4: trust 2D ----------
        return best_app

    return predict

        

if __name__ == "__main__":
    chains = buildchain()
    # print("---CHAINS (events)---")
    # for prev, curr, t in chains:
    #     print(prev, "->", curr, "@", t)
    
    chains_2d = buildchain_2()
    # for a, b, c, t in chains_2d:
    #     print(f"({a}, {b}) → {c} @ {t}")

    probs_1d,totals_1d = build_transition_probs(chains)
    probs_2d,totals_2d = build_2d_transition_probs(chains_2d)
    predict = inference_layer(probs_1d=probs_1d,probs_2d=probs_2d,totals_1d=totals_1d,totals_2d=totals_2d)
    # use the last two apps from 2D chain
    #last_prev_prev, last_prev, _, _ = chains_2d[-1]
    last_prev_prev = "spotify"
    last_prev = "chrome"
    result = predict(last_prev_prev, last_prev)
    print(f"Predicted next app after ({last_prev_prev}, {last_prev}) → {result}")

    # print("\n---PROBABILTIES---")
    # for i,j in probs_2d.items():
    #     print(i," -> ",j)

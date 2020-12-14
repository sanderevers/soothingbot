from collections import defaultdict

def run(d,start,end):
    current_states = {start}

    while True:
        possible = defaultdict(set)
        for node in current_states:
            for sym,dsts in d[node].items():
                possible[sym].update(dsts)
        accepting = bool(current_states & end)
        input_sym = yield accepting, set(possible.keys())
        print(f'got:{input_sym} possible: {possible}')
        current_states = possible[input_sym]
        if not current_states:
            break

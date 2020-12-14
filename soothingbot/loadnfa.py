import json
import sys
from collections import defaultdict
from .composite_emoji import join_to_next, join_to_prev, collect_composite_emoji

# def parse(data):
#     [g] = pydot.graph_from_dot_data(data.replace(' ',''))
#     edges = [(e.source, e]

'''
Transform libre json graph format into
{0: {'a': {1}, 1: set()} 
'''
def graph_to_dict(graph):
    d = defaultdict(lambda: defaultdict(set))
    start = graph['start']
    end = set(graph['end'])
    for edge in graph['edges']:
        d[edge['src']][edge.get('symbol','')].add(edge['dst'])
    return d,start,end

def dfs(d,start,seen):
    seen.append(start)
    for sym,dsts in d[start].items():
        for dst in dsts:
            if not dst in seen:
                dfs(d,dst,seen)
    return seen

'''
Collapse consecutive edges representing one Unicode point into one.
Mutates d.
'''
def collapse_unicode_dfs(d,start,seen):
    seen.append(start)
    symdsts = d[start]
    newsyms = defaultdict(set)
    todelete = set()
    for sym,dsts in symdsts.items():
        try:
            symbytes = bytes(sym, 'latin1')
        except UnicodeEncodeError:
            break
        depth = (count_leading_ones(symbytes[0]) - 1) if len(sym)>0 else 0
        if depth > 0:
            todelete.add(sym)
            for dst in dsts:
                for s,ds in collect_unicode_tails(d, dst, depth, symbytes).items():
                    newsyms[s].update(ds)
    for sym in todelete:
        del symdsts[sym]
    for s,ds in newsyms.items():
        symdsts[s].update(ds)
    for sym,dsts in symdsts.items():
        for dst in dsts:
            if dst not in seen:
                collapse_unicode_dfs(d, dst, seen)
    return seen

def collect_unicode_tails(d,src,depth,prefix):
    if depth==0: #or: does not start with 10
        return {str(prefix,'utf8'):{src}}
    res = defaultdict(set)
    for sym,dsts in d[src].items():
        for dst in dsts:
            for s,ds in collect_unicode_tails(d,dst,depth-1,prefix+bytes(sym,'latin1')).items():
                res[s].update(ds)
    return res

def collapse_emoji_dfs(d,start,end,seen):
    seen.append(start)
    newsyms = defaultdict(set)
    for sym,dsts in d[start].items():
        if not (join_to_next(sym) or join_to_prev(sym)):
            for dst in dsts:
                for s,ds in collect_composite_emoji(d, dst, end, sym, True).items():
                    newsyms[s].update(ds)

    newd = defaultdict(lambda: defaultdict(set))
    for sym,dsts in newsyms.items():
        for dst in dsts:
            if dst not in seen:
                newd.update(collapse_emoji_dfs(d, dst, end, seen))
    newd[start] = newsyms
    return newd



# how many consecutive leading bits (msb) of byte_as_int are 1
def count_leading_ones(byte_as_int):
    return next(i for i in range(8) if not byte_as_int & 2**(7-i))

def pretty_edge(sym,dsts):
    return f'{sym or " "}:{len(sym)} -> {",".join(map(str,dsts))}'

def pretty(d,order,end):
    out = ''
    for node in order:
        out += f'{node:3d}' + ('* ' if node in end else '  ')
        out += '\n     '.join(pretty_edge(*e) for e in d[node].items())
        out += '\n'
    return out


def process(graph, debug=False):
    d,start,end = graph_to_dict(graph)

    if debug:
        r1 = dfs(d,start,[])
        print(pretty(d,r1,end))
        print()

    reachable = collapse_unicode_dfs(d,start,[])
    for n in set(d.keys()) - set(reachable):
        del d[n]

    if debug:
        print(pretty(d,reachable,end))

    r2 = []
    nd = collapse_emoji_dfs(d,start,end,r2)

    if debug:
        print(pretty(nd,r2,end))

    return nd,start,end

def nfa_from_file(filename):
    with open(filename) as f:
        graph = json.loads(f.read())
    return process(graph)

if __name__=='__main__':
    if len(sys.argv)>1:
        filename=sys.argv[1]
        with open(filename) as f:
            graph = json.loads(f.read())
    else:
        graph = json.loads(sys.stdin.read())
    process(graph,True)



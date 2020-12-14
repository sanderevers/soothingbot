import unicodedata
from collections import defaultdict

# nv?(jnv?)* -> second group must be greedy
# def pnfa():
#     {0:[(normalsym, {1,2,3})],
#      1:[(vs16,{2,3})],
#      2:[(zwj,{0})],
#      3:accept}

def collect_composite_emoji(d,src,end,prefix,acceptprefix):
    res = defaultdict(set)
    if src in end:
        res[prefix].update({src})
    for sym,dsts in d[src].items():
        if join_to_prev(sym):
            for dst in dsts:
                for s,ds in collect_composite_emoji(d,dst,end,prefix+sym,True).items():
                    res[s].update(ds)
        elif join_to_next(sym):
            for dst in dsts:
                for s,ds in collect_composite_emoji(d,dst,end,prefix+sym,False).items():
                    res[s].update(ds)
        elif acceptprefix:
            res[prefix].update({src})
        else:
            for dst in dsts:
                for s,ds in collect_composite_emoji(d,dst,end,prefix+sym,True).items():
                    res[s].update(ds)
    return res

def join_to_next(sym):
    return sym == zero_width_joiner

def join_to_prev(sym):
    return sym==variation_selector_16 or unicodedata.category(sym[0])=='Sk'


def split_emoji(syms):
    out = []
    cur = ''
    acceptprefix = False
    for sym in syms:
        if join_to_prev(sym):
            cur+=sym
        elif join_to_next(sym):
            cur+=sym
            acceptprefix = False
        elif acceptprefix:
            out.append(cur)
            cur = sym
        else:
            acceptprefix = True
            cur += sym
    if acceptprefix:
        out.append(cur)
    return out



variation_selector_16='\ufe0f'
zero_width_joiner='\u200d'
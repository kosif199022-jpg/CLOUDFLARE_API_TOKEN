#!/usr/bin/env python3
"""Validate finite DAG structure only, never causal truth."""
import json,sys
from collections import deque
def verify(x):
    nodes=x["nodes"]; edges=x["edges"]
    if not isinstance(nodes,list) or any(not isinstance(n,str) or not n for n in nodes) or len(set(nodes))!=len(nodes):
        raise ValueError("unique nonempty string nodes required")
    if not isinstance(edges,list): raise ValueError("edge list required")
    adj={n:[] for n in nodes}; degree={n:0 for n in nodes}; seen=set()
    for e in edges:
        if not isinstance(e,list) or len(e)!=2 or any(not isinstance(n,str) for n in e): raise ValueError("two string endpoints required")
        a,b=e
        if a not in adj or b not in adj: raise ValueError("unknown endpoint")
        if a==b: raise ValueError("self loop")
        if (a,b) in seen: raise ValueError("duplicate edge")
        seen.add((a,b));adj[a].append(b);degree[b]+=1
    q=deque(n for n in nodes if degree[n]==0); order=[]
    while q:
        a=q.popleft();order.append(a)
        for b in adj[a]:
            degree[b]-=1
            if degree[b]==0:q.append(b)
    return {"acyclic":len(order)==len(nodes),"topological_order":order if len(order)==len(nodes) else None,"causal_effect_verified":False}
if __name__=="__main__":
    try: print(json.dumps(verify(json.load(sys.stdin))))
    except (ValueError,KeyError,TypeError) as e:
        print(json.dumps({"error":str(e)}));sys.exit(2)


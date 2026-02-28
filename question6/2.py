from collections import defaultdict, deque


def max_flow_edmonds_karp(cap_graph, src, dst):
    """
    Calculates maximum flow using Edmonds–Karp algorithm.

    Idea:
    Use BFS to repeatedly find shortest augmenting paths
    in the residual network and update flows.

    Complexity:
    Time  -> O(V * E^2)
    Space -> O(V + E)
    """
    res_net = defaultdict(lambda: defaultdict(int))

    for u in cap_graph:
        for v, capacity in cap_graph[u].items():
            res_net[u][v] += capacity
    total_flow = 0

    while True:
        #  Step 1: BFS to find augmenting path
        parent_map = {src: None}
        q = deque([src])

        while q and dst not in parent_map:
            current = q.popleft()
            for nxt in res_net[current]:
                if nxt not in parent_map and res_net[current][nxt] > 0:
                    parent_map[nxt] = current
                    q.append(nxt)
        if dst not in parent_map:
            break

        #  Step 2
        flow = float('inf')
        node = dst

        while node != src:
            prev = parent_map[node]
            flow = min(flow, res_net[prev][node])
            node = prev

        #  Step 3
        node = dst
        while node != src:
            prev = parent_map[node]
            res_net[prev][node] -= flow
            res_net[node][prev] += flow
            node = prev
            total_flow += flow

    return total_flow
#  Graph data 
NETWORK = {
    'KTM': {'JA': 10, 'JB': 15},
    'JA': {'KTM': 10, 'PH': 8, 'BS': 5},
    'JB': {'KTM': 15, 'JA': 4, 'BS': 12},
    'PH': {'JA': 8, 'BS': 6},
    'BS': {'JA': 5, 'JB': 12, 'PH': 6},
}
if __name__ == "__main__":
    max_result = max_flow_edmonds_karp(NETWORK, 'KTM', 'BS')

    print(f"Maximum flow (trucks/hour): {max_result}")
    print(f"Min-cut: JA->BS(5) + JB->BS(12) + PH->BS(6) = 23")
    print(f"Max-flow == Min-cut: {max_result == 23}")
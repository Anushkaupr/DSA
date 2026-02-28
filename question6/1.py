import heapq
import math


def compute_safest_routes(graph, start):
    """
    Computes the safest routes from a given start node.

    Approach:
    Convert each probability p into a weight using -log(p),
    which transforms the problem into a shortest path problem.
    Then apply Dijkstra’s algorithm.

    Complexity:
    Time  -> O((V + E) log V)
    Space -> O(V)
    """
    distances = {node: float('inf') for node in graph}
    parent = {node: None for node in graph}

    distances[start] = 0.0
    heap = [(0.0, start)]

    while heap:
        current_dist, current_node = heapq.heappop(heap)
        if current_dist > distances[current_node]:
            continue
        for neighbor, prob in graph[current_node]:
            weight = -math.log(prob)

            candidate_dist = current_dist + weight
            if candidate_dist < distances[neighbor]:
                distances[neighbor] = candidate_dist
                parent[neighbor] = current_node
                heapq.heappush(heap, (candidate_dist, neighbor))

    return distances, parent
def get_path(parent, start, end):
    """Reconstructs path from start to end using parent links."""
    route = []
    node = end

    while node is not None:
        route.append(node)
        node = parent[node]
    route.reverse()

    return route if route and route[0] == start else []
# Graph definition
GRAPH = {
    'KTM': [('JA', 0.90), ('JB', 0.80)],
    'JA': [('KTM', 0.90), ('PH', 0.95), ('BS', 0.70)],
    'JB': [('KTM', 0.80), ('JA', 0.60), ('BS', 0.90)],
    'PH': [('JA', 0.95), ('BS', 0.85)],
    'BS': [('JA', 0.70), ('JB', 0.90), ('PH', 0.85)],
}
if __name__ == "__main__":
    dist_map, parent_map = compute_safest_routes(GRAPH, 'KTM')

    print("=== Safest paths from KTM ===")
    for destination in ['JA', 'JB', 'PH', 'BS']:
        safety_score = math.exp(-dist_map[destination])
        path = get_path(parent_map, 'KTM', destination)

        print(f"KTM -> {destination}: safety = {safety_score:.4f} "
              f"path = {' -> '.join(path)}")
        


        
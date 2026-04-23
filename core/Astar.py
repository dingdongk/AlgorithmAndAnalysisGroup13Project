# core/Astar.py
import pickle
from core.Min_heap import MinHeap
from core.Graph import normalize_edge
from core.Dijkstra import reconstruct_path, calculate_path_time


def dijkstra_all_distances(graph, start, avoid_nodes=None, avoid_edges=None):
    """
    Run Dijkstra from one source and return shortest distance to every reachable node.
    This is used for ALT landmark preprocessing.

    Returns:
        dict: {node: shortest_distance_from_start}
    """
    if avoid_nodes is None:
        avoid_nodes = set()
    if avoid_edges is None:
        avoid_edges = set()

    if not graph.has_node(start) or start in avoid_nodes:
        return {}

    heap = MinHeap()
    counter = 0

    dist = {start: 0}
    heap.push((0, counter, start))

    while not heap.is_empty():
        curr_dist, _, u = heap.pop()

        if curr_dist > dist.get(u, float("inf")):
            continue

        for edge in graph.get_neighbors(u):
            v = edge.v

            if v in avoid_nodes:
                continue

            if normalize_edge(u, v, undirected=True) in avoid_edges:
                continue

            new_dist = curr_dist + edge.distance

            if new_dist < dist.get(v, float("inf")):
                dist[v] = new_dist
                counter += 1
                heap.push((new_dist, counter, v))

    return dist


def choose_landmarks(graph, k=4):
    """
    Choose landmark nodes for ALT.

    Simple farthest-point style heuristic:
    1. pick the first node
    2. run Dijkstra to find the farthest reachable node
    3. repeat from the newest farthest node until k landmarks

    This is simple and suitable for your project.
    """
    nodes = graph.nodes()
    if not nodes:
        return []

    if k <= 0:
        return []

    landmarks = []

    # start with the first node in the graph
    current = nodes[0]
    landmarks.append(current)

    while len(landmarks) < min(k, len(nodes)):
        dist_map = dijkstra_all_distances(graph, current)

        if not dist_map:
            # fallback: add first not-yet-used node
            for node in nodes:
                if node not in landmarks:
                    landmarks.append(node)
                    current = node
                    break
            continue

        # farthest node not already used as landmark
        farthest_node = None
        farthest_dist = -1

        for node, d in dist_map.items():
            if node not in landmarks and d > farthest_dist:
                farthest_dist = d
                farthest_node = node

        if farthest_node is None:
            # fallback
            for node in nodes:
                if node not in landmarks:
                    farthest_node = node
                    break

        if farthest_node is None:
            break

        landmarks.append(farthest_node)
        current = farthest_node

    return landmarks


def preprocess_landmarks(graph, landmarks):
    """
    Precompute shortest distances from each landmark to all nodes.

    Returns:
        dict:
        {
            landmark1: {nodeA: d1, nodeB: d2, ...},
            landmark2: {nodeA: d1, nodeB: d2, ...},
            ...
        }
    """
    landmark_distances = {}

    for landmark in landmarks:
        landmark_distances[landmark] = dijkstra_all_distances(graph, landmark)

    return landmark_distances


def alt_heuristic(node, target, landmark_distances):
    """
    ALT heuristic using triangle inequality:

        h(v) = max over landmarks L of |dist(L,target) - dist(L,v)|

    Since some nodes may be unreachable from some landmarks, we only use
    landmarks where both distances exist.
    """
    best = 0

    for landmark, dist_map in landmark_distances.items():
        if node in dist_map and target in dist_map:
            estimate = abs(dist_map[target] - dist_map[node])
            if estimate > best:
                best = estimate

    return best


def alt_distance(graph, start, end, landmark_distances, avoid_nodes=None, avoid_edges=None):
    """
    ALT search for shortest distance.

    Returns:
    {
        "path": [...],
        "total_distance": ...,
        "total_time": 0,
        "visited_count": ...
    }
    or None if no path exists.
    """
    if avoid_nodes is None:
        avoid_nodes = set()
    if avoid_edges is None:
        avoid_edges = set()

    if not graph.has_node(start) or not graph.has_node(end):
        return None

    if start in avoid_nodes or end in avoid_nodes:
        return None

    heap = MinHeap()
    counter = 0

    g_cost = {start: 0}
    previous = {start: None}
    visited_count = 0

    start_h = alt_heuristic(start, end, landmark_distances)
    heap.push((start_h, counter, start))

    while not heap.is_empty():
        f_cost, _, u = heap.pop()
        visited_count += 1

        # stale entry protection:
        current_expected_f = g_cost.get(u, float("inf")) + alt_heuristic(u, end, landmark_distances)
        if f_cost > current_expected_f:
            continue

        if u == end:
            path = reconstruct_path(previous, start, end)
            return {
                "path": path,
                "total_distance": g_cost[end],
                "total_time": 0,
                "visited_count": visited_count,
            }

        for edge in graph.get_neighbors(u):
            v = edge.v

            if v in avoid_nodes:
                continue

            if normalize_edge(u, v, undirected=True) in avoid_edges:
                continue

            new_g = g_cost[u] + edge.distance

            if new_g < g_cost.get(v, float("inf")):
                g_cost[v] = new_g
                previous[v] = u
                h = alt_heuristic(v, end, landmark_distances)
                counter += 1
                heap.push((new_g + h, counter, v))

    return None


def enrich_alt_result_with_time(graph, result, start_hour):
    """
    For a distance-optimal ALT result, compute actual total travel time
    using the time-dependent edge lists.
    """
    if result is None:
        return None

    result["total_time"] = calculate_path_time(graph, result["path"], start_hour)
    return result

def save_landmark_data(filename, landmarks, landmark_distances):
    data = {
        "landmarks": landmarks,
        "distances": landmark_distances
    }
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def load_landmark_data(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data["landmarks"], data["distances"]
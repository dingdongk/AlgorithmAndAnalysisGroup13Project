import pickle
from core.Min_heap import MinHeap
from core.Graph import normalize_edge
from core.Dijkstra import reconstruct_path, calculate_path_time


def dijkstra_all_distances(graph, start, avoid_nodes=None, avoid_edges=None):
    # Run Dijkstra from a single node to all nodes (mainly use for preprocessing landmark)
    if avoid_nodes is None:
        avoid_nodes = set()
    if avoid_edges is None:
        avoid_edges = set()

    if not graph.has_node(start) or start in avoid_nodes:
        return {}

    heap = MinHeap()
    counter = 0

    # Shortest distance to each node
    dist = {start: 0}
    heap.push((0, counter, start))

    while not heap.is_empty():
        curr_dist, _, u = heap.pop()

        # Skip outdated entries
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
    # choose landmarks using greedy farthest-node strategy
    nodes = list(graph.nodes())
    if not nodes:
        return []

    # Start with any node
    landmarks = [nodes[0]]

    while len(landmarks) < min(k, len(nodes)):

        best_node = None
        best_score = -1

        for node in nodes:

            # Skip the node become landmarks already
            if node in landmarks:
                continue


            min_distance_to_landmark = float('inf')


            # Greedy Approximation algorithm
            for lm in landmarks:

                dist_map = dijkstra_all_distances(graph, lm) 
                distance = dist_map.get(node, float('inf')) 

                # Find closest landmark to this node
                if distance < min_distance_to_landmark:
                    min_distance_to_landmark = distance


            score = min_distance_to_landmark
            # Finding the largest distance (worst coverage)
            # Get the node that landmark in landmarks['j', 'L'] haven't coverage good enought to become new landmark
            if score > best_score:
                best_score = score
                best_node = node


        if best_node is None:
            break

        landmarks.append(best_node)

    return landmarks



def preprocess_landmarks(graph, landmarks):
    # Preprocess distances from each landmark to all nodes
    landmark_distances = {}

    for landmark in landmarks:
        landmark_distances[landmark] = dijkstra_all_distances(graph, landmark)

    return landmark_distances


def alt_heuristic(node, target, landmark_distances):
    # ALT heuristic using triangle inequality
    best = 0

    for landmark, dist_map in landmark_distances.items():
        if node in dist_map and target in dist_map:
            estimate = abs(dist_map[target] - dist_map[node])
            if estimate > best:
                best = estimate

    return best


def alt_distance(graph, start, end, landmark_distances, avoid_nodes=None, avoid_edges=None):
    # ALT search using precomputed landmarks
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

    # Actual distance
    g_cost = {start: 0}
    previous = {start: None}
    visited_count = 0

    start_h = alt_heuristic(start, end, landmark_distances)
    # f = g + h
    heap.push((start_h, counter, start)) 

    while not heap.is_empty():
        f_cost, _, u = heap.pop()
        visited_count += 1

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
    # Compute actual travel time for ALT path
    if result is None:
        return None

    result["total_time"] = calculate_path_time(graph, result["path"], start_hour)
    return result

def save_landmark_data(filename, landmarks, landmark_distances):
    # Save ALT preprocessing to file
    data = {
        "landmarks": landmarks,
        "distances": landmark_distances
    }
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def load_landmark_data(filename):
    # Load ALT preprocessing from file
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data["landmarks"], data["distances"]

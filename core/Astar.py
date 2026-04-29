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
    To choose the landmarks (the nodes) for the graph, we will apply k-center expression
    new_Landmark = Max(Min(distance(Landmark, Vertex))) with Landmark ∈ Landmarks
    Vertex is from all vertices of the graph
    Purpose: Using greedy approximation agolrithm to find to be farthest from the landmark inside
    the list of landamarks.
    landmarks = ['A', 'B'] find the new landmark farthest from A and B
    :param k is the number of landmarks user want to find

    """
    nodes = list(graph.nodes())
    if not nodes:
        return []

    landmarks = [nodes[0]]

    # min(k,len(nodes)) ensure that the component inside landmarks not reach out the node of the graph
    # for example k = 4 but graph only have 3 node which mean len(nodes) = 3
    # the landmarks can choose 3 landmarks only
    # if we set like this (while len(landmarks) < k = 4:) it will become infinite loop
    while len(landmarks) < min(k, len(nodes)):
        # For easy to understand: if k = 2 or 1, the first landmark always is node[0]
        # If k = 2, the second landmark is choosing the largest distance from the first landmark
        # Follow the expression: before we have the second landmark, we only have one landmark
        # The expression will be reduced [new_landmark = Max(landmark to all vertices of the graph)]
        # For example: this is the nodes of the graph ['J', 'B', 'G', 'T', 'E', 'D', 'A', 'H', 'F', 'L', 'C']
        # First landmark J:{'J': 0, 'B': 10, 'G': 5, 'T': 8, 'E': 12, 'D': 16, 'A': 12, 'H': 26, 'F': 18, 'L': 27, 'C': 15}
        # The second just choose the farthest distance from landmark(j) which is L
        # L:{'J': 27, 'B': 17, 'G': 26, 'T': 29, 'E': 25, 'D': 11, 'A': 15, 'H': 15, 'F': 9, 'L': 0, 'C': 15}
        # From the third landmark, we will follow the original expression
        # new_Landmark = Max(Min(distance(Landmark, vertex))) with Landmark ∈ Landmarks["J","L"]
        # The function will be Max(Min(distance('J','J'), distance('L','J')), Min(distance('J','B'),distance('L','B')), Min(...), ...)
        # It will stop when we finish find all the node
        # After that we have new_landmark is H
        # If we continue, the number of distance from landmark to vertex inside Min() will increase equaly with number of landmark at the moment
        # new_Landmark = Max(Min(distance(Landmark to all Vertex of the graph))) with Landmark ∈ Landmarks["J","L","H"]
        # Max(Min(distance('J','J'), distance('L','J'), distance('H','J')), Min(distance('J','B'),distance('L','B'), distance('H','B')), Min(...), ...)


        best_node = None
        best_score = -1

        for node in nodes:

            #Skip the node become landmarks already
            if node in landmarks:
                continue


            min_distance_to_landmark = float('inf')


            # Greedy Approximation algorithm
            for lm in landmarks:

                dist_map = dijkstra_all_distances(graph, lm) # return such as {'j':0, 'B':10,...}
                distance = dist_map.get(node, float('inf')) # if don't have the node, return infinite. But the graph is connected so it cannot happen
                # Finding the shortest distance of each landmark to current node of the graph
                # for example node = B, landmarks = ['J','L']
                # it will compare the minimum distance of (J to B) and (L to B)
                # The minium is used to calculate the coverage (distance) of the landmark with that node
                # The smaller of distance mean the landmark coverage that node good
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

# core/Dijkstra.py

from core.Min_heap import MinHeap
from core.Graph import normalize_edge


def reconstruct_path(previous, start, end):
    """
    Reconstruct path from start to end using predecessor map.
    Returns list of nodes, or [] if no path exists.
    """
    if start == end:
        return [start]

    if end not in previous:
        return []

    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous.get(current)

    path.reverse()

    if not path or path[0] != start:
        return []

    return path


def calculate_path_distance(graph, path):
    """
    Sum the distance along a given path.
    """
    if not path or len(path) == 1:
        return 0

    total = 0
    for i in range(len(path) - 1):
        edge = graph.get_edge(path[i], path[i + 1])
        if edge is None:
            raise ValueError(f"Missing edge in path: {path[i]} -> {path[i + 1]}")
        total += edge.distance

    return total


def calculate_path_time(graph, path, start_hour):
    """
    Sum travel time along a path using time-dependent edge weights.

    Assumption:
    - time_list values are in minutes
    - the hour bucket changes when elapsed minutes cross a full hour boundary
    """
    if not path or len(path) == 1:
        return 0

    total_minutes = 0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        edge = graph.get_edge(u, v)

        if edge is None:
            raise ValueError(f"Missing edge in path: {u} -> {v}")

        current_hour = (start_hour + (total_minutes // 60)) % 24
        total_minutes += edge.time_list[current_hour]

    return total_minutes


def dijkstra_distance(graph, start, end, avoid_nodes=None, avoid_edges=None):
    """
    Standard Dijkstra minimizing total distance.

    Returns a dictionary:
    {
        "path": [...],
        "total_distance": ...,
        "total_time": ...,
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

    dist = {start: 0}
    previous = {start: None}
    visited_count = 0

    heap.push((0, counter, start))

    while not heap.is_empty():
        curr_dist, _, u = heap.pop()
        visited_count += 1

        # stale entry check
        if curr_dist > dist.get(u, float("inf")):
            continue

        if u == end:
            path = reconstruct_path(previous, start, end)
            total_distance = curr_dist
            total_time = 0  # this solver is distance-based only
            return {
                "path": path,
                "total_distance": total_distance,
                "total_time": total_time,
                "visited_count": visited_count,
            }

        for edge in graph.get_neighbors(u):
            v = edge.v

            if v in avoid_nodes:
                continue

            if normalize_edge(u, v, undirected=True) in avoid_edges:
                continue

            new_dist = curr_dist + edge.distance

            if new_dist < dist.get(v, float("inf")):
                dist[v] = new_dist
                previous[v] = u
                counter += 1
                heap.push((new_dist, counter, v))

    return None


def dijkstra_time(graph, start, end, start_hour, avoid_nodes=None, avoid_edges=None):
    """
    Dijkstra minimizing total travel time.

    Edge time depends on arrival hour:
        current_hour = (start_hour + elapsed_minutes // 60) % 24

    Returns a dictionary:
    {
        "path": [...],
        "total_distance": ...,
        "total_time": ...,
        "visited_count": ...
    }
    or None if no path exists.
    """
    if avoid_nodes is None:
        avoid_nodes = set()
    if avoid_edges is None:
        avoid_edges = set()

    if start_hour < 0 or start_hour > 23:
        raise ValueError("start_hour must be between 0 and 23.")

    if not graph.has_node(start) or not graph.has_node(end):
        return None

    if start in avoid_nodes or end in avoid_nodes:
        return None

    heap = MinHeap()
    counter = 0

    best_time = {start: 0}
    previous = {start: None}
    visited_count = 0

    # store (priority_time, counter, node)
    heap.push((0, counter, start))

    while not heap.is_empty():
        curr_time, _, u = heap.pop()
        visited_count += 1

        # stale entry check
        if curr_time > best_time.get(u, float("inf")):
            continue

        if u == end:
            path = reconstruct_path(previous, start, end)
            total_distance = calculate_path_distance(graph, path)
            total_time = curr_time
            return {
                "path": path,
                "total_distance": total_distance,
                "total_time": total_time,
                "visited_count": visited_count,
            }

        for edge in graph.get_neighbors(u):
            v = edge.v

            if v in avoid_nodes:
                continue

            if normalize_edge(u, v, undirected=True) in avoid_edges:
                continue

            current_hour = (start_hour + (curr_time // 60)) % 24
            travel_time = edge.time_list[current_hour]
            new_time = curr_time + travel_time

            if new_time < best_time.get(v, float("inf")):
                best_time[v] = new_time
                previous[v] = u
                counter += 1
                heap.push((new_time, counter, v))

    return None


def enrich_distance_result_with_time(graph, result, start_hour):
    """
    For a distance-optimal result, compute its actual time.
    """
    if result is None:
        return None

    path = result["path"]
    result["total_time"] = calculate_path_time(graph, path, start_hour)
    return result


def enrich_time_result_with_distance(graph, result):
    """
    For a time-optimal result, ensure distance is filled.
    """
    if result is None:
        return None

    path = result["path"]
    result["total_distance"] = calculate_path_distance(graph, path)
    return result
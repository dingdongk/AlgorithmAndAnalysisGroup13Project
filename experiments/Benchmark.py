# experiments/Benchmark.py

import time
import os
import sys

# Allow running Benchmark.py directly
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.Graph import load_graph_txt, parse_avoid_nodes, parse_avoid_edges
from core.Dijkstra import dijkstra_distance, dijkstra_time, enrich_distance_result_with_time
from core.Astar import (
    choose_landmarks,
    preprocess_landmarks,
    alt_distance,
    enrich_alt_result_with_time,
    save_landmark_data,
    load_landmark_data,
)

GRAPH_FILE = "data/graph_by_road.txt"
QUERY_FILE = "tests/Sample_queries.txt"
LANDMARK_COUNT = 4
ALT_DATA_FILE = "data/alt_preprocessed.pkl"


def load_queries(filename):
    """
    Query format:
    source|destination|start_hour|avoid_nodes|avoid_edges
    """
    queries = []

    with open(filename, "r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split("|")
            if len(parts) != 5:
                raise ValueError(
                    f"Invalid query format on line {line_number}. "
                    f"Expected 5 fields separated by |"
                )

            source = parts[0].strip()
            destination = parts[1].strip()
            start_hour = int(parts[2].strip())
            avoid_nodes = parse_avoid_nodes(parts[3].strip())
            avoid_edges = parse_avoid_edges(parts[4].strip(), undirected=True)

            queries.append({
                "source": source,
                "destination": destination,
                "start_hour": start_hour,
                "avoid_nodes": avoid_nodes,
                "avoid_edges": avoid_edges,
            })

    return queries


def benchmark_distance_dijkstra(graph, queries):
    total_runtime = 0.0
    total_visited = 0
    success_count = 0

    for q in queries:
        start = time.perf_counter()
        result = dijkstra_distance(
            graph,
            q["source"],
            q["destination"],
            avoid_nodes=q["avoid_nodes"],
            avoid_edges=q["avoid_edges"],
        )
        end = time.perf_counter()

        total_runtime += (end - start)

        if result is not None:
            total_visited += result["visited_count"]
            success_count += 1

    return {
        "algorithm": "Dijkstra (distance)",
        "queries": len(queries),
        "successful_queries": success_count,
        "total_runtime_sec": total_runtime,
        "average_runtime_sec": total_runtime / len(queries) if queries else 0,
        "average_visited_nodes": total_visited / success_count if success_count else 0,
    }


def benchmark_distance_alt(graph, queries, landmark_distances):
    total_runtime = 0.0
    total_visited = 0
    success_count = 0

    for q in queries:
        start = time.perf_counter()
        result = alt_distance(
            graph,
            q["source"],
            q["destination"],
            landmark_distances,
            avoid_nodes=q["avoid_nodes"],
            avoid_edges=q["avoid_edges"],
        )
        end = time.perf_counter()

        total_runtime += (end - start)

        if result is not None:
            total_visited += result["visited_count"]
            success_count += 1

    return {
        "algorithm": "ALT (distance)",
        "queries": len(queries),
        "successful_queries": success_count,
        "total_runtime_sec": total_runtime,
        "average_runtime_sec": total_runtime / len(queries) if queries else 0,
        "average_visited_nodes": total_visited / success_count if success_count else 0,
    }


def benchmark_time_dijkstra(graph, queries):
    total_runtime = 0.0
    total_visited = 0
    success_count = 0

    for q in queries:
        start = time.perf_counter()
        result = dijkstra_time(
            graph,
            q["source"],
            q["destination"],
            q["start_hour"],
            avoid_nodes=q["avoid_nodes"],
            avoid_edges=q["avoid_edges"],
        )
        end = time.perf_counter()

        total_runtime += (end - start)

        if result is not None:
            total_visited += result["visited_count"]
            success_count += 1

    return {
        "algorithm": "Dijkstra (time)",
        "queries": len(queries),
        "successful_queries": success_count,
        "total_runtime_sec": total_runtime,
        "average_runtime_sec": total_runtime / len(queries) if queries else 0,
        "average_visited_nodes": total_visited / success_count if success_count else 0,
    }


def print_benchmark_result(result):
    print(f"\n=== {result['algorithm']} ===")
    print(f"Queries run: {result['queries']}")
    print(f"Successful queries: {result['successful_queries']}")
    print(f"Total runtime (sec): {result['total_runtime_sec']:.6f}")
    print(f"Average runtime per query (sec): {result['average_runtime_sec']:.6f}")
    print(f"Average visited nodes: {result['average_visited_nodes']:.2f}")


def compare_single_query_correctness(graph, query, landmark_distances):
    dijkstra_result = dijkstra_distance(
        graph,
        query["source"],
        query["destination"],
        avoid_nodes=query["avoid_nodes"],
        avoid_edges=query["avoid_edges"],
    )
    if dijkstra_result is not None:
        dijkstra_result = enrich_distance_result_with_time(graph, dijkstra_result, query["start_hour"])

    alt_result = alt_distance(
        graph,
        query["source"],
        query["destination"],
        landmark_distances,
        avoid_nodes=query["avoid_nodes"],
        avoid_edges=query["avoid_edges"],
    )
    if alt_result is not None:
        alt_result = enrich_alt_result_with_time(graph, alt_result, query["start_hour"])

    print("\n=== Correctness Check (Single Query) ===")
    print("Source:", query["source"])
    print("Destination:", query["destination"])
    print("Start hour:", query["start_hour"])

    if dijkstra_result is None and alt_result is None:
        print("Both algorithms returned no path.")
        return

    if dijkstra_result is None or alt_result is None:
        print("Mismatch: one algorithm found a path and the other did not.")
        return

    print("Dijkstra distance:", dijkstra_result["total_distance"])
    print("ALT distance:", alt_result["total_distance"])
    print("Dijkstra time on distance-path:", dijkstra_result["total_time"])
    print("ALT time on distance-path:", alt_result["total_time"])

    if dijkstra_result["total_distance"] == alt_result["total_distance"]:
        print("Distance results match.")
    else:
        print("Distance results do NOT match.")


def main():
    print("Loading graph...")
    graph = load_graph_txt(GRAPH_FILE, undirected=True)
    print(f"Graph loaded. Nodes: {graph.node_count()}, Directed edges: {graph.edge_count()}")

    print("\nLoading queries...")
    queries = load_queries(QUERY_FILE)
    print(f"Loaded {len(queries)} queries.")

    if os.path.exists(ALT_DATA_FILE):
        print("\nLoading cached ALT data...")
        load_start = time.perf_counter()
        landmarks, landmark_distances = load_landmark_data(ALT_DATA_FILE)
        load_end = time.perf_counter()
        preprocess_time = 0.0
        load_time = load_end - load_start

        print("Loaded landmarks:", landmarks)
        print(f"ALT cache load time (sec): {load_time:.6f}")
        print("ALT preprocessing time (sec): 0.000000 (cached)")
    else:
        print("\nSelecting landmarks for ALT...")
        landmarks = choose_landmarks(graph, k=LANDMARK_COUNT)
        print("Landmarks:", landmarks)

        print("\nPreprocessing landmark distances...")
        preprocess_start = time.perf_counter()
        landmark_distances = preprocess_landmarks(graph, landmarks)
        preprocess_end = time.perf_counter()
        preprocess_time = preprocess_end - preprocess_start

        save_landmark_data(ALT_DATA_FILE, landmarks, landmark_distances)

        print(f"ALT preprocessing time (sec): {preprocess_time:.6f}")
        print(f"ALT data saved to: {ALT_DATA_FILE}")

    if queries:
        compare_single_query_correctness(graph, queries[0], landmark_distances)

    distance_dijkstra_result = benchmark_distance_dijkstra(graph, queries)
    distance_alt_result = benchmark_distance_alt(graph, queries, landmark_distances)
    time_dijkstra_result = benchmark_time_dijkstra(graph, queries)

    print_benchmark_result(distance_dijkstra_result)
    print_benchmark_result(distance_alt_result)
    print_benchmark_result(time_dijkstra_result)

    print("\n=== Summary ===")
    print("Use these results in your empirical evaluation section.")
    print("Remember to discuss:")
    print("- ALT preprocessing cost")
    print("- ALT distance-query speed vs Dijkstra distance-query speed")
    print("- Dijkstra time-query performance")
    print("- Whether ALT gives enough improvement on your graph size")


if __name__ == "__main__":
    main()
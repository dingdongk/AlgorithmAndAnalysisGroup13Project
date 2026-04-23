# main.py
import os
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
USE_ALT_FOR_DISTANCE = True
LANDMARK_COUNT = 4
ALT_DATA_FILE = "data/alt_preprocessed.pkl"


def format_path(path):
    if not path:
        return "No path"
    return " -> ".join(path)


def print_result(title, result):
    print(f"\n=== {title} ===")
    if result is None:
        print("No path found.")
        return

    print("Path:", format_path(result["path"]))
    print("Total distance:", result["total_distance"])
    print("Total travel time:", result["total_time"])
    print("Visited nodes:", result["visited_count"])


def get_user_input():
    print("SMART PATH FINDER")
    print("-" * 50)

    source = input("Enter source node: ").strip()
    destination = input("Enter destination node: ").strip()

    while True:
        try:
            start_hour = int(input("Enter start hour (0-23): ").strip())
            if 0 <= start_hour <= 23:
                break
            print("Start hour must be between 0 and 23.")
        except ValueError:
            print("Please enter a valid integer hour.")

    avoid_nodes_text = input(
        "Enter nodes to avoid (comma-separated, or leave blank): "
    ).strip()

    avoid_edges_text = input(
        "Enter edges to avoid in format A-B,B-C (or leave blank): "
    ).strip()

    avoid_nodes = parse_avoid_nodes(avoid_nodes_text)
    avoid_edges = parse_avoid_edges(avoid_edges_text, undirected=True)

    return source, destination, start_hour, avoid_nodes, avoid_edges


def main():
    print("Loading graph...")
    graph = load_graph_txt(GRAPH_FILE, undirected=True)
    print(f"Graph loaded successfully.")
    print(f"Nodes: {graph.node_count()}")
    print(f"Directed edges stored: {graph.edge_count()}")

    landmark_distances = None
    landmarks = []

    if USE_ALT_FOR_DISTANCE:
        if os.path.exists(ALT_DATA_FILE):
            print("\nLoading ALT preprocessed data...")
            landmarks, landmark_distances = load_landmark_data(ALT_DATA_FILE)
            print("Loaded landmarks:", landmarks)
        else:
            print("\nPreparing ALT landmarks...")
            landmarks = choose_landmarks(graph, k=LANDMARK_COUNT)
            landmark_distances = preprocess_landmarks(graph, landmarks)
            save_landmark_data(ALT_DATA_FILE, landmarks, landmark_distances)
            print("Selected landmarks:", landmarks)
            print(f"ALT data saved to: {ALT_DATA_FILE}")

    while True:
        print("\n" + "=" * 60)

        try:
            source, destination, start_hour, avoid_nodes, avoid_edges = get_user_input()

            if not graph.has_node(source):
                print(f"Source node '{source}' does not exist in the graph.")
                continue

            if not graph.has_node(destination):
                print(f"Destination node '{destination}' does not exist in the graph.")
                continue

            # Shortest distance path
            if USE_ALT_FOR_DISTANCE and landmark_distances is not None:
                distance_result = alt_distance(
                    graph,
                    source,
                    destination,
                    landmark_distances,
                    avoid_nodes=avoid_nodes,
                    avoid_edges=avoid_edges,
                )
                distance_result = enrich_alt_result_with_time(graph, distance_result, start_hour)
                distance_title = "Shortest Distance Path (ALT)"
            else:
                distance_result = dijkstra_distance(
                    graph,
                    source,
                    destination,
                    avoid_nodes=avoid_nodes,
                    avoid_edges=avoid_edges,
                )
                distance_result = enrich_distance_result_with_time(graph, distance_result, start_hour)
                distance_title = "Shortest Distance Path (Dijkstra)"

            # Shortest time path
            time_result = dijkstra_time(
                graph,
                source,
                destination,
                start_hour,
                avoid_nodes=avoid_nodes,
                avoid_edges=avoid_edges,
            )

            print_result(distance_title, distance_result)
            print_result("Shortest Time Path (Dijkstra)", time_result)

        except Exception as e:
            print("Error:", e)

        again = input("\nDo you want to run another query? (y/n): ").strip().lower()
        if again != "y":
            print("Exiting Smart Path Finder.")
            break


if __name__ == "__main__":
    main()
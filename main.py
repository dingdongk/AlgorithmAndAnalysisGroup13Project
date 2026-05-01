import os
from core.Graph import load_graph_txt, save_graph_txt, parse_avoid_nodes, parse_avoid_edges
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


def update_edge_time_interactive(graph):
    print("\n=== Update Edge Time List ===")

    u = input("Enter source node (u): ").strip()
    v = input("Enter destination node (v): ").strip()

    if not graph.has_node(u) or not graph.has_node(v):
        print("One or both nodes do not exist.")
        return

    print("Enter 24 time values (comma-separated):")

    try:
        time_input = input("Time list: ").strip()
        new_times = [int(x.strip()) for x in time_input.split(",")]

        if len(new_times) != 24:
            print("Error: You must enter exactly 24 values.")
            return

        graph.update_edge_time_list(u, v, new_times, undirected=True)
        print(f"Updated time list for edge: {u} <-> {v}")

        save_graph_txt(graph, GRAPH_FILE)
        print(f"Saved updated graph to {GRAPH_FILE}")

    except ValueError:
        print("Invalid input. Please enter integers only.")


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
    print("Graph loaded successfully.")
    print(f"Nodes: {graph.node_count()}")
    print(f"Directed edges stored: {graph.edge_count()}")

    landmark_distances = None

    # ALT Preprocessing and Loading
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

    # Main Menu Loop
    while True:
        print("\n" + "=" * 60)
        print("SMART PATH FINDER MENU")
        print("1. Run path query")
        print("2. Update edge time list")
        print("3. Exit")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            try:
                source, destination, start_hour, avoid_nodes, avoid_edges = get_user_input()

                if not graph.has_node(source):
                    print(f"Source node '{source}' does not exist.")
                    continue

                if not graph.has_node(destination):
                    print(f"Destination node '{destination}' does not exist.")
                    continue

                # Dijkstra Distance
                dijkstra_dist_result = dijkstra_distance(
                    graph,
                    source,
                    destination,
                    avoid_nodes=avoid_nodes,
                    avoid_edges=avoid_edges,
                )
                dijkstra_dist_result = enrich_distance_result_with_time(
                    graph, dijkstra_dist_result, start_hour
                )

                # ALT Distance
                alt_dist_result = alt_distance(
                    graph,
                    source,
                    destination,
                    landmark_distances,
                    avoid_nodes=avoid_nodes,
                    avoid_edges=avoid_edges,
                )
                alt_dist_result = enrich_alt_result_with_time(
                    graph, alt_dist_result, start_hour
                )

                # Time
                time_result = dijkstra_time(
                    graph,
                    source,
                    destination,
                    start_hour,
                    avoid_nodes=avoid_nodes,
                    avoid_edges=avoid_edges,
                )

                print_result("Shortest Distance Path (Dijkstra)", dijkstra_dist_result)
                print_result("Shortest Distance Path (ALT)", alt_dist_result)
                print_result("Shortest Time Path (Dijkstra)", time_result)

            except Exception as e:
                print("Error:", e)

        elif choice == "2":
            update_edge_time_interactive(graph)

        elif choice == "3":
            print("Exiting Smart Path Finder.")
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
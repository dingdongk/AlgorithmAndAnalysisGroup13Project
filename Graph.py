import random
class Edge:
    def __init__(self, v, distance, time_list):
        self.v = v
        self.distance = distance  # int
        self.time_list = time_list #int

# =========================
# Graph class
# =========================
class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v, distance=None, time_list=None):
        if u == v:
            return


        if distance is None:
            distance = random.randint(1, 10)

        if time_list is None:
            time_list = []
            for h in range(24):
                if 7 <= h <= 9 or 17 <= h <= 19:
                    factor = random.uniform(1.3, 1.6)
                else:
                    factor = random.uniform(0.8, 1.2)
                time_list.append(distance * factor)


        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []


        if not any(e.v == v for e in self.adj[u]):
            self.adj[u].append(Edge(v, distance, time_list))
        if not any(e.v == u for e in self.adj[v]):
            self.adj[v].append(Edge(u, distance, time_list))  # symmetric distance

def load_graph_txt(filename="graph1.txt"):
    g = Graph()

    with open(filename, "r",encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split('|')

            u = parts[0]
            v = parts[1]
            distance = int(parts[2])
            time_list = list(map(int, parts[3].split(",")))

            g.add_edge(u, v, distance, time_list)

    return g

class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, item):
        self.heap.append(item)
        self.heapify_up(len(self.heap) - 1)

    def extract_min(self):
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        min_value = self.heap[0]
        self.heap[0] = self.heap.pop()  
        self.heapify_down(0)
        return min_value

    def is_empty(self):
        return len(self.heap) == 0

    def heapify_up(self, index):
        while index > 0:
            parent_index = (index - 1) // 2
            if self.heap[index]["key"] < self.heap[parent_index]["key"]:
                self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
                index = parent_index
            else:
                break

    def heapify_down(self, index):
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        if left < len(self.heap) and self.heap[left]["key"] < self.heap[smallest]["key"]:
            smallest = left
        if right < len(self.heap) and self.heap[right]["key"] < self.heap[smallest]["key"]:
            smallest = right

        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self.heapify_down(smallest)
def find_shortest_time_path(graph, start, end, start_hour):
    min_heap=MinHeap()
    min_heap.insert({"key": 0, "node": start, "path": [start], "dist": 0})
    visited_costs = {start: 0}

    while not min_heap.is_empty():
        curr_data = min_heap.extract_min()
        curr_time = curr_data["key"]
        curr_node = curr_data["node"]
        path = curr_data["path"]
        curr_dist = curr_data["dist"]

        if curr_node == end:
            return {"path": path, "time": curr_time, "dist": curr_dist}

        if curr_node in graph.adj:
            for edge in graph.adj[curr_node]:
                arrival_h = int((start_hour + curr_time) % 24)
                travel_cost = edge.time_list[arrival_h]

                new_time = curr_time + travel_cost
                if edge.v not in visited_costs or new_time < visited_costs[edge.v]:
                    visited_costs[edge.v] = new_time
                    min_heap.insert({
                        "key": new_time,
                        "node": edge.v,
                        "path": path + [edge.v],
                        "dist": curr_dist + edge.distance
                    })
    return None
my_graph = load_graph_txt("graph_by_road")
start_node = "bùi thị xuân"  
end_node = "văn cao"  
hour = 12

result = find_shortest_time_path(my_graph, start_node, end_node, hour)
if result:
    print(f"Nodes visited: {len(result['path'])}")
    print(f"Total Time: {round(result['time'], 2)} minutes")
    print(f"Total Distance: {result['dist']} km")
    print(f"Route: {' ➔ '.join(result['path'])}")
else:
    print("No path found.")



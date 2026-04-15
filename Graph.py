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

    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split()

            u = parts[0]
            v = parts[1]
            distance = int(parts[2])
            time_list = list(map(int, parts[3].split(",")))

            g.add_edge(u, v, distance, time_list)

    return g

graph = load_graph_txt()
print(graph.adj["node_1"][1].v)






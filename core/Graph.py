class Edge:
    def __init__(self, v, distance, time_list):
        self.v = v
        self.distance = distance
        self.time_list = time_list

    def __repr__(self):
        return f"Edge(v={self.v}, distance={self.distance})"

class Graph:
    def __init__(self):
        # Adjacency list: node to list of edges
        self.adj = {}
        self._edge_count = 0

    def add_node(self, u):
        if u not in self.adj:
            self.adj[u] = []

    def add_edge(self, u, v, distance, time_list, undirected=True):
        # Add edge with distance and 24-hour time list
        if u == v:
            return

        if distance < 0:
            raise ValueError("Distance must be non-negative.")

        if len(time_list) != 24:
            raise ValueError("Each edge must have exactly 24 hourly time values.")

        self.add_node(u)
        self.add_node(v)

        if not self._has_edge(u, v):
            self.adj[u].append(Edge(v, distance, time_list))
            self._edge_count += 1

        if undirected and not self._has_edge(v, u):
            # Copy list to avoid accidental shared mutation
            self.adj[v].append(Edge(u, distance, list(time_list)))
            self._edge_count += 1

    def _has_edge(self, u, v):
        if u not in self.adj:
            return False
        for edge in self.adj[u]:
            if edge.v == v:
                return True
        return False

    def get_neighbors(self, u):
        return self.adj.get(u, [])

    def has_node(self, u):
        return u in self.adj

    def nodes(self):
        return list(self.adj.keys())

    def node_count(self):
        return len(self.adj)

    def edge_count(self):
        return self._edge_count

    def get_edge(self, u, v):
        # Return edge from u to v
        for edge in self.adj.get(u, []):
            if edge.v == v:
                return edge
        return None

    def update_edge_time_list(self, u, v, new_time_list, undirected=True):
        # Update time list for an edge (used for time list updates)
        if len(new_time_list) != 24:
            raise ValueError("Time list must contain exactly 24 values.")

        edge_uv = self.get_edge(u, v)
        if edge_uv is None:
            raise ValueError(f"Edge not found: {u} -> {v}")

        edge_uv.time_list = list(new_time_list)

        if undirected:
            edge_vu = self.get_edge(v, u)
            if edge_vu is not None:
                edge_vu.time_list = list(new_time_list)

    def __repr__(self):
        return f"Graph(nodes={self.node_count()}, directed_edges={self.edge_count()})"


def _parse_graph_line(line):
    # Parsing for graph
    #Supports two formats:
       # u|v|distance|t1,t2,...,t24
       # u v distance t1,t2,...,t24
       # This assumes node names do not contain spaces.
    line = line.strip()
    if not line:
        return None

    if "|" in line:
        parts = line.split("|")
    else:
        parts = line.split()

    if len(parts) != 4:
        raise ValueError(f"Invalid graph line format: {line}")

    u = parts[0].strip()
    v = parts[1].strip()
    distance = int(parts[2].strip())
    time_list = [int(x.strip()) for x in parts[3].split(",")]

    if len(time_list) != 24:
        raise ValueError(f"Edge ({u}, {v}) does not have 24 time values.")

    return u, v, distance, time_list

def save_graph_txt(graph, filename):
    # Save graph back to pipe-separated text format:
    # u|v|distance|t0,t1,...,t23
    saved_edges = set()

    with open(filename, "w", encoding="utf-8") as f:
        for u in graph.nodes():
            for edge in graph.get_neighbors(u):
                v = edge.v
                key = tuple(sorted((u, v)))

                if key in saved_edges:
                    continue

                saved_edges.add(key)

                time_text = ",".join(str(x) for x in edge.time_list)
                f.write(f"{u}|{v}|{edge.distance}|{time_text}\n")

def load_graph_txt(filename, undirected=True):
    # Load graph from a text file.
    # Supports 2 formats
    # u|v|distance|t1,t2,...,t24
    # u v distance t1,t2,...,t24
    graph = Graph()

    with open(filename, "r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            stripped = raw_line.strip()

            if not stripped:
                continue

            # Allow simple comment lines
            if stripped.startswith("#"):
                continue

            try:
                parsed = _parse_graph_line(stripped)
                if parsed is None:
                    continue

                u, v, distance, time_list = parsed
                graph.add_edge(u, v, distance, time_list, undirected=undirected)

            except Exception as e:
                raise ValueError(f"Error parsing line {line_number}: {e}")

    return graph


def normalize_edge(u, v, undirected=True):
    # Standardize edge representation for avoidance checks.
    # If undirected=True:
    # ('B', 'A') and ('A', 'B') become the same tuple.
    if undirected:
        return tuple(sorted((u, v)))
    return (u, v)


def parse_avoid_nodes(text):
    #Parse avoid nodes from a comma-separated string.
    # Example:
    #    "A,B,C" -> {"A", "B", "C"}
    #    "" -> set()
    if text is None:
        return set()

    text = text.strip()
    if not text:
        return set()

    return {item.strip() for item in text.split(",") if item.strip()}


def parse_avoid_edges(text, undirected=True):
    # Parse avoid edges from a comma-separated list like:
    #    "A-B,B-C"
    if text is None:
        return set()

    text = text.strip()
    if not text:
        return set()

    result = set()
    items = [item.strip() for item in text.split(",") if item.strip()]

    for item in items:
        if "-" not in item:
            raise ValueError(f"Invalid edge format: {item}. Use A-B")
        u, v = item.split("-", 1)
        u = u.strip()
        v = v.strip()
        if not u or not v:
            raise ValueError(f"Invalid edge format: {item}. Use A-B")
        result.add(normalize_edge(u, v, undirected=undirected))

    return result
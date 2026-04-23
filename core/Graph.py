# core/Graph.py

class Edge:
    def __init__(self, v, distance, time_list):
        self.v = v
        self.distance = distance
        self.time_list = time_list

    def __repr__(self):
        return f"Edge(v={self.v}, distance={self.distance})"


class Graph:
    def __init__(self):
        # adjacency list:
        # {
        #   "A": [Edge("B", 5, [...]), Edge("C", 2, [...])],
        #   ...
        # }
        self.adj = {}
        self._edge_count = 0

    def add_node(self, u):
        if u not in self.adj:
            self.adj[u] = []

    def add_edge(self, u, v, distance, time_list, undirected=True):
        """
        Add an edge u -> v.
        If undirected=True, also add v -> u.

        Constraints:
        - u != v
        - distance >= 0
        - len(time_list) == 24
        """
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
            # copy list to avoid accidental shared mutation
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
        """
        Return the Edge object from u to v, or None if not found.
        """
        for edge in self.adj.get(u, []):
            if edge.v == v:
                return edge
        return None

    def __repr__(self):
        return f"Graph(nodes={self.node_count()}, directed_edges={self.edge_count()})"


def _parse_graph_line(line):
    """
    Supports two formats:

    1) Pipe-separated:
       u|v|distance|t1,t2,...,t24

    2) Space-separated:
       u v distance t1,t2,...,t24
       This assumes node names do not contain spaces.
    """
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


def load_graph_txt(filename, undirected=True):
    """
    Load graph from a text file.

    File line formats supported:
    - u|v|distance|t1,t2,...,t24
    - u v distance t1,t2,...,t24

    Returns:
        Graph
    """
    graph = Graph()

    with open(filename, "r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            stripped = raw_line.strip()

            if not stripped:
                continue

            # allow simple comment lines
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
    """
    Standardize edge representation for avoidance checks.

    If undirected=True:
        ('B', 'A') and ('A', 'B') become the same tuple.
    """
    if undirected:
        return tuple(sorted((u, v)))
    return (u, v)


def parse_avoid_nodes(text):
    """
    Parse avoid nodes from a comma-separated string.
    Example:
        "A,B,C" -> {"A", "B", "C"}
        "" -> set()
    """
    if text is None:
        return set()

    text = text.strip()
    if not text:
        return set()

    return {item.strip() for item in text.split(",") if item.strip()}


def parse_avoid_edges(text, undirected=True):
    """
    Parse avoid edges from a comma-separated list like:
        "A-B,B-C"

    Returns:
        set of normalized edge tuples
    """
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
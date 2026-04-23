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


def load_graph_txt(filename="graph_full.txt"):
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

g = Graph()
g.add_edge("a","b",4)
g.add_edge("a","e",5)
g.add_edge("b","c",2)
g.add_edge("b","e",6)
g.add_edge("b","d",7)
g.add_edge("c","d",10)
g.add_edge("c","f",8)
g.add_edge("e","d",3)
g.add_edge("d","f",4)

import math
class MinHeap:
    def __init__(self):
        self.heap = []

    # =========================
    # Helper index functions
    # =========================
    def parent(self, i):
        return (i - 1) // 2

    def left(self, i):
        return 2 * i + 1

    def right(self, i):
        return 2 * i + 2

    # =========================
    # Push (heapify up)
    # =========================
    def push(self, item):
        self.heap.append(item)
        i = len(self.heap) - 1

        while i > 0:
            p = self.parent(i)

            if self.heap[i] < self.heap[p]:
                self.heap[i], self.heap[p] = self.heap[p], self.heap[i]
                i = p
            else:
                break

    # =========================
    # Pop min (heapify down)
    # =========================
    def pop(self):
        if not self.heap:
            return None

        root = self.heap[0]
        last = self.heap.pop()

        if self.heap:
            self.heap[0] = last
            self.heapify_down(0)

        return root

    # =========================
    # Heapify down
    # =========================
    def heapify_down(self, i):
        size = len(self.heap)

        while True:
            l = self.left(i)
            r = self.right(i)
            smallest = i

            if l < size and self.heap[l] < self.heap[smallest]:
                smallest = l

            if r < size and self.heap[r] < self.heap[smallest]:
                smallest = r

            if smallest == i:
                break

            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest

    # =========================
    # Peek (xem min)
    # =========================
    def top(self):
        return self.heap[0] if self.heap else None

    # =========================
    # Check empty
    # =========================
    def empty(self):
        return len(self.heap) == 0

    def print_heap(self):
        print(self.heap)

def dijkstra(graph, start, target):
    dist = {node: math.inf for node in graph.adj}
    prev = {node: None for node in graph.adj}

    dist[start] = 0

    pq = MinHeap()
    pq.push((0, start))   # (distance, node)

    while not pq.empty():
        cur_dist, u = pq.pop()

        if cur_dist > dist[u]:
            continue

        if u == target:
            break

        for edge in graph.adj[u]:
            v = edge.v
            weight = edge.distance

            new_dist = cur_dist + weight

            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                pq.push((new_dist, v))

    # truy vết đường đi
    path = []
    node = target

    while node is not None:
        path.append(node)
        node = prev[node]

    path.reverse()

    return path, dist[target]

def dijkstra_all(graph, start):

    dist = {node: math.inf for node in graph.adj}
    dist[start] = 0

    pq = MinHeap()
    pq.push((0, start))

    while not pq.empty():
        cur_dist, u = pq.pop()

        if cur_dist > dist[u]:
            continue

        for edge in graph.adj[u]:
            v = edge.v
            w = edge.distance

            nd = cur_dist + w
            if nd < dist[v]:
                dist[v] = nd
                pq.push((nd, v))

    return dist

def select_farthest_landmarks(graph, k=3):
    nodes = list(graph.adj.keys())

    landmarks = [random.choice(nodes)]

    # khoảng cách từ landmark đến tất cả node
    dist_cache = {}

    dist_cache[landmarks[0]] = dijkstra_all(graph, landmarks[0])

    while len(landmarks) < k:
        best_node = None
        best_dist = -1

        for node in nodes:
            if node in landmarks:
                continue

            # khoảng cách tới landmark gần nhất (max-min strategy)
            min_dist = min(dist_cache[l][node] for l in landmarks)

            if min_dist > best_dist:
                best_dist = min_dist
                best_node = node

        landmarks.append(best_node)
        dist_cache[best_node] = dijkstra_all(graph, best_node)

    return landmarks, dist_cache

def alt_heuristic(v, goal, landmarks, dist_cache):
    best = 0

    for L in landmarks:
        dv = dist_cache[L].get(v, math.inf)
        dg = dist_cache[L].get(goal, math.inf)

        if dv == math.inf or dg == math.inf:
            continue

        best = max(best, abs(dg - dv))

    return best

def astar_alt(graph, start, goal, landmarks, dist_cache):

    g_score = {node: math.inf for node in graph.adj}
    g_score[start] = 0

    pq = MinHeap()
    pq.push((alt_heuristic(start, goal, landmarks, dist_cache), start))

    prev = {node: None for node in graph.adj}

    while not pq.empty():
        f, u = pq.pop()

        # ❗ skip stale states (QUAN TRỌNG)
        if f > g_score[u] + alt_heuristic(u, goal, landmarks, dist_cache):
            continue

        if u == goal:
            break

        for edge in graph.adj[u]:
            v = edge.v
            w = edge.distance

            tentative_g = g_score[u] + w

            if tentative_g < g_score[v]:
                g_score[v] = tentative_g
                prev[v] = u

                f_score = tentative_g + alt_heuristic(v, goal, landmarks, dist_cache)
                pq.push((f_score, v))

    # reconstruct
    if g_score[goal] == math.inf:
        return [], math.inf

    path = []
    node = goal

    while node is not None:
        path.append(node)
        node = prev[node]

    path.reverse()

    return path, g_score[goal]

    return path, g_score[goal]

landmarks, dist_cache = select_farthest_landmarks(g, k=3)

path, cost = astar_alt(g, "a", "f", landmarks, dist_cache)

print(path, cost)
# path, cost = dijkstra(g, "a", "f")
# print("Đường đi ngắn nhất:", " -> ".join(path))
# print("Tổng distance:", cost)

# def generate_graph_file(input_file="graph_by_road.txt",
#                         output_file="graph_full.txt"):
#
#     with open(input_file, "r", encoding="utf-8") as fin, \
#          open(output_file, "w", encoding="utf-8") as fout:
#
#         for line in fin:
#             parts = line.strip().split(",")
#             if len(parts) < 2:
#                 continue
#
#             u = parts[0].strip()
#             v = parts[1].strip()
#
#             if u == v:
#                 continue
#
#             # distance int > 0
#             distance = random.randint(1, 10)
#
#             # ===== time_list mới (không quy luật) =====
#             time_list = []
#             current = random.randint(1, distance * 2)
#
#             for _ in range(24):
#                 # biến động nhẹ
#                 current += random.randint(-2, 2)
#
#                 # spike ngẫu nhiên (kẹt xe bất chợt)
#                 if random.random() < 0.15:
#                     current += random.randint(3, 7)
#
#                 # đảm bảo > 0
#                 current = max(1, current)
#
#                 time_list.append(current)
#
#             # ========================================
#
#             time_str = ",".join(map(str, time_list))
#             fout.write(f"{u}|{v}|{distance}|{time_str}\n")
#
#     print("Đã tạo file:", output_file)


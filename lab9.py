"""
Лабораторная работа № 9. Вариант 11.

Графы: матрица смежности и списки смежности.
BFS, итеративный DFS и проверка двудольности (И4).
"""
import random
import sys
import time
from collections import deque


class MatrixGraph:
    """Граф на матрице смежности. Память Θ(n²)."""

    def __init__(self, n):
        self.n = n
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v):
        self.matrix[u][v] = self.matrix[v][u] = 1

    def has_edge(self, u, v):
        return self.matrix[u][v] == 1

    def neighbors(self, v):
        return [u for u in range(self.n) if self.matrix[v][u]]


class ListGraph:
    """Граф на списках смежности. Память Θ(n + m)."""

    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]

    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.adj[v].append(u)

    def has_edge(self, u, v):
        return v in self.adj[u]

    def neighbors(self, v):
        return self.adj[v]


def bfs(graph, start):
    """Обход в ширину: порядок, расстояния, предки."""
    dist = [-1] * graph.n
    parent = [-1] * graph.n
    order = []
    dist[start] = 0
    queue = deque([start])
    while queue:
        v = queue.popleft()
        order.append(v)
        for u in graph.neighbors(v):
            if dist[u] == -1:
                dist[u] = dist[v] + 1
                parent[u] = v
                queue.append(u)
    return order, dist, parent


def dfs(graph, start):
    """Итеративный обход в глубину (без рекурсии)."""
    visited = [False] * graph.n
    order, stack = [], [start]
    while stack:
        v = stack.pop()
        if visited[v]:
            continue
        visited[v] = True
        order.append(v)
        for u in reversed(graph.neighbors(v)):
            if not visited[u]:
                stack.append(u)
    return order


def is_bipartite(graph):
    """Проверка двудольности раскраской в два цвета при BFS.

    Возвращает (двудольный?, цвета, конфликтное ребро).
    """
    color = [-1] * graph.n
    for start in range(graph.n):
        if color[start] != -1:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            v = queue.popleft()
            for u in graph.neighbors(v):
                if color[u] == -1:
                    color[u] = 1 - color[v]
                    queue.append(u)
                elif color[u] == color[v]:
                    return False, color, (v, u)
    return True, color, None


def connected_components(graph):
    """Компоненты связности через повторные BFS."""
    seen = [False] * graph.n
    comps = []
    for v in range(graph.n):
        if not seen[v]:
            order, _, _ = bfs(graph, v)
            for u in order:
                seen[u] = True
            comps.append(sorted(order))
    return comps


def generate(cls, n, m, bipartite=False, seed=42):
    """Случайный разреженный граф; при bipartite=True рёбра только между долями."""
    rng = random.Random(seed)
    g = cls(n)
    edges = set()
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v or (bipartite and u % 2 == v % 2):
            continue
        a, b = sorted((u, v))
        if (a, b) not in edges:
            edges.add((a, b))
            g.add_edge(u, v)
    return g, len(edges)


def memory_kb(graph):
    """Память под матрицу или списки смежности, КБ."""
    if isinstance(graph, MatrixGraph):
        size = sys.getsizeof(graph.matrix) + sum(
            sys.getsizeof(row) for row in graph.matrix)
    else:
        size = sys.getsizeof(graph.adj) + sum(
            sys.getsizeof(row) for row in graph.adj)
    return size / 1024


def main():
    print("=" * 76)
    print("ЛР № 9, вариант 11: графы, BFS/DFS и проверка двудольности")
    print("=" * 76)

    # --- малый тестовый граф: 4-цикл с хвостом + треугольник ---
    small = ListGraph(8)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4),
             (5, 6), (6, 7), (7, 5)]
    for u, v in edges:
        small.add_edge(u, v)

    order, dist, parent = bfs(small, 0)
    print("\nТестовый граф, BFS от вершины 1:")
    print("  порядок:", [v + 1 for v in order])
    print("  расстояния:", [d for d in dist])
    print("  предки:", [p + 1 if p != -1 else -1 for p in parent])
    print("  DFS:", [v + 1 for v in dfs(small, 0)])
    print("  компоненты:", [[v + 1 for v in c]
                            for c in connected_components(small)])

    ok, color, conflict = is_bipartite(small)
    print(f"  двудольный: {ok}", end="")
    if conflict:
        print(f", конфликт рёбер {conflict[0] + 1}-{conflict[1] + 1}")
    else:
        print()

    # компонента без треугольника — двудольная
    good = ListGraph(5)
    for u, v in [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4)]:
        good.add_edge(u, v)
    print("  компонента {1..5} двудольна:", is_bipartite(good)[0])

    # --- сравнение представлений на разреженных графах ---
    print("\nРазреженные графы, m = 3n:")
    print(f"{'n':>5}{'тип':>12}{'m':>7}{'матрица, с':>13}"
          f"{'списки, с':>12}{'матрица, КБ':>14}{'списки, КБ':>12}{'двудольный':>12}")
    for n in (1000, 2000, 4000):
        for label, bip in (("случайный", False), ("двудольный", True)):
            gm, m = generate(MatrixGraph, n, 3 * n, bip, seed=n + int(bip))
            gl, _ = generate(ListGraph, n, 3 * n, bip, seed=n + int(bip))

            t = time.perf_counter(); bfs(gm, 0)
            t_m = time.perf_counter() - t
            t = time.perf_counter(); bfs(gl, 0)
            t_l = time.perf_counter() - t
            ok_m = is_bipartite(gm)[0]
            ok_l = is_bipartite(gl)[0]
            assert ok_m == ok_l

            print(f"{n:>5}{label:>12}{m:>7}{t_m:>13.4f}{t_l:>12.4f}"
                  f"{memory_kb(gm):>14.0f}{memory_kb(gl):>12.0f}"
                  f"{'да' if ok_l else 'нет':>12}")


if __name__ == "__main__":
    main()

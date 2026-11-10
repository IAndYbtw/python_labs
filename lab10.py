"""
Лабораторная работа № 10. Вариант 11.

Дейкстра с линейным поиском и с кучей на сетке k×k.
К4: число кратчайших путей между двумя вершинами.
Критический путь проекта из 14 работ.
"""
import heapq
import random
import time
from collections import deque

INF = float("inf")


def dijkstra_array(adj, s):
    """Дейкстра с линейным поиском минимума: Θ(n²)."""
    n = len(adj)
    dist = [INF] * n
    parent = [-1] * n
    used = [False] * n
    dist[s] = 0
    for _ in range(n):
        v, best = -1, INF
        for i in range(n):
            if not used[i] and dist[i] < best:
                v, best = i, dist[i]
        if v == -1:
            break
        used[v] = True
        for u, w in adj[v]:
            if dist[v] + w < dist[u]:
                dist[u] = dist[v] + w
                parent[u] = v
    return dist, parent


def dijkstra_heap(adj, s):
    """Дейкстра с приоритетной очередью: O(m log n)."""
    n = len(adj)
    dist = [INF] * n
    parent = [-1] * n
    dist[s] = 0
    heap = [(0, s)]
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v]:
            continue
        for u, w in adj[v]:
            if d + w < dist[u]:
                dist[u] = d + w
                parent[u] = v
                heapq.heappush(heap, (dist[u], u))
    return dist, parent


def dijkstra_count(adj, s):
    """Дейкстра + число кратчайших путей до каждой вершины (К4)."""
    n = len(adj)
    dist = [INF] * n
    count = [0] * n
    parent = [-1] * n
    dist[s] = 0
    count[s] = 1
    heap = [(0, s)]
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v]:
            continue
        for u, w in adj[v]:
            nd = d + w
            if nd < dist[u]:
                dist[u] = nd
                count[u] = count[v]
                parent[u] = v
                heapq.heappush(heap, (nd, u))
            elif nd == dist[u]:
                count[u] += count[v]
    return dist, count, parent


def restore_path(parent, target):
    """Восстановление пути по массиву предков."""
    path = []
    while target != -1:
        path.append(target)
        target = parent[target]
    return path[::-1]


def grid_graph(k, max_weight=50, seed=11):
    """Неориентированная сетка k×k; каждая дуга хранится в обе стороны."""
    n = k * k
    adj = [[] for _ in range(n)]
    rng = random.Random(seed + k)

    def idx(r, c):
        return r * k + c

    for r in range(k):
        for c in range(k):
            v = idx(r, c)
            if r + 1 < k:
                u, w = idx(r + 1, c), rng.randint(1, max_weight)
                adj[v].append((u, w)); adj[u].append((v, w))
            if c + 1 < k:
                u, w = idx(r, c + 1), rng.randint(1, max_weight)
                adj[v].append((u, w)); adj[u].append((v, w))
    return adj


# ------------------------- критический путь -------------------------

def topological_order(tasks):
    """Алгоритм Кана. tasks: код -> (длительность, предшественники)."""
    indeg = {v: len(preds) for v, (_, preds) in tasks.items()}
    succ = {v: [] for v in tasks}
    for v, (_, preds) in tasks.items():
        for p in preds:
            succ[p].append(v)
    queue = deque(sorted(v for v, d in indeg.items() if d == 0))
    order = []
    while queue:
        v = queue.popleft()
        order.append(v)
        for u in succ[v]:
            indeg[u] -= 1
            if indeg[u] == 0:
                queue.append(u)
    if len(order) != len(tasks):
        raise ValueError("в сетевом графике есть цикл")
    return order, succ


def critical_path(tasks):
    """ES, EF, LS, LF, резервы и критический путь."""
    order, succ = topological_order(tasks)
    ES, EF = {}, {}
    for v in order:
        t, preds = tasks[v]
        ES[v] = max((EF[p] for p in preds), default=0)
        EF[v] = ES[v] + t
    T = max(EF.values())

    LS, LF = {}, {}
    for v in reversed(order):
        t = tasks[v][0]
        LF[v] = min((LS[u] for u in succ[v]), default=T)
        LS[v] = LF[v] - t

    reserve = {v: LS[v] - ES[v] for v in tasks}
    critical = [v for v in order if reserve[v] == 0]
    return T, ES, EF, LS, LF, reserve, critical


def main():
    print("=" * 78)
    print("ЛР № 10, вариант 11: Дейкстра на сетке и критический путь")
    print("=" * 78)

    # --- малый граф для ручной проверки ---
    small = [[] for _ in range(6)]
    for u, v, w in [(0, 1, 1), (0, 2, 4), (1, 2, 2), (1, 3, 5),
                    (2, 3, 1), (2, 4, 2), (3, 4, 1), (4, 5, 1)]:
        small[u].append((v, w))
    dist, cnt, parent = dijkstra_count(small, 0)
    path = restore_path(parent, 5)
    print("\nМалый граф, Дейкстра от 0:")
    print("  расстояния:", dist)
    print("  число путей:", cnt)
    print("  путь до 5:", " → ".join(map(str, path)), f"(длина {dist[5]})")

    # --- сетка k×k: две реализации ---
    print("\nСетка k×k, веса 1..50:")
    print(f"{'k':>3}{'n':>7}{'m':>8}{'массив, с':>12}{'куча, с':>10}"
          f"{'отнош.':>9}{'d':>7}{'путей':>13}{'верш.':>7}")
    for k in (25, 45, 65):
        adj = grid_graph(k)
        n, m = k * k, sum(len(a) for a in adj)

        t = time.perf_counter(); d1, _ = dijkstra_array(adj, 0)
        t_arr = time.perf_counter() - t
        t = time.perf_counter(); d2, _ = dijkstra_heap(adj, 0)
        t_heap = time.perf_counter() - t
        assert d1 == d2

        d, count, p = dijkstra_count(adj, 0)
        print(f"{k:>3}{n:>7}{m:>8}{t_arr:>12.4f}{t_heap:>10.4f}"
              f"{t_arr / t_heap:>9.1f}{d[n - 1]:>7}{count[n - 1]:>13,}"
              f"{len(restore_path(p, n - 1)):>7}")

    # --- проект из 14 работ ---
    print("\nПроект из 14 работ:")
    tasks = {
        "A": (5, []), "B": (7, ["A"]), "C": (4, ["B"]), "D": (6, ["B"]),
        "E": (10, ["C"]), "F": (9, ["D"]), "G": (3, ["E", "F"]),
        "H": (4, ["C", "D"]), "I": (6, ["G"]), "J": (2, ["H", "I"]),
        "K": (5, ["C"]), "L": (4, ["E", "K"]), "M": (3, ["I", "L"]),
        "N": (2, ["J", "M"]),
    }
    T, ES, EF, LS, LF, R, crit = critical_path(tasks)
    print(f"  длительность проекта: {T} дн.")
    print(f"{'раб.':>6}{'t':>4}{'ES':>5}{'EF':>5}{'LS':>5}{'LF':>5}{'R':>4}{'крит.':>7}")
    for v in sorted(tasks):
        print(f"{v:>6}{tasks[v][0]:>4}{ES[v]:>5}{EF[v]:>5}{LS[v]:>5}"
              f"{LF[v]:>5}{R[v]:>4}{'да' if R[v] == 0 else '':>7}")
    print("  критический путь:", " → ".join(crit))


if __name__ == "__main__":
    main()

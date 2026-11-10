"""
Лабораторная работа № 12. Вариант 11.

Упаковка предметов в контейнеры: точный алгоритм (ДП по подмножествам),
первый подходящий с сортировкой (FFD) и локальный поиск переносом предмета.
"""
import math
import random
import statistics
import time


CAP = 100


def generate_items(n, seed=42):
    """n предметов со случайными размерами 10..50."""
    rng = random.Random(seed)
    return [rng.randint(10, 50) for _ in range(n)]


def first_fit_decreasing(items, cap=CAP):
    """Конструктивная эвристика: первый подходящий с сортировкой."""
    bins = []
    for x in sorted(items, reverse=True):
        for b in bins:
            if sum(b) + x <= cap:
                b.append(x)
                break
        else:
            bins.append([x])
    return bins


def exact_packing(items, cap=CAP):
    """Точный минимум контейнеров: ДП по подмножествам, O(n·2^n).

    Состояние (число контейнеров, свободное место в последнем).
    Возвращает (контейнеры, размер таблицы).
    """
    n = len(items)
    size = 1 << n
    dp = [None] * size
    parent = [None] * size
    dp[0] = (0, -cap)
    for mask in range(size):
        state = dp[mask]
        if state is None:
            continue
        bins, neg_free = state
        free = -neg_free
        for i in range(n):
            if mask & (1 << i):
                continue
            x = items[i]
            if x <= free:
                cand, new_bin = (bins, -(free - x)), False
            else:
                cand, new_bin = (bins + 1, -(cap - x)), True
            nm = mask | (1 << i)
            if dp[nm] is None or cand < dp[nm]:
                dp[nm] = cand
                parent[nm] = (mask, i, new_bin)

    bins, cur, mask = [], [], size - 1
    while mask:
        prev, i, new_bin = parent[mask]
        cur.append(items[i])
        if new_bin:
            bins.append(cur)
            cur = []
        mask = prev
    if cur:
        bins.append(cur)
    return bins, size


def local_search(bins, cap=CAP, max_k=3):
    """Локальный поиск: перепаковка k контейнеров в меньшее число."""
    bins = [b[:] for b in bins]
    removed = 0
    while True:
        order = sorted(range(len(bins)), key=lambda k: sum(bins[k]))
        moved = False
        for k in range(2, min(max_k, len(bins)) + 1):
            idx = set(order[:k])
            group = [x for i in idx for x in bins[i]]
            packed, _ = exact_packing(group, cap)
            if len(packed) < k:
                bins = [b for i, b in enumerate(bins) if i not in idx] + packed
                removed += k - len(packed)
                moved = True
                break
        if not moved:
            return bins, removed


def deviation(bins, opt):
    return (len(bins) - opt) / opt * 100


def main():
    print("=" * 78)
    print("ЛР № 12, вариант 11: упаковка предметов в контейнеры")
    print("=" * 78)

    # --- рост времени точного алгоритма ---
    print("\nТочный алгоритм (ДП по подмножествам), вместимость 100:")
    print(f"{'n':>4}{'2^n':>10}{'оптимум':>10}{'время, с':>12}")
    for n in range(6, 25):
        items = generate_items(n, seed=42)
        t = time.perf_counter()
        bins, states = exact_packing(items)
        dt = time.perf_counter() - t
        print(f"{n:>4}{states:>10}{len(bins):>10}{dt:>12.4f}")
        if dt > 10:
            break

    # --- качество на малых размерностях (М4) ---
    print("\nОтклонение от оптимума, 30 наборов:")
    print(f"{'n':>4}{'FFD, %':>10}{'FFD+перенос, %':>18}"
          f"{'доля оптимума':>16}")
    for n in (6, 7, 8, 9, 10, 12, 15):
        dev_ffd, dev_loc, hits = [], [], 0
        for trial in range(30):
            items = generate_items(n, seed=1000 + trial)
            opt = len(exact_packing(items)[0])
            b1 = first_fit_decreasing(items)
            b2, _ = local_search(b1)
            dev_ffd.append(deviation(b1, opt))
            dev_loc.append(deviation(b2, opt))
            hits += len(b2) == opt
        print(f"{n:>4}{statistics.mean(dev_ffd):>10.2f}"
              f"{statistics.mean(dev_loc):>18.2f}{hits / 30 * 100:>15.0f}%")

    # --- большая размерность ---
    print("\nБольшая размерность, n = 600:")
    items = generate_items(600, seed=7)
    lb = math.ceil(sum(items) / CAP)

    t = time.perf_counter()
    b_ffd = first_fit_decreasing(items)
    t_ffd = time.perf_counter() - t

    t = time.perf_counter()
    b_loc, removed = local_search(b_ffd)
    t_loc = time.perf_counter() - t

    print(f"  нижняя оценка: {lb}")
    print(f"  FFD:           {len(b_ffd)} контейнеров, {t_ffd:.4f} с")
    print(f"  FFD+перенос:   {len(b_loc)} контейнеров, {t_loc:.4f} с, "
          f"убрано {removed}")
    print(f"  улучшение: {len(b_ffd) - len(b_loc)} контейнеров")


if __name__ == "__main__":
    main()

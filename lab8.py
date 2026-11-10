"""
Лабораторная работа № 8. Вариант 11.

Задача о рюкзаке 0/1: два жадных критерия и точное решение (ДП).
Ж4: зависимость отклонения жадного решения от размерности задачи.
"""
import random
import statistics
import time


def knapsack_dp(weights, values, capacity):
    """Точное решение: максимальная ценность (одномерное ДП)."""
    D = [0] * (capacity + 1)
    for wi, vi in zip(weights, values):
        for w in range(capacity, wi - 1, -1):
            D[w] = max(D[w], D[w - wi] + vi)
    return D[capacity]


def greedy(weights, values, capacity, key):
    """Жадный алгоритм: предметы берутся в порядке убывания key."""
    total, remain, chosen = 0, capacity, []
    for i in sorted(range(len(weights)), key=key, reverse=True):
        if weights[i] <= remain:
            chosen.append(i)
            remain -= weights[i]
            total += values[i]
    return total, sorted(chosen)


def greedy_density(weights, values, capacity):
    """Критерий 1: максимальная удельная ценность v/w."""
    return greedy(weights, values, capacity, lambda i: values[i] / weights[i])


def greedy_value(weights, values, capacity):
    """Критерий 2: максимальная ценность v."""
    return greedy(weights, values, capacity, lambda i: values[i])


def experiment(trials=500, n=24, capacity=200, seed=2024):
    """Отклонение жадных решений от оптимума на случайных наборах."""
    rng = random.Random(seed)
    dev = {"плотность": [], "ценность": []}
    hits = {"плотность": 0, "ценность": 0}
    for _ in range(trials):
        weights = [rng.randint(5, 40) for _ in range(n)]
        values = [rng.randint(10, 100) for _ in range(n)]
        opt = knapsack_dp(weights, values, capacity)
        for name, func in (("плотность", greedy_density),
                           ("ценность", greedy_value)):
            got, _ = func(weights, values, capacity)
            dev[name].append((opt - got) / opt * 100)
            hits[name] += got == opt
    return dev, hits


def deviation_by_n(n, trials=500, capacity=200):
    """Ж4: среднее и максимальное отклонение при данном N."""
    rng = random.Random(100 + n)
    dev1, dev2 = [], []
    for _ in range(trials):
        weights = [rng.randint(5, 40) for _ in range(n)]
        values = [rng.randint(10, 100) for _ in range(n)]
        opt = knapsack_dp(weights, values, capacity)
        dev1.append((opt - greedy_density(weights, values, capacity)[0]) / opt * 100)
        dev2.append((opt - greedy_value(weights, values, capacity)[0]) / opt * 100)
    return statistics.mean(dev1), max(dev1), statistics.mean(dev2), max(dev2)


def main():
    print("=" * 74)
    print("ЛР № 8, вариант 11: рюкзак 0/1 — жадные критерии и точное ДП")
    print("=" * 74)

    # --- контрпример ---
    w, v, W = [6, 5, 5], [12, 9, 9], 10
    g1, s1 = greedy_density(w, v, W)
    g2, s2 = greedy_value(w, v, W)
    opt = knapsack_dp(w, v, W)
    print("\nКонтрпример: веса", w, "ценности", v, "W =", W)
    print(f"  по плотности: предметы {s1}, ценность {g1}")
    print(f"  по ценности:  предметы {s2}, ценность {g2}")
    print(f"  оптимум ДП:   ценность {opt}, отклонение {(opt - g1) / opt * 100:.1f}%")

    # --- второй контрпример: ошибка критерия «максимальная ценность» ---
    w2, v2, W2 = [9, 6, 4], [10, 7, 6], 10
    g1, s1 = greedy_density(w2, v2, W2)
    g2, s2 = greedy_value(w2, v2, W2)
    opt2 = knapsack_dp(w2, v2, W2)
    print("\nКонтрпример для критерия «максимальная ценность»:")
    print(f"  по плотности: предметы {s1}, ценность {g1}")
    print(f"  по ценности:  предметы {s2}, ценность {g2}")
    print(f"  оптимум ДП:   ценность {opt2}, отклонение {(opt2 - g2) / opt2 * 100:.1f}%")

    # --- серия случайных наборов ---
    dev, hits = experiment()
    trials = len(dev["плотность"])
    print(f"\nСерия из {trials} наборов (N = 24, W = 200):")
    print(f"{'критерий':<14}{'среднее, %':>12}{'медиана, %':>12}"
          f"{'максимум, %':>13}{'совпало':>10}")
    for name, d in dev.items():
        print(f"{name:<14}{statistics.mean(d):>12.2f}{statistics.median(d):>12.2f}"
              f"{max(d):>13.2f}{hits[name] / trials * 100:>9.1f}%")

    # --- Ж4: отклонение от размерности ---
    print("\nЖ4. Отклонение от размерности (W = 200, по 500 наборов):")
    print(f"{'N':>4}{'плотн. ср., %':>16}{'плотн. макс., %':>18}"
          f"{'ценность ср., %':>18}{'ценность макс., %':>20}")
    for n in (5, 10, 20, 40, 80):
        m1, x1, m2, x2 = deviation_by_n(n)
        print(f"{n:>4}{m1:>16.2f}{x1:>18.2f}{m2:>18.2f}{x2:>20.2f}")

    # --- время работы ---
    print("\nВремя работы при W = 1000:")
    print(f"{'N':>6}{'жадный, с':>14}{'ДП, с':>12}{'раз быстрее':>14}")
    rng = random.Random(1)
    for n in (100, 500, 2000, 5000):
        weights = [rng.randint(5, 40) for _ in range(n)]
        values = [rng.randint(10, 100) for _ in range(n)]
        t = time.perf_counter(); greedy_density(weights, values, 1000)
        t_g = time.perf_counter() - t
        t = time.perf_counter(); knapsack_dp(weights, values, 1000)
        t_dp = time.perf_counter() - t
        print(f"{n:>6}{t_g:>14.5f}{t_dp:>12.5f}{t_dp / t_g:>14.1f}")


if __name__ == "__main__":
    main()

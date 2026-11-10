"""
Лабораторная работа № 7. Вариант 11.

А: числа Фибоначчи — наивная рекурсия, мемоизация, итеративный вариант.
Б: размен суммы 250 монетами 1, 4, 6, 9 — ДП с восстановлением ответа.
Г4: зависимость времени ДП от суммы S.
"""
import time
from collections import Counter
from itertools import combinations_with_replacement

calls = 0  # счётчик вызовов рекурсивной функции


def fib_naive(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n, cache=None):
    global calls
    calls += 1
    if cache is None:
        cache = {}
    if n < 2:
        return n
    if n not in cache:
        cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]


def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_calls(n, cnt):
    """Сколько раз вызывается F(k) при вычислении F(n)."""
    cnt[n] = cnt.get(n, 0) + 1
    if n >= 2:
        count_calls(n - 1, cnt)
        count_calls(n - 2, cnt)


def coin_dp(coins, S, recover=True):
    """Минимальное число монет для суммы S и сам набор монет."""
    D = [0] + [float("inf")] * S
    for s in range(1, S + 1):
        D[s] = min(D[s - c] + 1 for c in coins if c <= s)

    if not recover:
        return D[S]
    if D[S] == float("inf"):
        return None, []

    # обратный проход: ищем монету, которой набрана текущая сумма
    ans, s = [], S
    while s > 0:
        for c in coins:
            if c <= s and D[s] == D[s - c] + 1:
                ans.append(c)
                s -= c
                break
    return int(D[S]), ans


def coin_brute(coins, S):
    """Полный перебор — только для проверки на малых S."""
    for k in range(1, S + 1):
        for combo in combinations_with_replacement(coins, k):
            if sum(combo) == S:
                return k
    return None


def main():
    global calls
    print("=" * 72)
    print("ЛР № 7, вариант 11: Фибоначчи (три способа) и размен суммы (ДП)")
    print("=" * 72)

    # --- повторяющиеся подзадачи ---
    cnt = {}
    count_calls(5, cnt)
    print("\nДерево F(5):",
          ", ".join(f"F({k}) x{v}" for k, v in sorted(cnt.items(), reverse=True)))

    # --- задача А ---
    print("\nЗадача А. Числа Фибоначчи")
    print(f"{'n':>3} {'наивно, с':>11} {'вызовов':>12} {'мемо, с':>10}"
          f" {'вызовов':>9} {'итер., с':>9} {'F(n)':>10}")
    for n in (10, 15, 20, 25, 30, 31):
        calls = 0
        t = time.perf_counter(); f1 = fib_naive(n); t1 = time.perf_counter() - t
        c1 = calls

        calls = 0
        t = time.perf_counter(); f2 = fib_memo(n); t2 = time.perf_counter() - t
        c2 = calls

        t = time.perf_counter(); f3 = fib_iter(n); t3 = time.perf_counter() - t
        assert f1 == f2 == f3
        print(f"{n:>3} {t1:>11.4f} {c1:>12,} {t2:>10.6f} {c2:>9,}"
              f" {t3:>9.6f} {f1:>10,}")

    # --- предел наивной рекурсии ---
    print("\nПредел наивной рекурсии (ориентир 10 с):")
    for n in (34, 36, 38, 40):
        calls = 0
        t = time.perf_counter(); fib_naive(n); dt = time.perf_counter() - t
        print(f"  n={n}: {dt:6.2f} с, вызовов {calls:,}")

    # --- задача Б ---
    print("\nЗадача Б. Размен суммы")
    coins, S = [1, 4, 6, 9], 250
    t = time.perf_counter(); count, ans = coin_dp(coins, S); dt = time.perf_counter() - t
    print(f"  S = {S}, монеты {coins}")
    print(f"  минимум монет: {count}")
    print(f"  состав: {dict(sorted(Counter(ans).items()))}")
    print(f"  проверка суммы: {sum(ans)}, время: {dt:.6f} с")

    # --- сверка с полным перебором ---
    print("\nСверка ДП с полным перебором:")
    print(f"{'S':>4} {'ДП':>5} {'перебор':>8} {'итог':>6}")
    for s in (10, 15, 20, 25, 30):
        a, _ = coin_dp(coins, s)
        b = coin_brute(coins, s)
        print(f"{s:>4} {a:>5} {b:>8} {'OK' if a == b else 'ОШИБКА':>6}")

    # --- Г4: время ДП от S ---
    print("\nГ4. Время ДП в зависимости от S")
    print(f"{'S':>8} {'время, с':>10} {'T(2S)/T(S)':>12}")
    prev = 0
    for s in (50_000, 100_000, 200_000, 400_000):
        times = []
        for _ in range(3):  # берём медиану из трёх замеров
            t = time.perf_counter()
            coin_dp(coins, s, recover=False)
            times.append(time.perf_counter() - t)
        med = sorted(times)[1]
        ratio = f"{med / prev:.2f}" if prev else "—"
        print(f"{s:>8} {med:>10.6f} {ratio:>12}")
        prev = med

    # O(k*S): линейно по значению S, но само S занимает log S бит,
    # поэтому от длины входа зависимость экспоненциальная — псевдополиномиальность.


if __name__ == "__main__":
    main()

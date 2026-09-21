"""
Лабораторная работа № 2. Вариант 11.
Сравнение сортировки пузырьком (с флагом), шейкерной сортировки (М5)
и сортировки вставками на массивах с большим числом повторов (тип D).

Исходные данные: n = 1000, 2000, 3000, 4000; значения из [0; 10];
k = 3 повтора (берётся медиана); дополнительное задание М5.
"""
import random
import statistics
import time

SIZES = [1000, 2000, 3000, 4000]
LO, HI = 0, 10
REPEATS = 3


def generate_data(n, kind="random", lo=0, hi=100_000, seed=42):
    """Генерирует массив длины n заданного типа.

    kind: random | sorted | reversed | nearly_sorted | duplicates
    Для типа "duplicates" (тип D варианта) значения берутся из узкого
    диапазона [lo; hi], поэтому в массиве много одинаковых элементов.
    """
    rng = random.Random(seed + n)      # воспроизводимость эксперимента
    data = [rng.randint(lo, hi) for _ in range(n)]
    if kind == "sorted":
        data.sort()
    elif kind == "reversed":
        data.sort(reverse=True)
    elif kind == "nearly_sorted":
        data.sort()
        for _ in range(max(1, n // 20)):          # 5 % случайных перестановок
            i, j = rng.randrange(n), rng.randrange(n)
            data[i], data[j] = data[j], data[i]
    return data


def measure(sort_func, data, repeats=3):
    """Возвращает медианное время работы sort_func на данных data, с."""
    times = []
    expected = sorted(data)            # эталон считается вне замера
    for _ in range(repeats):
        start = time.perf_counter()
        result = sort_func(data)
        times.append(time.perf_counter() - start)
        assert result == expected, f"{sort_func.__name__}: ошибка сортировки"
    return statistics.median(times)


def bubble_sort(arr):
    """Сортировка пузырьком с флагом досрочного выхода."""
    a = arr.copy()
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def shaker_sort(arr):
    """Шейкерная (двунаправленная) сортировка: проходы вправо и влево."""
    a = arr.copy()
    left, right = 0, len(a) - 1
    while left < right:
        swapped = False
        for j in range(left, right):              # проход вправо: максимум в конец
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        right -= 1
        if not swapped:
            break
        swapped = False
        for j in range(right, left, -1):          # проход влево: минимум в начало
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                swapped = True
        left += 1
        if not swapped:
            break
    return a


def insertion_sort(arr):
    """Сортировка вставками."""
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


# ---- версии со счётчиками (используются ОТДЕЛЬНО от замера времени) ----
def bubble_counts(arr):
    a, n, cmp_, mv = arr.copy(), len(arr), 0, 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            cmp_ += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                mv += 1
                swapped = True
        if not swapped:
            break
    return cmp_, mv


def shaker_counts(arr):
    a, cmp_, mv = arr.copy(), 0, 0
    left, right = 0, len(a) - 1
    while left < right:
        swapped = False
        for j in range(left, right):
            cmp_ += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                mv += 1
                swapped = True
        right -= 1
        if not swapped:
            break
        swapped = False
        for j in range(right, left, -1):
            cmp_ += 1
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                mv += 1
                swapped = True
        left += 1
        if not swapped:
            break
    return cmp_, mv


def insertion_counts(arr):
    a, cmp_, mv = arr.copy(), 0, 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            cmp_ += 1
            if a[j] > key:
                a[j + 1] = a[j]
                mv += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    return cmp_, mv


if __name__ == "__main__":
    import json
    try:
        import importlib

        matplotlib = importlib.import_module("matplotlib")
        matplotlib.use("Agg")
        plt = importlib.import_module("matplotlib.pyplot")
    except ImportError as exc:
        raise RuntimeError(
            "Не найден matplotlib. Установите его командой: "
            "python -m pip install matplotlib"
        ) from exc

    algorithms = {"Пузырьком": bubble_sort,
                    "Шейкерная": shaker_sort,
                    "Вставками": insertion_sort}
    results = {name: [] for name in algorithms}

    print(f"{'n':>6}" + "".join(f"{name:>14}" for name in algorithms))
    for n in SIZES:
        data = generate_data(n, kind="duplicates", lo=LO, hi=HI)
        row = f"{n:>6}"
        for name, func in algorithms.items():
            t = measure(func, data, REPEATS)
            results[name].append(t)
            row += f"{t:>14.4f}"
        print(row)

    # отношения T(2n)/T(n) и T(n)/n^2
    print("\nT(2n)/T(n):")
    for name, ts in results.items():
        print(f"  {name:<10} 1000->2000: {ts[1] / ts[0]:.2f}   2000->4000: {ts[3] / ts[1]:.2f}")
    print("\nT(n)/n^2, x1e-8:")
    for name, ts in results.items():
        print(f"  {name:<10}", [round(t / n ** 2 * 1e8, 2) for t, n in zip(ts, SIZES)])

    # число сравнений и обменов (сдвигов)
    counts = {}
    print("\nСравнения / обмены(сдвиги):")
    for n in SIZES:
        data = generate_data(n, kind="duplicates", lo=LO, hi=HI)
        counts[n] = {"bubble": bubble_counts(data), "shaker": shaker_counts(data),
                        "insertion": insertion_counts(data)}
        print(n, counts[n])

    # график
    for name, ts in results.items():
        plt.plot(SIZES, ts, marker="o", label=name)
    plt.xlabel("Размер массива n")
    plt.ylabel("Время, с")
    plt.title("Зависимость времени сортировки от n (тип D, значения 0…10)")
    plt.grid(True)
    plt.legend()
    plt.savefig("lr2_plot.png", dpi=150)

    json.dump({"sizes": SIZES, "results": results,
                "counts": {str(k): v for k, v in counts.items()}},
                open("results.json", "w"), ensure_ascii=False)
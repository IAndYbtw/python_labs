"""
Лабораторная работа № 11. Вариант 11.

Поиск подстроки: наивный алгоритм и КМП.
Расстояние Левенштейна: полная таблица и Θ(min(n,m)) памяти (Л4).
Сопоставление наименований контрагентов.
"""
import random
import re
import sys
import time


def naive_search(text, pattern):
    """Наивный поиск: (позиции, число сравнений)."""
    n, m = len(text), len(pattern)
    positions, comparisons = [], 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            positions.append(i)
    return positions, comparisons


def prefix_function(pattern):
    """π[i] — наибольший собственный префикс-суффикс P[0..i]."""
    pi = [0] * len(pattern)
    k = 0
    for i in range(1, len(pattern)):
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    return pi


def kmp_search(text, pattern):
    """Алгоритм Кнута — Морриса — Пратта: Θ(n + m)."""
    n, m = len(text), len(pattern)
    pi = prefix_function(pattern)
    positions, comparisons = [], 0
    k = 0
    for i in range(n):
        while k > 0 and text[i] != pattern[k]:
            comparisons += 1
            k = pi[k - 1]
        comparisons += 1
        if text[i] == pattern[k]:
            k += 1
        if k == m:
            positions.append(i - m + 1)
            k = pi[k - 1]
    return positions, comparisons


def levenshtein(a, b):
    """Расстояние Левенштейна, Θ(min(len(a), len(b))) памяти."""
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1,
                         cur[j - 1] + 1,
                         prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]


def levenshtein_full(a, b):
    """Полная таблица (для фрагмента отчёта и замера памяти)."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i - 1][j] + 1,
                          D[i][j - 1] + 1,
                          D[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    return D[n][m], D


def similarity(a, b):
    """Сходство в [0; 1]."""
    if not a and not b:
        return 1.0
    return 1 - levenshtein(a, b) / max(len(a), len(b))


LEGAL_FORMS = {"ооо", "оао", "зао", "пао", "ао", "ип"}


def normalize(name):
    """Нижний регистр, без кавычек/пунктуации и правовых форм."""
    s = name.lower().replace("ё", "е")
    s = re.sub(r"[\"'«»„“”.,()-]", " ", s)
    return " ".join(w for w in s.split() if w not in LEGAL_FORMS)


def match_records(list_a, list_b, threshold=0.8):
    """Сопоставление записей: точное, затем нечёткое."""
    norm_b = [(b, normalize(b)) for b in list_b]
    result = []
    for a in list_a:
        na = normalize(a)
        best, best_sim, kind = None, 0.0, "не найдено"
        for b, nb in norm_b:
            if na == nb:
                best, best_sim, kind = b, 1.0, "точное"
                break
            s = similarity(na, nb)
            if s > best_sim:
                best, best_sim, kind = b, s, "нечёткое"
        if best_sim >= threshold:
            result.append((a, best, best_sim, kind))
        else:
            result.append((a, None, best_sim, "не найдено"))
    return result


def table_memory_kb(table):
    """Память под списки таблицы, КБ (без объектов int)."""
    return (sys.getsizeof(table)
            + sum(sys.getsizeof(row) for row in table)) / 1024


def main():
    print("=" * 78)
    print("ЛР № 11, вариант 11: поиск подстроки, Левенштейн, сопоставление")
    print("=" * 78)

    # --- префикс-функция ---
    pattern = "abbabba"
    print("\nπ для", pattern, ":", prefix_function(pattern))

    # --- поиск на случайном тексте ---
    rng = random.Random(42)
    print("\nСлучайный текст, образец", pattern)
    print(f"{'n':>9}{'наивный, с':>12}{'КМП, с':>10}"
          f"{'сравн. наим.':>15}{'сравн. КМП':>13}{'вхожд.':>9}")
    for n in (100_000, 1_000_000):
        text = "".join(rng.choice("ab") for _ in range(n))
        t = time.perf_counter(); pos1, c1 = naive_search(text, pattern)
        t1 = time.perf_counter() - t
        t = time.perf_counter(); pos2, c2 = kmp_search(text, pattern)
        t2 = time.perf_counter() - t
        assert pos1 == pos2
        print(f"{n:>9}{t1:>12.4f}{t2:>10.4f}{c1:>15,}{c2:>13,}{len(pos1):>9,}")

    # --- худший случай для наивного алгоритма ---
    print("\nХудший случай: текст 'a'*n, образец 'a'*50+'b'")
    print(f"{'n':>9}{'наивный, с':>12}{'КМП, с':>10}"
          f"{'сравн. наим.':>15}{'сравн. КМП':>13}")
    bad_pattern = "a" * 50 + "b"
    for n in (100_000, 1_000_000):
        text = "a" * n
        t = time.perf_counter(); _, c1 = naive_search(text, bad_pattern)
        t1 = time.perf_counter() - t
        t = time.perf_counter(); _, c2 = kmp_search(text, bad_pattern)
        t2 = time.perf_counter() - t
        print(f"{n:>9}{t1:>12.4f}{t2:>10.4f}{c1:>15,}{c2:>13,}")

    # --- Левенштейн: короткие пары ---
    print("\nРасстояние Левенштейна:")
    for a, b in [("кот", "скот"), ("Ромашка", "Ромашки"),
                 ("аналитика", "аналитик"), ("логистик плюс", "логистик плюсс")]:
        d = levenshtein(a, b)
        print(f"  d('{a}', '{b}') = {d}, сходство {similarity(a, b):.3f}")

    # --- Л4: полная таблица против двух строк ---
    print("\nЛ4: полная таблица и Θ(min(n,m)) памяти")
    print(f"{'L':>5}{'полная, с':>12}{'2 строки, с':>13}"
          f"{'полная, КБ':>13}{'2 строки, КБ':>15}")
    rng = random.Random(7)
    for L in (500, 1000, 2000):
        a = "".join(rng.choice("abc") for _ in range(L))
        b = "".join(rng.choice("abc") for _ in range(L))

        t = time.perf_counter(); d1, D = levenshtein_full(a, b)
        t1 = time.perf_counter() - t
        t = time.perf_counter(); d2 = levenshtein(a, b)
        t2 = time.perf_counter() - t
        assert d1 == d2
        mem_full = table_memory_kb(D)
        mem_two = 2 * sys.getsizeof([0] * (L + 1)) / 1024
        print(f"{L:>5}{t1:>12.3f}{t2:>13.3f}{mem_full:>13.1f}{mem_two:>15.1f}")

    # --- сопоставление записей ---
    system_a = ['ООО "Ромашка"', 'АО "Василёк"', "ИП Иванов И.И.",
                'ООО "Северный ветер"', 'ПАО "Гранит"',
                'ООО "Логистик Плюс"', 'ООО "Альфа Трейд"']
    system_b = ["Ромашка, ООО", "ВАСИЛЕК АО", "Иванов Иван Иванович",
                "Северный Ветер ООО", "Гранит-Строй ПАО",
                "Логистик Плюсс", 'ООО "Альфа-Трейд"']

    print("\nСопоставление записей (порог 0,80):")
    print(f"{'Система А':<26}{'Система Б':<26}{'сходство':>10}{'тип':>12}")
    for a, b, s, kind in match_records(system_a, system_b, 0.80):
        target = b if b else "—"
        print(f"{a:<26}{target:<26}{s:>10.3f}{kind:>12}")


if __name__ == "__main__":
    main()

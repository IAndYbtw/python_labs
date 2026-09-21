#hola hola hola
"""
Лабораторная работа № 1. Вариант 11.
Итерационные методы вычисления √a, ∛b, ln c.

Исходные данные: a = 29, b = 70, c = 50, eps = 1e-4,
критерий остановки для корней - по разности соседних приближений (Р),
начальное приближение x0 = 1, дополнительное требование Д3
(нормализация аргумента логарифма c = m * 2^k).
"""
import math  # ТОЛЬКО для эталонных значений

A, B, C = 29, 70, 50
EPS = 1e-4
X0 = 1.0
N_MAX = 100


def sqrt_newton(a, eps=EPS, x0=X0, n_max=N_MAX):
    """Квадратный корень методом Ньютона (формула Герона)."""
    if a < 0:
        raise ValueError("Подкоренное выражение должно быть неотрицательным")
    if a == 0:
        return 0.0, 0
    x = x0
    for n in range(1, n_max + 1):
        x_new = 0.5 * (x + a / x)
        if abs(x_new - x) < eps:          # критерий Р
            return x_new, n
        x = x_new
    raise RuntimeError("Точность не достигнута за N_MAX итераций")


def cbrt_newton(b, eps=EPS, x0=X0, n_max=N_MAX):
    """Кубический корень методом Ньютона (с учётом знака)."""
    if b == 0:
        return 0.0, 0
    sign = -1 if b < 0 else 1
    b = abs(b)
    x = x0
    for n in range(1, n_max + 1):
        x_new = (2 * x + b / (x * x)) / 3
        if abs(x_new - x) < eps:          # критерий Р
            return sign * x_new, n
        x = x_new
    raise RuntimeError("Точность не достигнута за N_MAX итераций")


def ln_series(c, eps=EPS, n_max=10_000):
    """ln c через ряд: ln c = 2(y + y^3/3 + y^5/5 + ...), y=(c-1)/(c+1)."""
    if c <= 0:
        raise ValueError("Аргумент логарифма должен быть положительным")
    y = (c - 1) / (c + 1)
    y2 = y * y
    power = y                              # y^(2k+1)
    total = 0.0
    for k in range(n_max):
        term = 2 * power / (2 * k + 1)
        if abs(term) < eps:
            return total, k
        total += term
        power *= y2
    raise RuntimeError("Точность не достигнута за n_max итераций")


def normalize(c):
    """Представление c = m * 2^k, m in [0.5; 1). Только умножения/деления."""
    k = 0
    m = c
    while m >= 1:
        m /= 2
        k += 1
    while m < 0.5:
        m *= 2
        k -= 1
    return m, k


def ln_normalized(c, eps=EPS):
    """ln c = ln m + k ln 2 (оба логарифма считаются рядом, |y| <= 1/3).
    Точность делим на (|k|+1), чтобы погрешность k*ln2 не превысила eps."""
    if c <= 0:
        raise ValueError("Аргумент логарифма должен быть положительным")
    m, k = normalize(c)
    e = eps / (abs(k) + 1)
    ln_m, n1 = ln_series(m, e)
    ln_2, n2 = ln_series(2.0, e)
    return ln_m + k * ln_2, n1 + n2, (m, k, n1, n2)


def iteration_table(f_step, x0, target, eps):
    """Таблица итераций (для анализа сходимости)."""
    rows, x = [], x0
    for n in range(1, 100):
        x_new = f_step(x)
        rows.append((n, x_new, abs(x_new - x), abs(x_new - target)))
        if abs(x_new - x) < eps:
            break
        x = x_new
    return rows


if __name__ == "__main__":
    ref_sqrt, ref_cbrt, ref_ln = math.sqrt(A), B ** (1 / 3), math.log(C)

    s, ns = sqrt_newton(A)
    cb, nc = cbrt_newton(B)
    l1, nl1 = ln_series(C)
    l2, nl2, info = ln_normalized(C)

    print(f"{'Функция':<14}{'Арг.':>6}{'Результат':>16}{'Эталон':>16}"
            f"{'Погрешность':>14}{'Итер.':>7}")
    for name, arg, val, ref, n in [
        ("sqrt(a)", A, s, ref_sqrt, ns),
        ("cbrt(b)", B, cb, ref_cbrt, nc),
        ("ln c (ряд)", C, l1, ref_ln, nl1),
        ("ln c (норм.)", C, l2, ref_ln, nl2),
    ]:
        print(f"{name:<14}{arg:>6}{val:>16.10f}{ref:>16.10f}"
                f"{abs(val - ref):>14.2e}{n:>7}")
    m, k, n1, n2 = info
    print(f"Нормализация: c = {m} * 2^{k}, членов: ln m -> {n1}, ln 2 -> {n2}")

    print("\nТаблица итераций sqrt(29):")
    for r in iteration_table(lambda x: 0.5 * (x + A / x), X0, ref_sqrt, EPS):
        print("%3d %.10f %.3e %.3e" % r)
    print("\nТаблица итераций cbrt(70):")
    for r in iteration_table(lambda x: (2 * x + B / (x * x)) / 3, X0, ref_cbrt, EPS):
        print("%3d %.10f %.3e %.3e" % r)

    print("\nЗависимость числа итераций от eps:")
    for p in range(1, 11):
        e = 10.0 ** (-p)
        print(p, sqrt_newton(A, e)[1], cbrt_newton(B, e)[1],
                ln_series(C, e)[1], ln_normalized(C, e)[1])
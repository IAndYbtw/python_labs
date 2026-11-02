"""
Лабораторная работа № 6. Вариант 11.
Реализация линейных структур данных и анализ трудоёмкости их операций.

Исходные данные (вариант 11, табл. 1):
  - структуры:        кольцевой буфер (очередь) и список;
  - операции:         постановка (enqueue), извлечение (dequeue), переполнение;
  - размеры n:        5000; 10 000; 20 000;
  - прикладная задача: буфер последних 100 событий.

Дополнительные требования (табл. 2, для всех вариантов):
  - Т1: проверка корректности на малом примере с выводом содержимого;
  - Т2: время операций для собственной реализации и встроенного list;
  - Т3: определить, какой оценке (Theta(1) или Theta(n)) соответствует каждая
        операция (по отношению T(2n)/T(n));
  - Т4: расход памяти на 10 000 элементов через sys.getsizeof.

Программа только печатает результаты в консоль:
без построения графиков (PNG) и без сохранения JSON-файлов.
"""
import sys
import time


# ===========================================================================
# 1. ОДНОСВЯЗНЫЙ СПИСОК
# ===========================================================================

class Node:
    """Узел односвязного списка.

    КАК УСТРОЕН: хранит значение и ссылку на следующий узел.
    __slots__ экономит память, запрещая создавать лишние атрибуты.
    """
    __slots__ = ("value", "next")

    def __init__(self, value, nxt=None):
        self.value = value
        self.next = nxt


class LinkedList:
    """Односвязный список со ссылками на голову и хвост.

    КАК РАБОТАЮТ ОПЕРАЦИИ:
      - вставка/удаление в начале (push_front/pop_front) — Theta(1): просто
        переставляем ссылку head;
      - вставка в конец (push_back) — Theta(1), потому что храним ссылку tail;
      - доступ по индексу (get) и вставка в середину (insert) — Theta(n):
        нужно пройти от начала до нужного узла.
    """

    def __init__(self):
        self.head = None      # первый узел
        self.tail = None      # последний узел (для быстрой вставки в конец)
        self.size = 0         # число элементов

    def push_front(self, value):
        """Вставка в начало — Theta(1)."""
        self.head = Node(value, self.head)     # новый узел ссылается на старую голову
        if self.tail is None:
            self.tail = self.head
        self.size += 1

    def push_back(self, value):
        """Вставка в конец — Theta(1) благодаря ссылке tail."""
        node = Node(value)
        if self.tail is None:                  # список был пуст
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def insert(self, index, value):
        """Вставка по индексу — Theta(n): проход до позиции index-1."""
        if not 0 <= index <= self.size:
            raise IndexError("индекс вне диапазона")
        if index == 0:                         # частный случай = вставка в начало
            self.push_front(value)
            return
        node = self.head
        for _ in range(index - 1):             # идём к узлу ПЕРЕД местом вставки
            node = node.next
        new = Node(value, node.next)           # вставляем между node и node.next
        node.next = new
        if new.next is None:                   # вставили в самый конец
            self.tail = new
        self.size += 1

    def pop_front(self):
        """Удаление из начала — Theta(1)."""
        if self.head is None:
            raise IndexError("список пуст")
        value = self.head.value
        self.head = self.head.next
        if self.head is None:                  # список опустел
            self.tail = None
        self.size -= 1
        return value

    def get(self, index):
        """Доступ по индексу — Theta(n): проход от начала."""
        if not 0 <= index < self.size:
            raise IndexError("индекс вне диапазона")
        node = self.head
        for _ in range(index):
            node = node.next
        return node.value

    def find(self, value):
        """Поиск значения — Theta(n). Возвращает индекс или -1."""
        node = self.head
        i = 0
        while node:
            if node.value == value:
                return i
            node = node.next
            i += 1
        return -1

    def to_list(self):
        """Значения списка в виде обычного list (для вывода)."""
        result, node = [], self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

    def __len__(self):
        return self.size


# ===========================================================================
# 2. КОЛЬЦЕВОЙ БУФЕР (ОЧЕРЕДЬ)
# ===========================================================================

class CircularQueue:
    """Очередь на основе кольцевого буфера фиксированной ёмкости.

    КАК УСТРОЕНА:
      Данные лежат в массиве self.data. Храним индекс head (следующий на
      извлечение) и счётчик count (сколько элементов). Позиция хвоста
      вычисляется как (head + count) % capacity. Когда индекс достигает
      конца массива, он «перепрыгивает» в начало — отсюда название
      «кольцевой».

      Обе операции (постановка и извлечение) — Theta(1): никаких сдвигов
      элементов, в отличие от очереди на обычном списке, где извлечение из
      начала требует сдвига всех элементов за Theta(n).
    """

    def __init__(self, capacity, overwrite=False):
        self.capacity = capacity
        self.data = [None] * capacity
        self.head = 0             # индекс следующего на извлечение
        self.count = 0            # текущее число элементов
        self.overwrite = overwrite  # True -> при переполнении вытесняем старый

    def is_full(self):
        return self.count == self.capacity

    def enqueue(self, value):
        """Постановка в конец — Theta(1).

        КАК РАБОТАЕТ:
          - если буфер полон и overwrite=False -> ОШИБКА переполнения;
          - если буфер полон и overwrite=True -> новый элемент записывается
            на место самого старого (head), а head сдвигается вперёд. Так
            буфер всегда хранит последние capacity элементов.
          - иначе пишем в свободную ячейку хвоста и увеличиваем count.
        """
        if self.is_full():
            if not self.overwrite:
                raise OverflowError("очередь переполнена")
            self.data[self.head] = value        # затираем самый старый
            self.head = (self.head + 1) % self.capacity
            return
        tail = (self.head + self.count) % self.capacity
        self.data[tail] = value
        self.count += 1

    def dequeue(self):
        """Извлечение из начала — Theta(1)."""
        if self.count == 0:
            raise IndexError("очередь пуста")
        value = self.data[self.head]
        self.data[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.count -= 1
        return value

    def to_list(self):
        """Элементы в порядке постановки (FIFO)."""
        return [self.data[(self.head + i) % self.capacity]
                for i in range(self.count)]

    def __len__(self):
        return self.count


# ===========================================================================
# 3. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ЗАМЕРА
# ===========================================================================

def measure(action, repeats=3):
    """Медианное время выполнения action(), с.

    КАК РАБОТАЕТ: повторяем замер repeats раз и берём медиану, чтобы
    случайные всплески загрузки ОС не исказили результат.
    """
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        action()
        times.append(time.perf_counter() - start)
    times.sort()
    return times[len(times) // 2]


# ===========================================================================
# 4. ОСНОВНАЯ ПРОГРАММА
# ===========================================================================

def main():
    print("=" * 78)
    print("ЛР № 6, вариант 11: кольцевой буфер; постановка/извлечение/переполнение")
    print("=" * 78)

    # --- Т1. Проверка корректности на малом примере ---
    print("\n--- Т1. Односвязный список ---")
    lst = LinkedList()
    print("создан пустой список:", lst.to_list(), "длина", len(lst))
    lst.push_back(10);    print("push_back(10)  ->", lst.to_list())
    lst.push_back(25);    print("push_back(25)  ->", lst.to_list())
    lst.push_front(7);    print("push_front(7)  ->", lst.to_list())
    lst.insert(1, 99);    print("insert(1, 99)  ->", lst.to_list())
    lst.pop_front();      print("pop_front()    ->", lst.to_list())
    print("get(2) =", lst.get(2), "| find(10) =", lst.find(10),
          "| find(999) =", lst.find(999))

    print("\n--- Т1. Кольцевой буфер (ёмкость 4) ---")
    q = CircularQueue(4)
    q.enqueue("A");       print("enqueue(A) ->", q.to_list(), "длина", len(q))
    q.enqueue("B");       print("enqueue(B) ->", q.to_list())
    q.enqueue("C");       print("enqueue(C) ->", q.to_list())
    q.dequeue();          print("dequeue()  ->", q.to_list())
    q.enqueue("D");       print("enqueue(D) ->", q.to_list())
    q.enqueue("E");       print("enqueue(E) ->", q.to_list())
    try:
        q.enqueue("F")
    except OverflowError as e:
        print("enqueue(F) -> ОШИБКА:", e, "(буфер полон)")

    print("\n--- Прикладная задача: буфер последних 100 событий ---")
    buf = CircularQueue(100, overwrite=True)   # хранит только последние 100
    for i in range(250):
        buf.enqueue(f"событие-{i}")
    events = buf.to_list()
    print(f"поступило 250 событий, в буфере осталось: {len(events)}")
    print("первые 3:", events[:3])
    print("последние 3:", events[-3:])

    # --- Т2 и Т3. Замер времени операций ---
    SIZES = [5000, 10_000, 20_000]

    print("\n--- Т2. Время постановки и извлечения (с) ---")
    header = (f"{'n':>7} {'кольцо:enqueue':>15} {'list:append':>13} "
              f"{'кольцо:dequeue':>15} {'list:pop(0)':>13} {'список:dequeue':>15}")
    print(header)
    data = {n: {} for n in SIZES}
    for n in SIZES:
        data[n]["ring_enqueue"] = measure(lambda n=n: _fill_ring(n))
        data[n]["list_append"] = measure(lambda n=n: _fill_list(n))
        data[n]["ring_dequeue"] = measure(lambda n=n: _drain_ring(n))
        data[n]["list_pop0"] = measure(lambda n=n: _drain_list(n))
        data[n]["linked_dequeue"] = measure(lambda n=n: _drain_linked(n))

    for n in SIZES:
        d = data[n]
        print(f"{n:>7} {d['ring_enqueue']:>15.5f} {d['list_append']:>13.5f} "
              f"{d['ring_dequeue']:>15.5f} {d['list_pop0']:>13.5f} "
              f"{d['linked_dequeue']:>15.5f}")

    print("\n--- Т3. Отношение T(2n)/T(n) и соответствие оценке ---")

    ops = [
        ("кольцо: enqueue", "ring_enqueue", "Theta(n) суммарно, Theta(1) на операцию"),
        ("list: append", "list_append", "Theta(n) амортизированно"),
        ("кольцо: dequeue", "ring_dequeue", "Theta(n) суммарно, Theta(1) на операцию"),
        ("list: pop(0)", "list_pop0", "Theta(n^2): каждый pop(0) сдвигает массив"),
        ("связн. список: dequeue", "linked_dequeue", "Theta(n): push_back и pop_front по Theta(1)"),
    ]
    print(f"{'операция':<24}{'T(10k)/T(5k)':>14}{'T(20k)/T(10k)':>15}{'соответствие':>14}")
    for label, key, note in ops:
        r1 = data[10_000][key] / data[5_000][key]
        r2 = data[20_000][key] / data[10_000][key]
        print(f"{label:<24}{r1:>14.2f}{r2:>15.2f}{'':>14}")
        print(f"{'':<24}{'':>14}{'':>15}{note}")

    # --- переполнение ---
    print("\n--- Переполнение: обработка n событий буфером ёмкости 100 ---")
    print(f"{'n':>7} {'кольцо:overwrite':>19} {'list:последние 100':>20}")
    for n in SIZES:
        def ring_overwrite():
            q = CircularQueue(100, overwrite=True)
            for i in range(n):
                q.enqueue(i)

        def list_last100():
            s = []
            for i in range(n):
                s.append(i)
                if len(s) > 100:
                    s.pop(0)

        print(f"{n:>7} {measure(ring_overwrite):>19.5f} {measure(list_last100):>20.5f}")

    # --- Т4. Память ---
    print("\n--- Т4. Расход памяти на 10 000 элементов ---")
    n = 10_000
    values = list(range(1000, 1000 + n))      # различные int (> 256, не кэшируются)
    ints_bytes = sum(sys.getsizeof(v) for v in values)

    arr_bytes = sys.getsizeof(values)         # сам массив указателей

    ll = LinkedList()
    for v in values:
        ll.push_back(v)
    node = ll.head
    nodes_bytes = 0
    while node:
        nodes_bytes += sys.getsizeof(node)
        node = node.next

    q = CircularQueue(n)
    for v in values:
        q.enqueue(v)
    buf_bytes = sys.getsizeof(q.data)

    print(f"объекты int (общие для всех): {ints_bytes:,} байт")
    print(f"встроенный list:   массив указателей {arr_bytes:,} + int "
          f"-> итого {arr_bytes + ints_bytes:,} байт")
    print(f"односвязный список: {nodes_bytes:,} (узлы) + int "
          f"-> итого {nodes_bytes + ints_bytes:,} байт")
    print(f"кольцевой буфер:   массив {buf_bytes:,} + int "
          f"-> итого {buf_bytes + ints_bytes:,} байт")
    print(f"размер одного узла Node: {sys.getsizeof(Node(0))} байт; "
          f"на элемент списка {nodes_bytes // n} байт против "
          f"{arr_bytes // n} байт у массива")


# --- короткие замыкаемые действия для замера (обёртки-функции) ---
def _fill_ring(n):
    q = CircularQueue(n)
    for i in range(n):
        q.enqueue(i)


def _fill_list(n):
    s = []
    for i in range(n):
        s.append(i)


def _drain_ring(n):
    q = CircularQueue(n)
    for i in range(n):
        q.enqueue(i)
    for i in range(n):
        q.dequeue()


def _drain_list(n):
    s = list(range(n))
    for i in range(n):
        s.pop(0)


def _drain_linked(n):
    s = LinkedList()
    for i in range(n):
        s.push_back(i)
    for i in range(n):
        s.pop_front()


if __name__ == "__main__":
    main()

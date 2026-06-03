# Лабораторная работа №1 по дисциплине ЛОИС
# Автор: Морозов Артем
# Вариант 9: построение СДНФ формулы логики высказываний

# ============================================================
# Вычислитель: считает значение дерева при заданных значениях
# переменных + извлекает список переменных из дерева
# ============================================================


def get_variables(tree) -> list:
    """Собирает все уникальные переменные из дерева, сортирует по алфавиту."""
    variables = set()

    def walk(node):
        if node[0] == "var":
            variables.add(node[1])
        elif node[0] == "const":
            return
        elif node[0] == "not":
            walk(node[1])
        else:  # бинарные: and, or, impl, equiv
            walk(node[1])
            walk(node[2])

    walk(tree)
    return sorted(variables)


def evaluate(tree, values: dict) -> int:
    """
    Вычисляет значение дерева при заданных значениях переменных.

    tree   — дерево разбора (кортеж)
    values — словарь {имя_переменной: 0 или 1}
    """
    op = tree[0]

    if op == "var":
        return values[tree[1]]
    elif op == "const":
        return tree[1]
    elif op == "not":
        return 1 - evaluate(tree[1], values)
    elif op == "and":
        return evaluate(tree[1], values) & evaluate(tree[2], values)
    elif op == "or":
        return evaluate(tree[1], values) | evaluate(tree[2], values)
    elif op == "impl":
        a = evaluate(tree[1], values)
        b = evaluate(tree[2], values)
        return 0 if (a == 1 and b == 0) else 1
    elif op == "equiv":
        a = evaluate(tree[1], values)
        b = evaluate(tree[2], values)
        return 1 if a == b else 0
    else:
        raise ValueError(f"Неизвестная операция: {op}")


def truth_table(tree, variables: list) -> list:
    """
    Строит полную таблицу истинности.

    Возвращает список кортежей (values_dict, result)
    для всех 2^n комбинаций.
    """
    n = len(variables)
    table = []
    for mask in range(2 ** n):
        values = {}
        for j, var in enumerate(variables):
            values[var] = (mask >> (n - 1 - j)) & 1
        result = evaluate(tree, values)
        table.append((values, result))
    return table

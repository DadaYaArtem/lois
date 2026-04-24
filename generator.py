# ============================================================
# Генератор случайных формул для режима тестирования
# ============================================================

import random


def _random_tree(variables: list, depth: int = 0, max_depth: int = 3):
    """Рекурсивно строит случайное дерево формулы."""
    # На максимальной глубине или с вероятностью — возвращаем переменную
    if depth >= max_depth or (depth > 0 and random.random() < 0.3):
        var = random.choice(variables)
        # Иногда добавляем отрицание
        if random.random() < 0.3:
            return ("not", ("var", var))
        return ("var", var)

    # Выбираем случайную бинарную операцию
    op = random.choice(["and", "or", "impl", "equiv"])
    left = _random_tree(variables, depth + 1, max_depth)
    right = _random_tree(variables, depth + 1, max_depth)
    return (op, left, right)


def tree_to_string(tree) -> str:
    """Преобразует дерево обратно в строку формулы."""
    op = tree[0]

    if op == "var":
        return tree[1]
    elif op == "not":
        inner = tree_to_string(tree[1])
        if tree[1][0] == "var":
            return f"!{inner}"
        return f"!({inner})"
    else:
        left = tree_to_string(tree[1])
        right = tree_to_string(tree[2])

        op_str = {
            "and": "/\\",
            "or": "\\/",
            "impl": "->",
            "equiv": "~",
        }[op]

        return f"({left}{op_str}{right})"


def generate_formula(num_vars: int = 2, max_depth: int = 2) -> str:
    """
    Генерирует случайную формулу.

    num_vars  — количество переменных (2 или 3)
    max_depth — максимальная глубина дерева
    """
    all_vars = list("PQRS")
    variables = all_vars[:num_vars]
    tree = _random_tree(variables, depth=0, max_depth=max_depth)
    return tree_to_string(tree)


def generate_formula_for_test(difficulty: int = 1) -> str:
    """
    Генерирует формулу заданной сложности для тестирования.

    difficulty:
        1 — лёгкая (2 переменные, глубина 1-2)
        2 — средняя (2-3 переменные, глубина 2)
        3 — сложная (3 переменные, глубина 2-3)
    """
    if difficulty == 1:
        return generate_formula(num_vars=2, max_depth=2)
    elif difficulty == 2:
        num_vars = random.choice([2, 3])
        return generate_formula(num_vars=num_vars, max_depth=2)
    else:
        return generate_formula(num_vars=3, max_depth=3)

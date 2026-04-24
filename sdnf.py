# ============================================================
# Построение СДНФ (совершенной дизъюнктивной нормальной формы)
# ============================================================

from parser import parse
from evaluator import get_variables, evaluate, truth_table


def build_sdnf(formula: str) -> str:
    """
    Главная функция: строка с формулой -> строка с СДНФ.

    Алгоритм:
    1. Парсим формулу в дерево
    2. Извлекаем переменные
    3. Строим таблицу истинности
    4. Для строк с результатом 1 — строим конституенты
    5. Соединяем конституенты через \\/
    """
    tree = parse(formula)
    variables = get_variables(tree)
    table = truth_table(tree, variables)

    # Собираем конституенты единицы
    constituents = []
    for values, result in table:
        if result == 1:
            literals = []
            for var in variables:
                if values[var] == 1:
                    literals.append(var)
                else:
                    literals.append("!" + var)
            constituents.append(literals)

    # Собираем СДНФ в строку
    if not constituents:
        return ""  # противоречие — СДНФ не существует

    if len(constituents) == 1:
        c = constituents[0]
        if len(c) == 1:
            return f"({c[0]})"
        return "(" + "/\\".join(c) + ")"

    parts = []
    for c in constituents:
        if len(c) == 1:
            parts.append(f"({c[0]})")
        else:
            parts.append("(" + "/\\".join(c) + ")")

    return "(" + "\\/".join(parts) + ")"


def build_sdnf_detailed(formula: str) -> dict:
    """
    Расширенная версия: возвращает словарь с промежуточными шагами.

    Ключи:
        formula      — исходная формула
        variables    — список переменных
        truth_table  — таблица истинности [(values, result), ...]
        constituents — список конституент единицы
        sdnf         — итоговая СДНФ-строка
    """
    tree = parse(formula)
    variables = get_variables(tree)
    table = truth_table(tree, variables)

    constituents = []
    for values, result in table:
        if result == 1:
            literals = []
            for var in variables:
                if values[var] == 1:
                    literals.append(var)
                else:
                    literals.append("!" + var)
            constituents.append(literals)

    # Собираем строку
    if not constituents:
        sdnf_str = ""
    elif len(constituents) == 1:
        c = constituents[0]
        if len(c) == 1:
            sdnf_str = f"({c[0]})"
        else:
            sdnf_str = "(" + "/\\".join(c) + ")"
    else:
        parts = []
        for c in constituents:
            if len(c) == 1:
                parts.append(f"({c[0]})")
            else:
                parts.append("(" + "/\\".join(c) + ")")
        sdnf_str = "(" + "\\/".join(parts) + ")"

    return {
        "formula": formula,
        "variables": variables,
        "truth_table": table,
        "constituents": constituents,
        "sdnf": sdnf_str,
    }

# Лабораторная работа №1 по дисциплине ЛОИС
# Автор: Морозов Артем
# Вариант 9: построение СДНФ формулы логики высказываний

# ============================================================
# Построение СДНФ (совершенной дизъюнктивной нормальной формы)
# ============================================================

from parser import parse
from evaluator import get_variables, evaluate, truth_table


def _format_literal(literal: str) -> str:
    return f"({literal})" if literal.startswith("!") else literal


def _format_constituent(constituent: list) -> str:
    if len(constituent) == 1:
        return _format_literal(constituent[0])
    result = "(" + _format_literal(constituent[0]) + "/\\" + _format_literal(constituent[1]) + ")"
    for lit in constituent[2:]:
        result = "(" + result + "/\\" + _format_literal(lit) + ")"
    return result


def _build_sdnf_string(constituents: list) -> str:
    if not constituents:
        return ""
    parts = [_format_constituent(c) for c in constituents]
    if len(parts) == 1:
        return parts[0]
    result = "(" + parts[0] + "\\/" + parts[1] + ")"
    for p in parts[2:]:
        result = "(" + result + "\\/" + p + ")"
    return result


def _collect_constituents(table, variables):
    constituents = []
    for values, result in table:
        if result == 1:
            literals = [var if values[var] == 1 else "!" + var for var in variables]
            constituents.append(literals)
    return constituents


def build_sdnf(formula: str) -> str:
    tree = parse(formula)
    variables = get_variables(tree)
    table = truth_table(tree, variables)
    if not variables:
        return "1" if table[0][1] == 1 else ""
    constituents = _collect_constituents(table, variables)
    return _build_sdnf_string(constituents)


def build_sdnf_detailed(formula: str) -> dict:
    tree = parse(formula)
    variables = get_variables(tree)
    table = truth_table(tree, variables)
    if not variables:
        sdnf_str = "1" if table[0][1] == 1 else ""
        return {
            "formula": formula,
            "variables": variables,
            "truth_table": table,
            "constituents": [[]] if table[0][1] == 1 else [],
            "sdnf": sdnf_str,
        }
    constituents = _collect_constituents(table, variables)
    return {
        "formula": formula,
        "variables": variables,
        "truth_table": table,
        "constituents": constituents,
        "sdnf": _build_sdnf_string(constituents),
    }

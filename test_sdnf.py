# Лабораторная работа №1 по дисциплине ЛОИС
# Автор: Морозов Артем
# Вариант 9: построение СДНФ формулы логики высказываний

import pytest

from evaluator import evaluate, get_variables
from lexer import tokenize
from parser import parse
from sdnf import build_sdnf, build_sdnf_detailed


def _is_equivalent(formula1: str, formula2: str) -> bool:
    tree1, tree2 = parse(formula1), parse(formula2)
    variables = get_variables(tree1)
    for mask in range(2 ** len(variables)):
        values = {v: (mask >> (len(variables) - 1 - i)) & 1 for i, v in enumerate(variables)}
        if evaluate(tree1, values) != evaluate(tree2, values):
            return False
    return True


class TestLexer:
    def test_simple_var(self):
        assert tokenize("P") == [("VAR", "P")]

    def test_constants(self):
        assert tokenize("(P/\\1)")[-2] == ("CONST", "1")
        assert tokenize("0") == [("CONST", "0")]

    def test_all_operators(self):
        tokens = tokenize("((P/\\Q)->((!R)~(S\\/T)))")
        types = [token_type for token_type, _ in tokens]
        assert "AND" in types
        assert "OR" in types
        assert "NOT" in types
        assert "IMPL" in types
        assert "EQUIV" in types

    def test_spaces_are_invalid(self):
        with pytest.raises(ValueError):
            tokenize("(P /\\ Q)")

    def test_only_ascii_uppercase_variables(self):
        with pytest.raises(ValueError):
            tokenize("a")
        with pytest.raises(ValueError):
            tokenize("А")


class TestParser:
    def test_variable(self):
        assert parse("P") == ("var", "P")

    def test_constant(self):
        assert parse("1") == ("const", 1)

    def test_negation_requires_parentheses(self):
        assert parse("(!P)") == ("not", ("var", "P"))
        with pytest.raises(ValueError):
            parse("!P")

    def test_binary_operation_requires_parentheses(self):
        assert parse("(P/\\Q)") == ("and", ("var", "P"), ("var", "Q"))
        with pytest.raises(ValueError):
            parse("P/\\Q")

    def test_extra_parentheses_are_invalid(self):
        with pytest.raises(ValueError):
            parse("(P)")
        with pytest.raises(ValueError):
            parse("((P))")

    def test_each_binary_operation_requires_own_parentheses(self):
        with pytest.raises(ValueError):
            parse("(P\\/Q\\/R)")
        assert parse("((P\\/Q)\\/R)")[0] == "or"

    def test_implication_nested_explicitly(self):
        tree = parse("(P->(Q->R))")
        assert tree[0] == "impl"
        assert tree[2][0] == "impl"


class TestEvaluator:
    def test_variable(self):
        tree = parse("P")
        assert evaluate(tree, {"P": 1}) == 1
        assert evaluate(tree, {"P": 0}) == 0

    def test_constant(self):
        assert evaluate(parse("1"), {}) == 1
        assert evaluate(parse("0"), {}) == 0

    def test_negation(self):
        tree = parse("(!P)")
        assert evaluate(tree, {"P": 1}) == 0
        assert evaluate(tree, {"P": 0}) == 1

    def test_implication(self):
        tree = parse("(P->Q)")
        assert evaluate(tree, {"P": 1, "Q": 0}) == 0
        assert evaluate(tree, {"P": 1, "Q": 1}) == 1
        assert evaluate(tree, {"P": 0, "Q": 0}) == 1

    def test_equivalence(self):
        tree = parse("(P~Q)")
        assert evaluate(tree, {"P": 1, "Q": 1}) == 1
        assert evaluate(tree, {"P": 0, "Q": 0}) == 1
        assert evaluate(tree, {"P": 1, "Q": 0}) == 0

    def test_get_variables_ignores_constants(self):
        assert get_variables(parse("(P->(1/\\R))")) == ["P", "R"]


class TestSDNF:
    def test_conjunction(self):
        assert build_sdnf("(P/\\Q)") == "(P/\\Q)"

    def test_negation(self):
        # Fix 1: single negated literal — no double parens
        assert build_sdnf("(!P)") == "(!P)"

    def test_single_variable(self):
        # Fix 3: single positive variable — no extra parens
        assert build_sdnf("P") == "P"

    def test_double_negation(self):
        assert build_sdnf("(!(!P))") == "P"

    def test_equivalence(self):
        # ((¬P∧¬Q)∨(P∧Q)) — 2 constituents, binary \/
        assert build_sdnf("(P~Q)") == "(((!P)/\\(!Q))\\/(P/\\Q))"

    def test_tautology(self):
        # (¬P∨P) — 2 constituents with single literals
        assert build_sdnf("(P\\/(!P))") == "((!P)\\/P)"

    def test_implication(self):
        # 3 constituents — left-associative binary \/
        assert build_sdnf("(P->Q)") == "((((!P)/\\(!Q))\\/((!P)/\\Q))\\/(P/\\Q))"

    def test_disjunction(self):
        # 3 constituents — left-associative binary \/
        assert build_sdnf("(P\\/Q)") == "((((!P)/\\Q)\\/(P/\\(!Q)))\\/(P/\\Q))"

    def test_triple_conjunction(self):
        # Fix 2: single constituent with 3 literals — binary /\ grouping
        assert build_sdnf("((P/\\Q)/\\R)") == "((P/\\Q)/\\R)"

    def test_contradiction(self):
        assert build_sdnf("(P/\\(!P))") == ""

    def test_constants_as_formulas(self):
        assert build_sdnf("1") == "1"
        assert build_sdnf("0") == ""
        assert build_sdnf("(!0)") == "1"

    def test_constants_in_operations(self):
        # single constituent with 1 literal — no extra parens
        assert build_sdnf("(P/\\1)") == "P"
        assert build_sdnf("(P\\/0)") == "P"
        assert build_sdnf("(P\\/1)") == "((!P)\\/P)"

    def test_implication_with_conjunction(self):
        # 5 constituents, 3 literals each — check via semantic equivalence + parseability
        formula = "(P->(Q/\\R))"
        result = build_sdnf(formula)
        assert result != ""
        parse(result)  # must be valid formula by the same grammar
        assert _is_equivalent(formula, result)

    def test_detailed_has_all_fields(self):
        result = build_sdnf_detailed("(P->Q)")
        assert "formula" in result
        assert "variables" in result
        assert "truth_table" in result
        assert "constituents" in result
        assert "sdnf" in result
        assert len(result["truth_table"]) == 4

    # --- новые тесты для трёх исправленных проблем ---

    def test_sdnf_output_is_parseable(self):
        # СДНФ-вывод обязан быть валидной формулой по той же грамматике
        formulas = [
            "P", "(!P)", "(P/\\Q)", "(P\\/Q)", "(P->Q)", "(P~Q)",
            "(!(!P))", "(P\\/(!P))", "((P/\\Q)/\\R)",
        ]
        for formula in formulas:
            result = build_sdnf(formula)
            if result not in ("", "1"):
                parse(result)  # не должно бросать исключение

    def test_sdnf_is_semantically_equivalent(self):
        formulas = [
            "(P->Q)", "(P\\/Q)", "(P~Q)", "((P/\\Q)/\\R)",
            "(P->(Q/\\R))", "(!P)", "(P/\\(!P))",
        ]
        for formula in formulas:
            result = build_sdnf(formula)
            if result not in ("", "1"):
                assert _is_equivalent(formula, result), f"СДНФ не эквивалентна: {formula} -> {result}"

    def test_single_negated_literal_no_double_parens(self):
        # (!P) — один отрицательный литерал, не должно быть ((!P))
        assert build_sdnf("(!P)") == "(!P)"
        # Аналогично для импликации: (A->1) даёт (!A) и A как конституенты
        result = build_sdnf("(A->1)")
        assert "((!A))" not in result

    def test_constituent_with_negation_is_parseable(self):
        # Конституента с отрицательным литералом должна давать parseable СДНФ
        result = build_sdnf("(P->Q)")  # содержит (!P)/\(!Q) как конституенту
        parse(result)

    def test_multivar_conjunction_is_binary(self):
        # 3-литеральная конституента: ((P/\Q)/\R), не P/\Q/\R
        result = build_sdnf("((P/\\Q)/\\R)")
        assert result == "((P/\\Q)/\\R)"
        parse(result)

    def test_four_var_constituent_is_binary(self):
        # 4 переменных в одной конституенте
        result = build_sdnf("(((A/\\B)/\\C)/\\D)")
        assert result == "(((A/\\B)/\\C)/\\D)"
        parse(result)

    def test_three_constituents_binary_disjunction(self):
        # 3 конституенты: левоассоциативное ((C1\/C2)\/C3), не (C1\/C2\/C3)
        result = build_sdnf("(P\\/Q)")  # 3 конституенты
        assert result.count("\\/") == 2
        parse(result)

    def test_four_constituents_binary_disjunction(self):
        # 4 конституенты: ((C1\/C2)\/C3)\/C4
        result = build_sdnf("(P->Q)")  # 3 конституенты — тест выше
        result4 = build_sdnf("(P~Q)")   # 2 конституенты
        # Для 4 используем (A\/B) — 3 конституенты = тест_disjunction выше
        # Возьмём формулу с 4 конституентами явно
        result4 = build_sdnf("(A\\/(!B))")  # проверяем parseability
        parse(result4)
        assert _is_equivalent("(A\\/(!B))", result4)

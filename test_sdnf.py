# Лабораторная работа №1 по дисциплине ЛОИС
# Автор: Морозов Артем
# Вариант 9: построение СДНФ формулы логики высказываний

import pytest

from evaluator import evaluate, get_variables
from lexer import tokenize
from parser import parse
from sdnf import build_sdnf, build_sdnf_detailed


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
    def test_implication(self):
        assert build_sdnf("(P->Q)") == "((!P/\\!Q)\\/(!P/\\Q)\\/(P/\\Q))"

    def test_conjunction(self):
        assert build_sdnf("(P/\\Q)") == "(P/\\Q)"

    def test_disjunction(self):
        assert build_sdnf("(P\\/Q)") == "((!P/\\Q)\\/(P/\\!Q)\\/(P/\\Q))"

    def test_equivalence(self):
        assert build_sdnf("(P~Q)") == "((!P/\\!Q)\\/(P/\\Q))"

    def test_negation(self):
        assert build_sdnf("(!P)") == "(!P)"

    def test_triple_conjunction(self):
        assert build_sdnf("((P/\\Q)/\\R)") == "(P/\\Q/\\R)"

    def test_implication_with_conjunction(self):
        expected = "((!P/\\!Q/\\!R)\\/(!P/\\!Q/\\R)\\/(!P/\\Q/\\!R)\\/(!P/\\Q/\\R)\\/(P/\\Q/\\R))"
        assert build_sdnf("(P->(Q/\\R))") == expected

    def test_tautology(self):
        assert build_sdnf("(P\\/(!P))") == "((!P)\\/(P))"

    def test_contradiction(self):
        assert build_sdnf("(P/\\(!P))") == ""

    def test_single_variable(self):
        assert build_sdnf("P") == "(P)"

    def test_double_negation(self):
        assert build_sdnf("(!(!P))") == "(P)"

    def test_constants_as_formulas(self):
        assert build_sdnf("1") == "1"
        assert build_sdnf("0") == ""
        assert build_sdnf("(!0)") == "1"

    def test_constants_in_operations(self):
        assert build_sdnf("(P/\\1)") == "(P)"
        assert build_sdnf("(P\\/0)") == "(P)"
        assert build_sdnf("(P\\/1)") == "((!P)\\/(P))"

    def test_detailed_has_all_fields(self):
        result = build_sdnf_detailed("(P->Q)")
        assert "formula" in result
        assert "variables" in result
        assert "truth_table" in result
        assert "constituents" in result
        assert "sdnf" in result
        assert len(result["truth_table"]) == 4

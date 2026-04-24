import pytest
from sdnf import build_sdnf, build_sdnf_detailed
from generator import generate_formula_for_test
from test_mode import _normalize_sdnf, _check_answer
from lexer import tokenize
from parser import parse
from evaluator import get_variables, evaluate


# ==================== Тесты лексера ====================

class TestLexer:
    def test_simple_vars(self):
        tokens = tokenize("P")
        assert tokens == [("VAR", "P")]

    def test_conjunction(self):
        tokens = tokenize("(P/\\Q)")
        assert len(tokens) == 5
        assert tokens[2] == ("AND", "/\\")

    def test_all_operators(self):
        tokens = tokenize("(P/\\Q)\\/(!R)->(S~T)")
        types = [t[0] for t in tokens]
        assert "AND" in types
        assert "OR" in types
        assert "NOT" in types
        assert "IMPL" in types
        assert "EQUIV" in types

    def test_invalid_char(self):
        with pytest.raises(ValueError):
            tokenize("P & Q")


# ==================== Тесты парсера ====================

class TestParser:
    def test_variable(self):
        tree = parse("P")
        assert tree == ("var", "P")

    def test_negation(self):
        tree = parse("!P")
        assert tree == ("not", ("var", "P"))

    def test_conjunction(self):
        tree = parse("(P/\\Q)")
        assert tree == ("and", ("var", "P"), ("var", "Q"))

    def test_priority(self):
        # /\\ сильнее \\/, поэтому P\\/Q/\\R = P\\/(Q/\\R)
        tree = parse("P\\/Q/\\R")
        assert tree[0] == "or"
        assert tree[2][0] == "and"

    def test_implication_right_assoc(self):
        # P->Q->R = P->(Q->R)
        tree = parse("P->Q->R")
        assert tree[0] == "impl"
        assert tree[2][0] == "impl"

    def test_unbalanced_parens(self):
        with pytest.raises(ValueError):
            parse("(P/\\Q")


# ==================== Тесты вычислителя ====================

class TestEvaluator:
    def test_variable(self):
        tree = parse("P")
        assert evaluate(tree, {"P": 1}) == 1
        assert evaluate(tree, {"P": 0}) == 0

    def test_negation(self):
        tree = parse("!P")
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

    def test_get_variables(self):
        tree = parse("(P->(Q/\\R))")
        vars = get_variables(tree)
        assert vars == ["P", "Q", "R"]


# ==================== Тесты СДНФ ====================

class TestSDNF:
    def test_implication(self):
        result = build_sdnf("(P->Q)")
        assert result == "((!P/\\!Q)\\/(!P/\\Q)\\/(P/\\Q))"

    def test_conjunction(self):
        result = build_sdnf("(P/\\Q)")
        assert result == "(P/\\Q)"

    def test_disjunction(self):
        result = build_sdnf("(P\\/Q)")
        assert result == "((!P/\\Q)\\/(P/\\!Q)\\/(P/\\Q))"

    def test_equivalence(self):
        result = build_sdnf("(P~Q)")
        assert result == "((!P/\\!Q)\\/(P/\\Q))"

    def test_negation(self):
        result = build_sdnf("(!P)")
        assert result == "(!P)"

    def test_triple_conjunction(self):
        result = build_sdnf("((P/\\Q)/\\R)")
        assert result == "(P/\\Q/\\R)"

    def test_implication_with_conjunction(self):
        result = build_sdnf("(P->(Q/\\R))")
        expected = "((!P/\\!Q/\\!R)\\/(!P/\\!Q/\\R)\\/(!P/\\Q/\\!R)\\/(!P/\\Q/\\R)\\/(P/\\Q/\\R))"
        assert result == expected

    def test_tautology(self):
        result = build_sdnf("(P\\/(!P))")
        assert result == "((!P)\\/(P))"

    def test_contradiction(self):
        result = build_sdnf("(P/\\(!P))")
        assert result == ""

    def test_single_variable(self):
        result = build_sdnf("P")
        assert result == "(P)"

    def test_double_negation(self):
        result = build_sdnf("(!(!P))")
        assert result == "(P)"

    def test_detailed_has_all_fields(self):
        result = build_sdnf_detailed("(P->Q)")
        assert "formula" in result
        assert "variables" in result
        assert "truth_table" in result
        assert "constituents" in result
        assert "sdnf" in result
        assert len(result["truth_table"]) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

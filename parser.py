# ============================================================
# Парсер: строит дерево разбора (AST) из списка токенов
#
# Грамматика (от низшего приоритета к высшему):
#   expr     -> equiv
#   equiv    -> impl ('~' impl)*
#   impl     -> or_expr ('->' impl)?       правоассоциативная
#   or_expr  -> and_expr ('\\/' and_expr)*
#   and_expr -> unary ('/\\' unary)*
#   unary    -> '!' unary | atom
#   atom     -> VAR | '(' expr ')'
# ============================================================

from lexer import (
    tokenize,
    TOK_VAR, TOK_NOT, TOK_AND, TOK_OR,
    TOK_IMPL, TOK_EQUIV, TOK_LPAREN, TOK_RPAREN,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        tok = self.peek()
        if tok is None:
            raise ValueError("Неожиданный конец формулы")
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Ожидался {expected_type}, получен {tok[0]}")
        self.pos += 1
        return tok

    def parse(self):
        tree = self.expr()
        if self.pos != len(self.tokens):
            raise ValueError(
                f"Лишние токены после формулы: {self.tokens[self.pos:]}"
            )
        return tree

    def expr(self):
        return self.equiv()

    def equiv(self):
        left = self.impl()
        while self.peek() and self.peek()[0] == TOK_EQUIV:
            self.consume()
            right = self.impl()
            left = ("equiv", left, right)
        return left

    def impl(self):
        left = self.or_expr()
        if self.peek() and self.peek()[0] == TOK_IMPL:
            self.consume()
            right = self.impl()  # правоассоциативная
            left = ("impl", left, right)
        return left

    def or_expr(self):
        left = self.and_expr()
        while self.peek() and self.peek()[0] == TOK_OR:
            self.consume()
            right = self.and_expr()
            left = ("or", left, right)
        return left

    def and_expr(self):
        left = self.unary()
        while self.peek() and self.peek()[0] == TOK_AND:
            self.consume()
            right = self.unary()
            left = ("and", left, right)
        return left

    def unary(self):
        if self.peek() and self.peek()[0] == TOK_NOT:
            self.consume()
            operand = self.unary()
            return ("not", operand)
        return self.atom()

    def atom(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Неожиданный конец формулы")
        if tok[0] == TOK_VAR:
            self.consume()
            return ("var", tok[1])
        if tok[0] == TOK_LPAREN:
            self.consume()
            node = self.expr()
            self.consume(TOK_RPAREN)
            return node
        raise ValueError(f"Неожиданный токен: {tok}")


def parse(formula: str):
    """Строка -> дерево разбора"""
    tokens = tokenize(formula)
    p = Parser(tokens)
    return p.parse()

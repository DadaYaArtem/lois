from lexer import (
    tokenize,
    TOK_AND,
    TOK_CONST,
    TOK_EQUIV,
    TOK_IMPL,
    TOK_LPAREN,
    TOK_NOT,
    TOK_OR,
    TOK_RPAREN,
    TOK_VAR,
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
            raise ValueError("Unexpected end of formula")
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok[0]}")
        self.pos += 1
        return tok

    def parse(self):
        tree = self.formula()
        if self.pos != len(self.tokens):
            raise ValueError(f"Extra tokens after formula: {self.tokens[self.pos:]}")
        return tree

    def formula(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of formula")

        if tok[0] == TOK_VAR:
            self.consume()
            return ("var", tok[1])

        if tok[0] == TOK_CONST:
            self.consume()
            return ("const", int(tok[1]))

        if tok[0] == TOK_LPAREN:
            return self.parenthesized_formula()

        raise ValueError(f"Unexpected token: {tok}")

    def parenthesized_formula(self):
        self.consume(TOK_LPAREN)

        if self.peek() and self.peek()[0] == TOK_NOT:
            self.consume(TOK_NOT)
            operand = self.formula()
            self.consume(TOK_RPAREN)
            return ("not", operand)

        left = self.formula()
        op = self.consume_binary_operator()
        right = self.formula()
        self.consume(TOK_RPAREN)
        return (op, left, right)

    def consume_binary_operator(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Expected binary operator")

        op_map = {
            TOK_AND: "and",
            TOK_OR: "or",
            TOK_IMPL: "impl",
            TOK_EQUIV: "equiv",
        }
        if tok[0] not in op_map:
            raise ValueError(f"Expected binary operator, got {tok[0]}")

        self.consume()
        return op_map[tok[0]]


def parse(formula: str):
    tokens = tokenize(formula)
    parser = Parser(tokens)
    return parser.parse()

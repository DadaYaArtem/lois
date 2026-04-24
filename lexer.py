# ============================================================
# Лексер: разбивает строку формулы на токены
# ============================================================

# Типы токенов
TOK_VAR = "VAR"
TOK_NOT = "NOT"
TOK_AND = "AND"
TOK_OR = "OR"
TOK_IMPL = "IMPL"
TOK_EQUIV = "EQUIV"
TOK_LPAREN = "LPAREN"
TOK_RPAREN = "RPAREN"


def tokenize(formula: str) -> list:
    """
    Разбивает строку на список токенов [(тип, значение), ...]

    Операторы: /\\ (и), \\/ (или), ! (не), -> (импл.), ~ (экв.)
    Переменные: A-Z
    """
    tokens = []
    i = 0
    while i < len(formula):
        ch = formula[i]

        if ch == ' ':
            i += 1
            continue
        elif ch == '(':
            tokens.append((TOK_LPAREN, '('))
            i += 1
        elif ch == ')':
            tokens.append((TOK_RPAREN, ')'))
            i += 1
        elif ch == '!':
            tokens.append((TOK_NOT, '!'))
            i += 1
        elif ch == '~':
            tokens.append((TOK_EQUIV, '~'))
            i += 1
        elif ch == '-' and i + 1 < len(formula) and formula[i + 1] == '>':
            tokens.append((TOK_IMPL, '->'))
            i += 2
        elif ch == '/' and i + 1 < len(formula) and formula[i + 1] == '\\':
            tokens.append((TOK_AND, '/\\'))
            i += 2
        elif ch == '\\' and i + 1 < len(formula) and formula[i + 1] == '/':
            tokens.append((TOK_OR, '\\/'))
            i += 2
        elif ch.isalpha() and ch.isupper():
            tokens.append((TOK_VAR, ch))
            i += 1
        else:
            raise ValueError(f"Неизвестный символ: '{ch}' на позиции {i}")

    return tokens

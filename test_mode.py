# ============================================================
# Режим тестирования: программа генерирует формулу,
# пользователь строит СДНФ, программа проверяет ответ
# ============================================================

from sdnf import build_sdnf, build_sdnf_detailed
from evaluator import get_variables, truth_table
from parser import parse


def _normalize_sdnf(sdnf_str: str) -> set:
    """
    Нормализует СДНФ для сравнения.

    Превращает строку СДНФ в множество frozenset-ов литералов,
    чтобы порядок конституент и литералов не влиял на сравнение.
    """
    if not sdnf_str.strip():
        return set()

    # Убираем внешние скобки
    s = sdnf_str.strip()
    if s.startswith("(") and s.endswith(")"):
        # Проверяем, что это действительно внешние скобки
        depth = 0
        is_outer = True
        for i, ch in enumerate(s):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            if depth == 0 and i < len(s) - 1:
                is_outer = False
                break
        if is_outer:
            s = s[1:-1]

    # Разделяем по \\/ на верхнем уровне скобок
    constituents = []
    depth = 0
    current = ""
    i = 0
    while i < len(s):
        if s[i] == '(':
            depth += 1
            current += s[i]
            i += 1
        elif s[i] == ')':
            depth -= 1
            current += s[i]
            i += 1
        elif s[i] == '\\' and i + 1 < len(s) and s[i + 1] == '/' and depth == 0:
            constituents.append(current.strip())
            current = ""
            i += 2
        else:
            current += s[i]
            i += 1
    if current.strip():
        constituents.append(current.strip())

    # Каждую конституенту разбиваем на литералы
    result = set()
    for const in constituents:
        # Убираем скобки вокруг конституенты
        c = const.strip()
        if c.startswith("(") and c.endswith(")"):
            c = c[1:-1]

        # Разделяем по /\\ на верхнем уровне
        literals = []
        current = ""
        i = 0
        while i < len(c):
            if c[i] == '/' and i + 1 < len(c) and c[i + 1] == '\\':
                literals.append(current.strip())
                current = ""
                i += 2
            else:
                current += c[i]
                i += 1
        if current.strip():
            literals.append(current.strip())

        result.add(frozenset(literals))

    return result


def _check_answer(formula: str, user_answer: str) -> dict:
    """
    Проверяет ответ пользователя.

    Возвращает словарь:
        correct    — bool, правильно ли
        expected   — правильная СДНФ
        user       — ответ пользователя
        message    — сообщение с пояснением
    """
    correct_sdnf = build_sdnf(formula)

    # Пустая СДНФ (противоречие)
    if not correct_sdnf:
        user_empty = user_answer.strip() == "" or user_answer.strip().lower() in (
            "нет", "противоречие", "-", "пусто"
        )
        if user_empty:
            return {
                "correct": True,
                "expected": "(противоречие)",
                "user": user_answer,
                "message": "Верно! Формула является противоречием, СДНФ не существует.",
            }
        else:
            return {
                "correct": False,
                "expected": "(противоречие)",
                "user": user_answer,
                "message": "Неверно. Формула является противоречием — СДНФ не существует.",
            }

    # Сравниваем нормализованные формы
    expected_norm = _normalize_sdnf(correct_sdnf)
    user_norm = _normalize_sdnf(user_answer)

    if expected_norm == user_norm:
        return {
            "correct": True,
            "expected": correct_sdnf,
            "user": user_answer,
            "message": "Верно!",
        }
    else:
        return {
            "correct": False,
            "expected": correct_sdnf,
            "user": user_answer,
            "message": f"Неверно.\n  Правильный ответ: {correct_sdnf}",
        }


def test_mode():
    """Запускает интерактивный режим тестирования."""
    print("\n=== Режим тестирования ===")
    print("Программа предлагает формулу — вы строите СДНФ.")
    print("Операторы: /\\ (и), \\/ (или), ! (не), -> (импл.), ~ (экв.)")
    print("Если формула — противоречие, напишите 'противоречие'.")
    print("Введите 'назад' для возврата в меню.\n")

    formulas = [
        "(P\\/Q)",
        "(!P/\\Q)",
        "(P->Q)",
    ]

    score = 0
    total = 0

    for formula in formulas:
        total += 1

        print(f"\n--- Вопрос {total} ---")
        print(f"Формула: {formula}")
        print("Постройте СДНФ:")

        try:
            answer = input("Ответ >>> ").strip()
        except EOFError:
            total -= 1
            break

        if answer.lower() in ("назад", "back", "quit", "exit"):
            total -= 1
            break

        # Проверяем
        result = _check_answer(formula, answer)

        if result["correct"]:
            score += 1
            print(f"  ✓ {result['message']}")
        else:
            print(f"  ✗ {result['message']}")

            # Показываем подробное решение
            print("\n  Подробное решение:")
            detailed = build_sdnf_detailed(formula)
            variables = detailed["variables"]
            header = "    " + " | ".join(variables) + " | F"
            print(header)
            print("    " + "-" * (len(header) - 4))
            for values, res in detailed["truth_table"]:
                row = " | ".join(str(values[v]) for v in variables)
                print(f"    {row} | {res}")

        print(f"\n  Счёт: {score}/{total}")

    # Итоги
    if total > 0:
        percent = score / total * 100
        print(f"\n=== Результат: {score}/{total} ({percent:.0f}%) ===\n")
    else:
        print("\n=== Тестирование завершено ===\n")

# ============================================================
# Режим решения: пользователь вводит формулу,
# программа показывает пошаговое построение СДНФ
# ============================================================

from sdnf import build_sdnf_detailed


def _print_truth_table(variables, table):
    """Печатает таблицу истинности."""
    header = " | ".join(variables) + " | F"
    print(header)
    print("-" * len(header))
    for values, result in table:
        row = " | ".join(str(values[v]) for v in variables)
        print(f"{row} | {result}")


def _print_constituents(constituents):
    """Печатает найденные конституенты единицы."""
    for i, c in enumerate(constituents, 1):
        print(f"  {i}) ({'/\\'.join(c)})")


def solve_one(formula: str):
    """Решает одну формулу с выводом всех шагов."""
    try:
        result = build_sdnf_detailed(formula)
    except ValueError as e:
        print(f"\n  Ошибка: {e}\n")
        return

    print(f"\n  Формула: {result['formula']}")
    print(f"  Переменные: {', '.join(result['variables'])}")

    print(f"\n  Таблица истинности:")
    _print_truth_table(result["variables"], result["truth_table"])

    if not result["constituents"]:
        print("\n  Формула является противоречием — СДНФ не существует.")
    else:
        print(f"\n  Конституенты единицы ({len(result['constituents'])} шт.):")
        _print_constituents(result["constituents"])
        print(f"\n  СДНФ: {result['sdnf']}")

    print()


def solve_mode():
    """Запускает интерактивный режим решения."""
    print("\n=== Режим построения СДНФ ===")
    print("Операторы: /\\ (и), \\/ (или), ! (не), -> (импл.), ~ (экв.)")
    print("Переменные: A-Z")
    print("Введите 'назад' для возврата в меню.\n")

    while True:
        try:
            inp = input("Формула >>> ").strip()
        except EOFError:
            break

        if inp.lower() in ("назад", "back", "quit", "exit"):
            break
        if not inp:
            continue

        solve_one(inp)

# Лабораторная работа №1 по дисциплине ЛОИС
# Автор: Морозов Артем
# Вариант 9: построение СДНФ формулы логики высказываний

from sdnf import build_sdnf_detailed


def _print_truth_table(variables, table):
    header = " | ".join(variables) + " | F" if variables else "F"
    print(header)
    print("-" * len(header))
    for values, result in table:
        row = " | ".join(str(values[v]) for v in variables)
        print(f"{row} | {result}" if variables else str(result))


def _print_constituents(constituents):
    for i, constituent in enumerate(constituents, 1):
        if constituent:
            text = "/\\".join(constituent)
            print(f"  {i}) ({text})")
        else:
            print(f"  {i}) 1")


def solve_one(formula: str):
    try:
        result = build_sdnf_detailed(formula)
    except ValueError as e:
        print(f"\n  Ошибка: {e}\n")
        return

    variables = result["variables"]
    variables_text = ", ".join(variables) if variables else "-"

    print(f"\n  Формула: {result['formula']}")
    print(f"  Переменные: {variables_text}")

    print("\n  Таблица истинности:")
    _print_truth_table(variables, result["truth_table"])

    if not result["constituents"]:
        print("\n  Формула является противоречием: СДНФ не существует.")
    else:
        print(f"\n  Конституенты единицы ({len(result['constituents'])} шт.):")
        _print_constituents(result["constituents"])
        print(f"\n  СДНФ: {result['sdnf']}")

    print()


def _has_whitespace(value: str) -> bool:
    return any(ch.isspace() for ch in value)


def solve_mode():
    print("\n=== Режим построения СДНФ ===")
    print("Операторы: /\\ (и), \\/ (или), ! (не), -> (импликация), ~ (эквиваленция)")
    print("Переменные: A-Z; константы: 0, 1")
    print("Строгий ввод: A, 1, (!A), (A/\\B), (A->1), ((A\\/B)/\\(!C))")
    print("Пробелы в формулах не допускаются. Введите 'назад' для возврата в меню.\n")

    while True:
        try:
            raw_inp = input("Формула >>> ")
        except EOFError:
            break

        inp = raw_inp.strip()
        if inp.lower() in ("назад", "back", "quit", "exit"):
            break
        if not inp:
            continue
        if raw_inp != inp or _has_whitespace(inp):
            print("Некорректный ввод: пробелы в формуле не допускаются.")
            continue

        solve_one(inp)

import io
import math
import tokenize
import token

def tokenize_expression(expression):
    """Разбивает выражение на отдельные элементы."""
    result = []

    try:
        generator = tokenize.generate_tokens(
            io.StringIO(expression).readline
        )

        for item in generator:
            if item.type in (
                token.ENDMARKER,
                token.NEWLINE,
                token.NL,
                token.INDENT,
                token.DEDENT
            ):
                continue

            if item.type == token.ERRORTOKEN:
                if item.string.isspace():
                    continue
                raise ValueError(
                    f"Недопустимый символ : {item.string}"
                )

            if item.type not in (
                token.NUMBER,
                token.NAME,
                token.OP
            ):
                raise ValueError(
                    f"Недопустимый элемент: {item.string}"
                )

            result.append((item.type, item.string))

    except (tokenize.TokenError, IndentationError) as error:
        raise ValueError("Ошибка разбора выражения") from error

    return result

# Общие переменные для работы функций
tokens = []
position = 0

def current():
    """Возвращает текущий элемент."""
    if position < len(tokens):
        return tokens[position]
    return None

def match(value):
    """Проверяет текущий элемент и переходит к следующему."""
    global position

    item = current()

    if item is not None and item[1] == value:
        position += 1
        return True

    return False

def expect(value):
    """Проверяет наличие нужного символа."""
    if not match(value):
        raise ValueError(f"Ожидался символ '{value}'")

def parse_or():
    """Обрабатывает побитовое ИЛИ."""
    result = parse_add()

    while match("|"):
        right = parse_add()

        if type(result) is not int or type(right) is not int:
            raise ValueError(
                "Оператор | работает только с целыми числами"
            )

        result = result | right

    return result

def parse_add():
    """Обрабатывает сложение и вычитание."""
    result = parse_mul()

    while True:
        if match("+"):
            result += parse_mul()
        elif match("-"):
            result -= parse_mul()
        else:
            break

    return result

def parse_mul():
    """Обрабатывает умножение и деление."""
    result = parse_unary()

    while True:
        if match("*"):
            result *= parse_unary()

        elif match("/"):
            right = parse_unary()

            if right == 0:
                raise ValueError("Деление на ноль")

            result /= right
        else:
            break

    return result

def parse_unary():
    """Обрабатывает унарный плюс и минус."""
    if match("+"):
        return parse_unary()

    if match ("-"):
        return -parse_unary()

    return parse_primary()

def parse_primary():
    """Обрабатывает числа, скобки и log10."""
    global position

    item = current()

    if item is None:
        raise ValueError("Ожидалось число или выражение")

    item_type, value = item

    if item_type == token.NUMBER:
        position += 1

        try:
            if any(char in value.lower() for char in ".e"):
                return float(value)

            return int(value)

        except (ValueError, OverflowError) as error:
            raise ValueError(
                f"Некорректное число: {value}"
            ) from error

    if item_type == token.OP and value == "(":
        position += 1
        result = parse_or()
        expect(")")
        return result

    if item_type == token.NAME and value == "log10":
        position += 1
        expect("(")
        argument = parse_or()
        expect(")")

        if argument <= 0:
            raise ValueError(
                "Аргумент log 10 должен быть больше 0"
            )

        return math.log10(argument)

    raise ValueError(f"Неожиданный элемент: {value}")

def calculate(expression):
    """Запускает вычисление выражения."""
    global tokens, position

    tokens = tokenize_expression(expression)
    position = 0

    if not tokens:
        raise ValueError("Выражение пустое")

    result = parse_or()

    if current() is not None:
        raise ValueError(
            f"Лишний элемент: {current()[1]}"
        )

    return result

def main():
    print("Калькулятор арифметических выражений")
    print("Поддерживаются: +, -, *, /, скобки, log10, |")
    print("Для выхода введите exit")

    while True:
        expression = input("\nВведите выражение:\n")

        if expression.strip() == "exit":
            break

        try:
            result = calculate(expression)
            print("Результат:", result)

        except (ValueError, ZeroDivisionError) as error:
            print("Ошибка:", error)

if __name__ == "__main__":
    main()
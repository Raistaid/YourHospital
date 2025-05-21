from datetime import datetime

# Вспомогательные функции
def datetoday():
    """Возвращает текущую дату в формате 'ГГГГ-ММ-ДД'."""
    today = datetime.now().strftime("%Y-%m-%d")
    return today


def checkonlyalpha(x):
    """Проверяет, состоит ли строка только из букв."""
    return x.isalpha()


def checkonlynum(x):
    """Проверяет, состоит ли строка только из цифр."""
    return x.isdigit()


def checkpass(x):
    """Проверяет сложность пароля (минимум 8 символов, буквы, цифры и спецсимволы)."""
    f1, f2, f3 = False, False, False
    if len(x) < 8:
        return False
    if any(c.isalpha() for c in x):
        f1 = True
    if any(c.isdigit() for c in x):
        f2 = True
    if any(c in x for c in ['@', '$', '!', '#', '%', '&', '*']):
        f3 = True

    return f1 and f2 and f3
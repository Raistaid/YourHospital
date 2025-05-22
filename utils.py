from datetime import datetime

def datetoday():
    """Возвращает текущую дату в формате 'ГГГГ-ММ-ДД'."""
    return datetime.now().strftime("%Y-%m-%d")

def checkonlyalpha(x):
    """Проверяет, состоит ли строка только из букв."""
    return x.isalpha()

def checkonlynum(x):
    """Проверяет, состоит ли строка только из цифр."""
    return x.isdigit()

def checkpass(x):
    """Проверяет сложность пароля (минимум 8 символов, буквы, цифры и спецсимволы)."""
    f1, f2, f3 = False, False, False
    if len(x) < 8: return False
    f1 = any(c.isalpha() for c in x)
    f2 = any(c.isdigit() for c in x)
    f3 = any(c in x for c in ['@', '$', '!', '#', '%', '&', '*'])
    return f1 and f2 and f3
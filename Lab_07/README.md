# Лабораторна робота №7 — `functools` та `operator` (Варіант 4: Облік працівників)

## Опис варіанта
Програма реалізує функціональний конвеєр обробки даних про працівників із використанням засобів стандартної бібліотеки Python (`functools` та `operator`):

- **`functools.reduce`**: побудова універсального конвеєра перетворень `pipeline(value, *funcs)` та обчислення загального фонду виплат `total_payroll`.
- **`functools.partial`**: налаштування політик нарахування премій (`standard_bonus_policy`, `senior_bonus_policy`), часткове застосування функцій відображення (`mapf`), фільтрації (`filt`) та сортування.
- **`operator` (`itemgetter`, `attrgetter`, `methodcaller`)**: видобування полів зі словників, нормалізація рядкових значень без зайвих `lambda`-виразів і багатокритеріальне сортування об'єктів.
- **`functools.singledispatch`**: поліморфний завантажувач `load_employees`, який підтримує JSON-рядки, шляхи до файлів `.json` та `.csv` (`str` і `pathlib.Path`), відкриті текстові потоки (`io.TextIOBase`) та готові списки словників (`list[dict]`).
- **`functools.total_ordering`**: клас `EmployeeOrder` з повним набором операцій порівняння за критеріями `(salary, experience, name)`.

## Структура проєкту
```text
Lab_07/
├── main.py
├── core.py
├── app.py
├── loaders.py
├── models.py
├── sample_data.json
├── sample_data.csv
├── README.md
├── requirements.txt
├── pyproject.toml
├── mypy.ini
├── tests/
│   ├── __init__.py
│   └── test_lab07.py
└── report/
    └── Zavalii_Agnesa_FeP-23_V04.pdf
```

## Встановлення залежностей
```bash
pip install -r requirements.txt
```

## Запуск програми
```bash
python main.py
```

## Перевірка якості коду та запуск тестів
```bash
pytest -q
mypy .
ruff check .
black --check .
```

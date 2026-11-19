# SIPL Language Toolkit

![CI](https://github.com/roadwsign/tp_lab/actions/workflows/ci.yml/badge.svg)

Інструментарій для навчальної імперативної мови **SIPL**: формальна граматика, LALR-парсер, типізоване AST із позиціями у коді, детермінований інтерпретатор, покрокове трасування виконання (`trace`), CLI та візуалізація Parse Tree й AST.

## Обрані завдання та бали

| ID | Модуль / функціональність | Бали |
| :--- | :--- | :---: |
| **CORE-01** | Формальна специфікація SIPL (`grammar/sipl.lark`, `docs/grammar.md`, приклади) | 0.5 |
| **CORE-02** | Парсер і типізоване AST із позиціями (`SourceSpan`, `SIPLSyntaxError`) | 1.5 |
| **CORE-03** | Детермінований інтерпретатор SIPL із захистом від зациклення (`--max-steps`) | 2.0 |
| **CORE-04** | Подієва модель виконання та режим `trace` | 1.0 |
| **CORE-05** | CLI (`parse`, `check`, `run`, `trace`) і формальна JSON-схема | 1.0 |
| **CORE-06** | Conformance suite (26 еталонних тестів) та автономний раннер | 1.0 |
| **VIS-01** | Візуалізація Parse Tree (Text, JSON, Graphviz DOT, SVG) | 1.5 |
| **VIS-02** | Візуалізація AST і side-by-side порівняння Parse Tree ↔ AST (JSON, SVG, HTML) | 1.0 |
| **REL-01** | CI у GitHub Actions (Ruff, Mypy, pytest, conformance suite, збірка пакета) | 0.5 |
| **REL-02** | GitHub Releases із тегами SemVer та `CHANGELOG.md` | 0.5 |
| **Разом** | | **10.5** |

## Вимоги та встановлення

Потрібен **Python 3.10** або новіший.

1. Клонуйте репозиторій та перейдіть у директорію проєкту:
   ```bash
   git clone [https://github.com/roadwsign/tp_lab.git](https://github.com/roadwsign/tp_lab.git)
   cd tp_lab
   ```

2. Створіть та активуйте віртуальне середовище:
   * **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

3. Встановіть пакет разом із залежностями для розробки та тестування:
   ```bash
   python -m pip install -e ".[dev]"
   ```

4. Перевірте, що CLI працює:
   ```bash
   sipl --version
   sipl run examples/power.sipl --state X=5 --state Y=2
   ```

## Структура проєкту

```text
tp_lab/
├── .github/workflows/ci.yml    # GitHub Actions CI
├── grammar/sipl.lark           # Формальна граматика Lark
├── src/sipl/
│   ├── ast.py                  # Типізовані вузли AST та SourceSpan
│   ├── parser.py               # LALR-парсер і серіалізація AST
│   ├── interpreter/engine.py   # Інтерпретатор і подієвий trace
│   ├── visualization/render.py # Експорт у Text, JSON, DOT, SVG, HTML
│   └── cli.py                  # Інтерфейс командного рядка
├── examples/                   # Приклади програм мовою SIPL
├── tests/                      # Модульні та еталонні (conformance) тести
└── docs/                       # Специфікація мови, CLI та JSON Schema
```

## Використання CLI

```bash
# Перевірка синтаксису
sipl check examples/power.sipl
sipl check examples/power.sipl --json

# Побудова та візуалізація дерев
sipl parse examples/power.sipl --view ast --format text
sipl parse examples/power.sipl --view parse-tree --format json
sipl parse examples/power.sipl --view parse-tree --format dot > tree.dot
sipl parse examples/power.sipl --view ast --format svg > ast.svg
sipl parse examples/power.sipl --view comparison --format html > comparison.html

# Виконання програми та трасування кроків
sipl run examples/power.sipl --state X=5 --state Y=2
sipl trace examples/power.sipl --state X=5 --state Y=2
```

Для зчитування коду зі стандартного потоку вводу (`stdin`) передайте `-` або не вказуйте шлях до файлу.

### Коди завершення (Exit Codes)
* `0` — успішне виконання;
* `2` — синтаксична помилка у програмі SIPL;
* `3` — помилка виконання (наприклад, звернення до неініціалізованої змінної чи перевищення ліміту кроків), некоректний формат `--state` або помилка читання файлу.

Ліміт кроків виконання за замовчуванням становить **100 000** і змінюється параметром `--max-steps`.

## Python API

```python
from sipl import parse
from sipl.interpreter import execute

program = parse("begin X := X + 1 end")
result = execute(program, initial_state={"X": 4}, trace=True)

print(result.state)  # {'X': 5}
print([event.to_dict() for event in result.trace])
```

## Тестування та перевірка якості

```bash
ruff check .
mypy src
pytest
python tests/run_conformance.py
```

Мінімальний поріг покриття коду тестами (`pytest-cov`), зафіксований у `pyproject.toml`, становить **80%**.

## Документація

* [Формальна граматика та лексика SIPL](docs/grammar.md)
* [Формат JSON-виводу CLI та JSON Schema](docs/cli-json.md)
* [Специфікація еталонного набору тестів (Conformance Suite)](docs/conformance.md)
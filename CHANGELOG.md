# Changelog

Усі суттєві зміни у проєкті документуються у цьому файлі.

## [0.1.0] — 2026-11-19

### Додано
- **Автоматизація та реліз (`REL-01`, `REL-02`):** CI-пайплайн GitHub Actions (Ruff, Mypy, pytest із порогом покриття 80%, conformance suite, збірка wheel/sdist) та реліз із тегом `v0.1.0`.
- **Документація:** українська специфікація граматики (`docs/grammar.md`), форматів CLI (`docs/cli-json.md`) та conformance suite (`docs/conformance.md`).

---

## [0.0.3] — 2026-11-18

### Додано
- **CLI та контракти (`CORE-05`):** інтерфейс командного рядка (`parse`, `check`, `run`, `trace`), підтримка зчитування зі `stdin`, документовані коди завершення (`0`, `2`, `3`) та JSON Schema (`docs/cli-output.schema.json`).
- **Візуалізація (`VIS-01`, `VIS-02`):** експорт Parse Tree та AST у текстовий вигляд, JSON, Graphviz DOT, SVG і side-by-side HTML/SVG-порівняння з вбудованими діаграмами дерев.

---

## [0.0.2] — 2026-11-17

### Додано
- **Інтерпретатор (`CORE-03`):** детерміноване виконання програм SIPL (`sipl.interpreter`), перевірка неініціалізованих змінних (`SIPLRuntimeError`) і захист від нескінченних циклів (`StepLimitExceeded`, параметр `--max-steps`).
- **Трасування виконання (`CORE-04`):** подієва модель (`BeforeStatement`, `AfterStatement`, `VariableChanged`, `ConditionChecked`, `ProgramTerminated`) з фіксацією стану пам'яті на кожному кроці.
- **Conformance Suite (`CORE-06`):** набір із 26 еталонних позитивних і негативних тестів (`tests/conformance.json`) та автономний скрипт перевірки (`tests/run_conformance.py`).

---

## [0.0.1] — 2026-11-16

### Додано
- **Специфікація та граматика (`CORE-01`):** формальна граматика мови SIPL у форматі Lark (`grammar/sipl.lark`), EBNF-опис та базові приклади програм (`examples/`).
- **Парсер і AST (`CORE-02`):** LALR-парсер (`sipl.parser`), типізовані незмінні вузли AST із точними координатами у вихідному тексті (`SourceSpan`) та інформативні синтаксичні помилки (`SIPLSyntaxError`).
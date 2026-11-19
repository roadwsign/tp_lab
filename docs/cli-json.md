# Формат JSON-виводу CLI

Усі структури JSON мають кодування **UTF-8** і валідуються формальною схемою [`docs/cli-output.schema.json`](cli-output.schema.json) (JSON Schema Draft 2020-12).

## 1. Перевірка синтаксису (`sipl check --json`)

У разі успішної перевірки повертається об'єкт:

```json
{
  "valid": true,
  "message": "SIPL program is syntactically correct"
}
```

## 2. Побудова дерев (`sipl parse --format json`)

Залежно від параметра `--view` повертається:
* `--view ast`: серіалізоване типізоване AST (`Program`, `Sequence`, `Assignment`, `While`, `If`, `Block`, `Skip` тощо);
* `--view parse-tree`: дерево розбору Lark із вузлами `Rule` та `Token`;
* `--view comparison`: комбінований об'єкт `{"parse_tree": {...}, "ast": {...}}`.

Кожен вузол містить координати `span` (`line`, `column`, `end_line`, `end_column`, `start_pos`, `end_pos`), а під час зчитування з файлу або потоку вводу — також поле `source_fragment` із точним фрагментом вихідного коду.

## 3. Виконання програми (`sipl run`)

Повертає фінальний стан пам'яті у вигляді словника `змінна → ціле значення`:

```json
{
  "X": 5,
  "Y": 0,
  "R": 25
}
```

## 4. Покрокове трасування (`sipl trace`)

Повертає об'єкт зі станом пам'яті, кількістю кроків та масивом подій `trace`:

```json
{
  "state": {"X": 5, "Y": 0, "R": 25},
  "steps": 11,
  "trace": [
    {
      "event": "VariableChanged",
      "step": 2,
      "statement": "Assignment",
      "span": {"line": 2, "column": 5, "end_line": 2, "end_column": 11, "start_pos": 10, "end_pos": 16},
      "state": {"X": 5, "Y": 2, "R": 1},
      "variable": "R",
      "old_value": null,
      "new_value": 1,
      "condition": null
    }
  ]
}
```

### Типи подій `trace`
* `BeforeStatement` — перед початком виконання оператора;
* `AfterStatement` — після завершення виконання оператора;
* `VariableChanged` — зміна значення змінної (заповнюються `variable`, `old_value`, `new_value`);
* `ConditionChecked` — обчислення булевої умови в `if` або `while` (заповнюється `condition`);
* `ProgramTerminated` — штатне завершення виконання програми.

## 5. Помилки та коди завершення

У разі помилки з прапорцем `--json` виводиться структурований JSON-об'єкт:

* **Синтаксична помилка (код завершення `2`):**
  ```json
  {
    "error": "syntax",
    "message": "Unexpected token 'end'",
    "line": 1,
    "column": 12,
    "expected": ["NAME", "NUMBER"]
  }
  ```

* **Помилка виконання або вводу/виводу (код завершення `3`):**
  ```json
  {
    "error": "execution",
    "message": "Variable 'Y' is not defined"
  }
  ```
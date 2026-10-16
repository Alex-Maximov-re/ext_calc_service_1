# Таблицы для хранения структуры FSIGHT алгоритмов

## Обзор

В этом каталоге находятся SQL скрипты для создания таблиц на основе структуры кубов и словарей из конфигурации алгоритмов FSIGHT (TEST_ALG.json).

## Созданные таблицы

### Таблицы для кубов

| Таблица | Описание |
|---------|----------|
| `cubes` | Основная таблица кубов (идентификатор, название, ключ) |
| `cube_dimensions` | Измерения кубов (связь куб-измерение) |
| `dimension_elements` | Элементы выбора для измерений кубов |

### Таблицы для словарей

| Таблица | Описание |
|---------|----------|
| `dictionaries` | Основная таблица словарей (ключ, ID, название) |
| `dictionary_attributes` | Атрибуты словарей (позиция, ID, ключ, название) |
| `dictionary_elements` | Элементы словарей (индекс, ID, имя, родитель, уровень) |
| `dictionary_element_attrs` | Атрибуты элементов словарей (ключ элемента, ID атрибута, значение) |

## Созданные SQL файлы

| Файл | Описание |
|------|----------|
| `create_cubes_tables.sql` | Создание таблиц для кубов и загрузка базовых данных |
| `create_dictionaries_tables.sql` | Создание таблиц для словарей и пример загрузки данных |
| `generate_cubes_dictionaries.sql` | Автогенерируемый файл со всеми таблицами и данными из TEST_ALG.json |

## Структура кубов из TEST_ALG.json

### Куб CUB_OSP_1 (Куб OSP 1)

**Измерения (11):**
1. Факты структуры хранения (DICT_INDICATOR_DATA_TYPES)
2. Валюты (DICT_CURR)
3. Контракты (DICT_CONTRACT)
4. МВЗ (DICT_MVZ)
5. Период (DICT_PERIOD)
6. Показатели (DICT_INDIC)
7. Статьи (DICT_ARTIC)
8. Сценарии (DICT_SCENAR)
9. ЦФО (DICT_TSFO)
10. Элементы затрат (DICT_COST)
11. Год (DICT_YEAR)

## Словари из TEST_ALG.json

Найдено 11 словарей:
- DICT_INDICATOR_DATA_TYPES (Факты структуры хранения) - 3 элемента
- DICT_CURR (Валюты)
- DICT_CONTRACT (Контракты)
- DICT_MVZ (МВЗ)
- DICT_PERIOD (Период)
- DICT_INDIC (Показатели)
- DICT_ARTIC (Статьи)
- DICT_SCENAR (Сценарии)
- DICT_TSFO (ЦФО)
- DICT_COST (Элементы затрат)
- DICT_YEAR (Год)

## Использование

### Генерация таблиц

```sql
-- В SQL Server Management Studio или другом СУБД
EXEC sp_executesql N'
    @sql = (SELECT * FROM OPENROWSET(BULK ''C:\Git\ext_calc_service_1\sql\generate_cubes_dictionaries.sql'', SINGLE_CLOB))
    EXEC(@sql)
'
```

### Проверка данных

```sql
-- Показать все кубы
SELECT * FROM cubes;

-- Показать измерения для куба
SELECT * FROM cube_dimensions WHERE cube_id = 'CUB_OSP_1';

-- Показать элементы выбора измерения
SELECT * FROM dimension_elements WHERE cube_id = 'CUB_OSP_1';

-- Показать все словари
SELECT * FROM dictionaries;

-- Показать элементы словаря
SELECT * FROM dictionary_elements WHERE dict_key = 2225;

-- Показать атрибуты элемента словаря
SELECT * FROM dictionary_element_attrs WHERE dict_key = 2225 AND elem_id = '1';
```

## Автоматическая генерация

Для пересоздания таблиц из обновленного JSON файла:

```bash
python generate_tables.py
```

Скрипт:
1. Читает TEST_ALG.json
2. Извлекает все кубы и измерения
3. Извлекает все словари, элементы и атрибуты
4. Генерирует SQL файл с CREATE TABLE и INSERT statements

## Примечания

- Все таблицы созданы с использованием SQL Server синтаксиса (IDENTITY, VARCHAR(MAX))
- Для других СУБД可能需要 небольшая адаптация (например, SERIAL вместо IDENTITY в PostgreSQL)
- Скрипт поддерживает любые размеры JSON файла конфигурации

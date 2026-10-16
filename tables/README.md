# Тестовые таблицы FSIGHT

## Обзор

В этой папке находятся таблицы, созданные на основе структуры кубов и словарей из файла `TEST_ALG.json`.

## Форматы данных

### 1. JSON файлы

Наиболее подробный формат с полной структурой данных.

| Файл | Размер | Записей | Описание |
|------|--------|---------|----------|
| `cubes.json` | 99 Б | 1 | Кубы FSIGHT |
| `cube_dimensions.json` | 1.4 КБ | 11 | Измерения кубов |
| `dimension_elements.json` | 1.4 КБ | 10 | Элементы выбора измерений |
| `dictionaries.json` | 1.1 КБ | 11 | Словари |
| `dictionary_attributes.json` | 8.4 КБ | 60 | Атрибуты словарей |
| `dictionary_elements.json` | 153 КБ | 768 | Элементы словарей |
| `dictionary_element_attrs.json` | 1.5 МБ | 3,946 | Атрибуты элементов |

**Как открыть:** Любой текстовый редактор, VS Code, или загрузить в Python:
```python
import json
with open('cubes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### 2. CSV файлы

Универсальный формат для Excel и других таблиц.

| Файл | Размер | Записей | Описание |
|------|--------|---------|----------|
| `cubes.csv` | 60 Б | 1 | Кубы |
| `cube_dimensions.csv` | 541 Б | 11 | Измерения |
| `dimension_elements.csv` | 523 Б | 10 | Элементы измерений |
| `dictionaries.csv` | 426 Б | 11 | Словари |
| `dictionary_attributes.csv` | 2.2 КБ | 60 | Атрибуты словарей |
| `dictionary_elements.csv` | 53 КБ | 768 | Элементы словарей |
| `dictionary_element_attrs.csv` | 656 КБ | 3,946 | Атрибуты элементов |

**Как открыть:** Excel, Google Sheets, или любой редактор таблиц.

### 3. SQLite база данных

Полноценная реляционная БД с связями между таблицами.

| Файл | Размер | Таблиц | Всего записей |
|------|--------|--------|---------------|
| `fsight_cubes.db` | 983 КБ | 7 | ~4,837 |

**Как открыть:**
- **DB Browser for SQLite** (рекомендуется) - https://sqlitebrowser.org/
- **VS Code** с расширением SQLite
- **Python**:
```python
import sqlite3
conn = sqlite3.connect('fsight_cubes.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM cubes')
print(cursor.fetchall())
```

## Структура БД

### Таблицы

```
cubes
├── cube_id (TEXT PRIMARY KEY)
├── cube_name (TEXT)
└── cube_key (INTEGER)

cube_dimensions
├── id (INTEGER PRIMARY KEY)
├── cube_id (TEXT, FK → cubes)
├── dim_name (TEXT)
├── dim_id (TEXT)
└── dim_key (INTEGER)

dimension_elements
├── id (INTEGER PRIMARY KEY)
├── cube_id (TEXT, FK → cubes)
├── dim_id (TEXT)
├── elem_key (TEXT)
└── elem_name (TEXT)

dictionaries
├── dict_key (INTEGER PRIMARY KEY)
├── dict_id (TEXT)
└── dict_name (TEXT)

dictionary_attributes
├── id (INTEGER PRIMARY KEY)
├── dict_key (INTEGER, FK → dictionaries)
├── attr_idx (INTEGER)
├── attr_id (TEXT)
├── attr_key (INTEGER)
└── attr_name (TEXT)

dictionary_elements
├── id (INTEGER PRIMARY KEY)
├── dict_key (INTEGER, FK → dictionaries)
├── elem_idx (INTEGER)
├── elem_id (TEXT)
├── elem_name (TEXT)
├── elem_parent (INTEGER)
└── elem_level_key (INTEGER)

dictionary_element_attrs
├── id (INTEGER PRIMARY KEY)
├── dict_key (INTEGER, FK → dictionaries)
├── elem_id (TEXT)
├── attr_id (TEXT)
└── attr_value (TEXT)
```

## Статистика данных

### Кубы
- **1 куб**: CUB_OSP_1 (Куб OSP 1)

### Измерения куба
- **11 измерений**:
  1. Факты структуры хранения
  2. Валюты
  3. Контракты
  4. МВЗ
  5. Период
  6. Показатели
  7. Статьи
  8. Сценарии
  9. ЦФО
  10. Элементы затрат
  11. Год

### Словари
- **11 словарей** с полной структурой атрибутов и элементов

## Использование

### Подключение к SQLite базе

```python
import sqlite3

conn = sqlite3.connect('fsight_cubes.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Пример: получить все измерения для куба
cursor.execute('''
    SELECT dim_name, dim_id, dim_key 
    FROM cube_dimensions 
    WHERE cube_id = 'CUB_OSP_1'
''')
for row in cursor.fetchall():
    print(f"{row['dim_name']} ({row['dim_id']})")

conn.close()
```

### Загрузка в SQL Server

```sql
-- Использовать sql/generate_cubes_dictionaries.sql
-- Или загрузить CSV через SSIS/большую команду INSERT
```

## Генерация новых данных

Для пересоздания всех таблиц из обновленного JSON файла:

```bash
python create_test_tables.py
```

## Примеры запросов

### PostgreSQL

```sql
-- Получить измерения куба
SELECT cd.dim_name, cd.dim_id, de.elem_key, de.elem_name
FROM cube_dimensions cd
LEFT JOIN dimension_elements de ON cd.cube_id = de.cube_id
WHERE cd.cube_id = 'CUB_OSP_1';

-- Получить все элементы словаря
SELECT de.elem_name, dea.attr_id, dea.attr_value
FROM dictionary_elements de
LEFT JOIN dictionary_element_attrs dea ON de.dict_key = dea.dict_key
WHERE de.dict_key = 2225;
```

### MySQL

```sql
-- Аналогично PostgreSQL, но без explicit ROWS
```

## Рекомендации

1. **Для разработки** - используйте SQLite базу (`fsight_cubes.db`)
2. **Для просмотра в Excel** - используйте CSV файлы
3. **Для интеграции** - используйте JSON файлы
4. **Для production** - используйте SQL Server / PostgreSQL с `generate_cubes_dictionaries.sql`

## Примечания

- Все даты в формате YYYY-MM-DD
- Текстовые поля используют кодировку UTF-8
- CSV файлы содержат BOM для корректного отображения кириллицы в Excel
- SQLite база использует Foreign Key constraints

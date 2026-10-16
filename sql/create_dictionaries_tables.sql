-- Таблицы для хранения словарей (dictionaries) FSIGHT

-- Таблица словарей
CREATE TABLE dictionaries (
    dict_key INT PRIMARY KEY,
    dict_id VARCHAR(50) NOT NULL,
    dict_name VARCHAR(255) NOT NULL
);

-- Таблица атрибутов словарей
CREATE TABLE dictionary_attributes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    dict_key INT NOT NULL,
    attr_idx INT NOT NULL,
    attr_id VARCHAR(50) NOT NULL,
    attr_key INT NOT NULL,
    attr_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)
);

-- Таблица элементов словарей
CREATE TABLE dictionary_elements (
    id INT IDENTITY(1,1) PRIMARY KEY,
    dict_key INT NOT NULL,
    elem_idx INT NOT NULL,
    elem_id VARCHAR(50) NOT NULL,
    elem_name VARCHAR(255) NOT NULL,
    elem_parent INT NOT NULL,
    elem_level_key INT NOT NULL,
    FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)
);

-- Таблица атрибутов элементов словарей
CREATE TABLE dictionary_element_attrs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    dict_key INT NOT NULL,
    elem_id VARCHAR(50) NOT NULL,
    attr_id VARCHAR(50) NOT NULL,
    attr_value VARCHAR(MAX) NOT NULL,
    FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)
);

-- Загружаем данные о словарях
INSERT INTO dictionaries (dict_key, dict_id, dict_name) VALUES
    (2225, 'DICT_INDICATOR_DATA_TYPES', 'Факты структуры хранения'),
    (2557, 'DICT_CURR', 'Валюты'),
    (2636, 'DICT_CONTRACT', 'Контракты'),
    (2572, 'DICT_MVZ', 'МВЗ'),
    (2552, 'DICT_PERIOD', 'Период'),
    (2565, 'DICT_INDIC', 'Показатели'),
    (2568, 'DICT_ARTIC', 'Статьи'),
    (2555, 'DICT_SCENAR', 'Сценарии'),
    (2570, 'DICT_TSFO', 'ЦФО'),
    (2559, 'DICT_COST', 'Элементы затрат'),
    (2554, 'DICT_YEAR', 'Год');

-- Загружаем атрибуты для словаря "Факты структуры хранения"
INSERT INTO dictionary_attributes (dict_key, attr_idx, attr_id, attr_key, attr_name) VALUES
    (2225, 0, 'KEY', 1, 'Ключ'),
    (2225, 1, 'NAME', 2, 'Наименование'),
    (2225, 2, 'ORD', 4, 'Порядок'),
    (2225, 3, 'DB_DATA_TYPE', 5, 'DbDataType'),
    (2225, 4, 'SYSTEM_ID', 6, 'SYSTEM_ID'),
    (2225, 5, 'IDENT', 7, 'Идетификатор факта'),
    (2225, 6, 'NAME_EN_US', 8, 'NAME_en_us'),
    (2225, 7, 'SYSTEM_ID_EN_US', 9, 'SYSTEM_ID_en_us'),
    (2225, 8, 'IDENT_EN_US', 10, 'IDENT_en_us');

-- Загружаем элементы для словаря "Факты структуры хранения"
INSERT INTO dictionary_elements (dict_key, elem_idx, elem_id, elem_name, elem_parent, elem_level_key) VALUES
    (2225, 0, '1', 'Строка', -1, 0),
    (2225, 1, '2', 'Число', -1, 0),
    (2225, 2, '3', 'Дата', -1, 0);

-- Загружаем атрибуты элементов для словаря "Факты структуры хранения"
INSERT INTO dictionary_element_attrs (dict_key, elem_id, attr_id, attr_value) VALUES
    (2225, '1', 'KEY', '1'),
    (2225, '1', 'NAME', 'Строка'),
    (2225, '1', 'ORD', '32'),
    (2225, '1', 'DB_DATA_TYPE', '1'),
    (2225, '1', 'SYSTEM_ID', 'STRING'),
    (2225, '1', 'IDENT', 'VALUE_TEXT'),
    (2225, '2', 'KEY', '2'),
    (2225, '2', 'NAME', 'Число'),
    (2225, '2', 'ORD', '64'),
    (2225, '2', 'DB_DATA_TYPE', '3'),
    (2225, '2', 'SYSTEM_ID', 'NUMBER'),
    (2225, '2', 'IDENT', 'VALUE_NUMBER'),
    (2225, '3', 'KEY', '3'),
    (2225, '3', 'NAME', 'Дата'),
    (2225, '3', 'ORD', '96'),
    (2225, '3', 'DB_DATA_TYPE', '7'),
    (2225, '3', 'SYSTEM_ID', 'DATE'),
    (2225, '3', 'IDENT', 'VALUE_DATE');

-- Загружаем атрибуты для словаря "Валюты"
INSERT INTO dictionary_attributes (dict_key, attr_idx, attr_id, attr_key, attr_name) VALUES
    (2557, 0, 'KEY', 1, 'Ключ'),
    (2557, 1, 'NAME', 2, 'Наименование'),
    (2557, 2, 'PARENT_KEY', 3, 'Владелец'),
    (2557, 3, 'ORD', 4, 'Порядок');

-- Загружаем элементы для словаря "Валюты"
INSERT INTO dictionary_elements (dict_key, elem_idx, elem_id, elem_name, elem_parent, elem_level_key) VALUES
    (2557, 0, '1', 'Без учета валюты', -1, 0);

-- Загружаем атрибуты элементов для словаря "Валюты"
INSERT INTO dictionary_element_attrs (dict_key, elem_id, attr_id, attr_value) VALUES
    (2557, '1', 'KEY', '1'),
    (2557, '1', 'NAME', 'Без учета валюты'),
    (2557, '1', 'PARENT_KEY', ''),
    (2557, '1', 'ORD', '32');

-- Проверка загруженных данных
SELECT 'Словари' AS info, CAST(dict_key AS VARCHAR) AS key, dict_id AS id, dict_name AS name FROM dictionaries
UNION ALL
SELECT 'Атрибуты словарей', CAST(dict_key AS VARCHAR), attr_id, attr_name FROM dictionary_attributes
UNION ALL
SELECT 'Элементы словарей', CAST(dict_key AS VARCHAR), elem_id, elem_name FROM dictionary_elements
UNION ALL
SELECT 'Атрибуты элементов', CAST(dict_key AS VARCHAR), attr_id, attr_value FROM dictionary_element_attrs
ORDER BY info, key, id;

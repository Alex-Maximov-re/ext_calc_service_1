-- Создаем таблицы для хранения структуры кубов FSIGHT

-- Таблица кубов
CREATE TABLE cubes (
    cube_id VARCHAR(50) PRIMARY KEY,
    cube_name VARCHAR(255) NOT NULL,
    cube_key INT NOT NULL
);

-- Таблица измерений кубов
CREATE TABLE cube_dimensions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cube_id VARCHAR(50) NOT NULL,
    dim_name VARCHAR(255) NOT NULL,
    dim_id VARCHAR(50) NOT NULL,
    dim_key INT NOT NULL,
    FOREIGN KEY (cube_id) REFERENCES cubes(cube_id)
);

-- Таблица элементов выбора для измерений
CREATE TABLE dimension_elements (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cube_id VARCHAR(50) NOT NULL,
    dim_id VARCHAR(50) NOT NULL,
    elem_key VARCHAR(50) NOT NULL,
    elem_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (cube_id) REFERENCES cubes(cube_id)
);

-- Загружаем данные о кубах
INSERT INTO cubes (cube_id, cube_name, cube_key) VALUES
    ('CUB_OSP_1', 'Куб OSP 1', 2952);

-- Загружаем данные об измерениях
INSERT INTO cube_dimensions (cube_id, dim_name, dim_id, dim_key) VALUES
    ('CUB_OSP_1', 'Факты структуры хранения', 'DICT_INDICATOR_DATA_TYPES', 2225),
    ('CUB_OSP_1', 'Валюты', 'DICT_CURR', 2557),
    ('CUB_OSP_1', 'Контракты', 'DICT_CONTRACT', 2636),
    ('CUB_OSP_1', 'МВЗ', 'DICT_MVZ', 2572),
    ('CUB_OSP_1', 'Период', 'DICT_PERIOD', 2552),
    ('CUB_OSP_1', 'Показатели', 'DICT_INDIC', 2565),
    ('CUB_OSP_1', 'Статьи', 'DICT_ARTIC', 2568),
    ('CUB_OSP_1', 'Сценарии', 'DICT_SCENAR', 2555),
    ('CUB_OSP_1', 'ЦФО', 'DICT_TSFO', 2570),
    ('CUB_OSP_1', 'Элементы затрат', 'DICT_COST', 2559),
    ('CUB_OSP_1', 'Год', 'DICT_YEAR', 2554);

-- Загружаем элементы выбора для измерений
INSERT INTO dimension_elements (cube_id, dim_id, elem_key, elem_name) VALUES
    ('CUB_OSP_1', 'DICT_INDICATOR_DATA_TYPES', '1', 'Число'),
    ('CUB_OSP_1', 'DICT_CURR', '1', 'Валюты договора'),
    ('CUB_OSP_1', 'DICT_CONTRACT', '1', 'Без учета контракта'),
    ('CUB_OSP_1', 'DICT_MVZ', '1', '0. Орг. в целом'),
    ('CUB_OSP_1', 'DICT_PERIOD', '1', 'P0'),
    ('CUB_OSP_1', 'DICT_INDIC', '4', 'Показатели по счетам'),
    ('CUB_OSP_1', 'DICT_ARTIC', '1', 'Средний курс за период'),
    ('CUB_OSP_1', 'DICT_SCENAR', '1', 'Бюджет'),
    ('CUB_OSP_1', 'DICT_TSFO', '1', 'Без учета ЦФО'),
    ('CUB_OSP_1', 'DICT_YEAR', '1', '2018');

-- Выборка данных для проверки
SELECT 'Таблица кубов:' AS table_name, * FROM cubes
UNION ALL
SELECT 'Таблица измерений:', cube_id, dim_name, dim_id, CAST(dim_key AS VARCHAR) FROM cube_dimensions
UNION ALL
SELECT 'Таблица элементов:', cube_id, dim_id, elem_key, elem_name FROM dimension_elements;

import json
import os

def extract_cubes_and_dictionaries(json_file):
    """Извлекает информацию о кубах и словарях из JSON файла"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Собираем информацию о кубах
    cubes_info = {}
    blocks = data.get('blocks', [])
    
    for block in blocks:
        receiver = block.get('receiver', {})
        if receiver:
            cube_id = receiver.get('cube_id')
            cube_name = receiver.get('cube_name')
            cube_key = receiver.get('cube_key')
            
            if cube_id not in cubes_info:
                cubes_info[cube_id] = {
                    'name': cube_name,
                    'key': cube_key,
                    'dims': []
                }
            
            # Собираем измерения
            for dim in receiver.get('dims', []):
                dim_info = {
                    'name': dim.get('name'),
                    'id': dim.get('id'),
                    'key': dim.get('key'),
                    'selection': dim.get('selection'),
                    'advanced_filter': dim.get('advanced_filter')
                }
                cubes_info[cube_id]['dims'].append(dim_info)
    
    # Получаем словари
    dictionaries_info = data.get('dictionaries', {})
    
    return cubes_info, dictionaries_info

def generate_sql(cubes_info, dictionaries_info):
    """Генерирует SQL скрипт для создания таблиц"""
    
    sql = []
    sql.append("-- Генерируемые таблицы для FSIGHT алгоритмов")
    sql.append("-- Автогенерировано на основе TEST_ALG.json\n")
    
    # Таблица кубов
    sql.append("-- Таблица кубов")
    sql.append("CREATE TABLE cubes (\n")
    sql.append("    cube_id VARCHAR(50) PRIMARY KEY,\n")
    sql.append("    cube_name VARCHAR(255) NOT NULL,\n")
    sql.append("    cube_key INT NOT NULL\n");
    sql.append(");\n\n")
    
    # Таблица измерений кубов
    sql.append("-- Таблица измерений кубов\n")
    sql.append("CREATE TABLE cube_dimensions (\n")
    sql.append("    id INT IDENTITY(1,1) PRIMARY KEY,\n")
    sql.append("    cube_id VARCHAR(50) NOT NULL,\n")
    sql.append("    dim_name VARCHAR(255) NOT NULL,\n")
    sql.append("    dim_id VARCHAR(50) NOT NULL,\n")
    sql.append("    dim_key INT NOT NULL,\n")
    sql.append("    FOREIGN KEY (cube_id) REFERENCES cubes(cube_id)\n");
    sql.append(");\n\n")
    
    # Таблица элементов выбора для измерений
    sql.append("-- Таблица элементов выбора для измерений\n")
    sql.append("CREATE TABLE dimension_elements (\n")
    sql.append("    id INT IDENTITY(1,1) PRIMARY KEY,\n")
    sql.append("    cube_id VARCHAR(50) NOT NULL,\n")
    sql.append("    dim_id VARCHAR(50) NOT NULL,\n")
    sql.append("    elem_key VARCHAR(50) NOT NULL,\n")
    sql.append("    elem_name VARCHAR(255) NOT NULL,\n")
    sql.append("    FOREIGN KEY (cube_id) REFERENCES cubes(cube_id)\n");
    sql.append(");\n\n")
    
    # Таблица словарей
    sql.append("-- Таблица словарей\n")
    sql.append("CREATE TABLE dictionaries (\n")
    sql.append("    dict_key INT PRIMARY KEY,\n")
    sql.append("    dict_id VARCHAR(50) NOT NULL,\n")
    sql.append("    dict_name VARCHAR(255) NOT NULL\n");
    sql.append(");\n\n")
    
    # Таблица атрибутов словарей
    sql.append("-- Таблица атрибутов словарей\n")
    sql.append("CREATE TABLE dictionary_attributes (\n")
    sql.append("    id INT IDENTITY(1,1) PRIMARY KEY,\n")
    sql.append("    dict_key INT NOT NULL,\n")
    sql.append("    attr_idx INT NOT NULL,\n")
    sql.append("    attr_id VARCHAR(50) NOT NULL,\n")
    sql.append("    attr_key INT NOT NULL,\n")
    sql.append("    attr_name VARCHAR(255) NOT NULL,\n")
    sql.append("    FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)\n");
    sql.append(");\n\n")
    
    # Таблица элементов словарей
    sql.append("-- Таблица элементов словарей\n")
    sql.append("CREATE TABLE dictionary_elements (\n")
    sql.append("    id INT IDENTITY(1,1) PRIMARY KEY,\n")
    sql.append("    dict_key INT NOT NULL,\n")
    sql.append("    elem_idx INT NOT NULL,\n")
    sql.append("    elem_id VARCHAR(50) NOT NULL,\n")
    sql.append("    elem_name VARCHAR(255) NOT NULL,\n")
    sql.append("    elem_parent INT NOT NULL,\n")
    sql.append("    elem_level_key INT NOT NULL,\n")
    sql.append("    FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)\n");
    sql.append(");\n\n")
    
    # Таблица атрибутов элементов словарей
    sql.append("-- Таблица атрибутов элементов словарей\n")
    sql.append("CREATE TABLE dictionary_element_attrs (\n")
    sql.append("    id INT IDENTITY(1,1) PRIMARY KEY,\n")
    sql.append("    dict_key INT NOT NULL,\n")
    sql.append("    elem_id VARCHAR(50) NOT NULL,\n")
    sql.append("    attr_id VARCHAR(50) NOT NULL,\n")
    sql.append("    attr_value VARCHAR(MAX) NOT NULL,\n")
    sql.append("    FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)\n");
    sql.append(");\n\n")
    
    # Вставка данных о кубах
    sql.append("-- Загружаем данные о кубах\n")
    for cube_id, info in cubes_info.items():
        sql.append(f"INSERT INTO cubes (cube_id, cube_name, cube_key) VALUES\n")
        sql.append(f"    ('{cube_id}', '{info['name']}', {info['key']});\n\n")
    
    # Вставка данных об измерениях
    sql.append("-- Загружаем данные об измерениях\n")
    for cube_id, info in cubes_info.items():
        for dim in info['dims']:
            sql.append(f"INSERT INTO cube_dimensions (cube_id, dim_name, dim_id, dim_key) VALUES\n")
            sql.append(f"    ('{cube_id}', '{dim['name']}', '{dim['id']}', {dim['key']});\n")
    sql.append("\n")
    
    # Вставка элементов выбора для измерений
    sql.append("-- Загружаем элементы выбора для измерений\n")
    for cube_id, info in cubes_info.items():
        for dim in info['dims']:
            if dim.get('selection') and dim['selection'].get('kind') == 'list':
                for elem in dim['selection'].get('elements', []):
                    sql.append(f"INSERT INTO dimension_elements (cube_id, dim_id, elem_key, elem_name) VALUES\n")
                    sql.append(f"    ('{cube_id}', '{dim['id']}', '{elem['key']}', '{elem['name']}');\n")
    sql.append("\n")
    
    # Вставка данных о словарях
    sql.append("-- Загружаем данные о словарях\n")
    for dict_key, dict_info in dictionaries_info.items():
        dict_key_int = int(dict_key)
        sql.append(f"INSERT INTO dictionaries (dict_key, dict_id, dict_name) VALUES\n")
        sql.append(f"    ({dict_key_int}, '{dict_info['id']}', '{dict_info['name']}');\n")
    sql.append("\n")
    
    # Вставка атрибутов словарей
    sql.append("-- Загружаем атрибуты словарей\n")
    for dict_key, dict_info in dictionaries_info.items():
        dict_key_int = int(dict_key)
        for attr in dict_info.get('attributes', []):
            sql.append(f"INSERT INTO dictionary_attributes (dict_key, attr_idx, attr_id, attr_key, attr_name) VALUES\n")
            sql.append(f"    ({dict_key_int}, {attr['idx']}, '{attr['id']}', {attr['key']}, '{attr['name']}');\n")
    sql.append("\n")
    
    # Вставка элементов словарей
    sql.append("-- Загружаем элементы словарей\n")
    for dict_key, dict_info in dictionaries_info.items():
        dict_key_int = int(dict_key)
        for elem in dict_info.get('elements', []):
            sql.append(f"INSERT INTO dictionary_elements (dict_key, elem_idx, elem_id, elem_name, elem_parent, elem_level_key) VALUES\n")
            sql.append(f"    ({dict_key_int}, {elem['idx']}, '{elem['id']}', '{elem['name']}', {elem['parent']}, {elem['level_key']});\n")
    sql.append("\n")
    
    # Вставка атрибутов элементов словарей
    sql.append("-- Загружаем атрибуты элементов словарей\n")
    for dict_key, dict_info in dictionaries_info.items():
        dict_key_int = int(dict_key)
        for elem in dict_info.get('elements', []):
            for attr_name, attr_value in elem.get('attrs', {}).items():
                sql.append(f"INSERT INTO dictionary_element_attrs (dict_key, elem_id, attr_id, attr_value) VALUES\n")
                sql.append(f"    ({dict_key_int}, '{elem['id']}', '{attr_name}', '{attr_value}');\n")
    sql.append("\n")
    
    return "\n".join(sql)

if __name__ == '__main__':
    json_file = 'TEST_ALG.json'
    
    # Извлекаем данные
    cubes_info, dictionaries_info = extract_cubes_and_dictionaries(json_file)
    
    # Генерируем SQL
    sql = generate_sql(cubes_info, dictionaries_info)
    
    # Сохраняем в файл
    os.makedirs('sql', exist_ok=True)
    output_file = 'sql/generate_cubes_dictionaries.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"SQL файл создан: {output_file}")
    print(f"Найдено кубов: {len(cubes_info)}")
    print(f"Найдено словарей: {len(dictionaries_info)}")

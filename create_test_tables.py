import json
import csv
import sqlite3
import os
from datetime import datetime

def extract_all_data(json_file):
    """Извлекает все данные из JSON файла"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Собираем кубы
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
                    'cube_id': cube_id,
                    'cube_name': cube_name,
                    'cube_key': cube_key,
                    'dims': []
                }
            
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
    
    # Получаем алгоритм и блоки
    algorithm = data.get('algorithm', {})
    params = algorithm.get('params', [])
    
    return cubes_info, dictionaries_info, algorithm, params

def create_cubes_json(cubes_info, output_dir):
    """Создает JSON файл для кубов"""
    
    # Таблица cubes (JSON)
    cubes_list = []
    for cube_id, info in cubes_info.items():
        cubes_list.append({
            'cube_id': info['cube_id'],
            'cube_name': info['cube_name'],
            'cube_key': info['cube_key']
        })
    
    with open(os.path.join(output_dir, 'cubes.json'), 'w', encoding='utf-8') as f:
        json.dump(cubes_list, f, ensure_ascii=False, indent=2)
    
    # Таблица cube_dimensions (JSON)
    dimensions_list = []
    for cube_id, info in cubes_info.items():
        for dim in info['dims']:
            dimensions_list.append({
                'cube_id': cube_id,
                'dim_name': dim['name'],
                'dim_id': dim['id'],
                'dim_key': dim['key']
            })
    
    with open(os.path.join(output_dir, 'cube_dimensions.json'), 'w', encoding='utf-8') as f:
        json.dump(dimensions_list, f, ensure_ascii=False, indent=2)
    
    # Таблица dimension_elements (JSON)
    elements_list = []
    for cube_id, info in cubes_info.items():
        for dim in info['dims']:
            if dim.get('selection') and dim['selection'].get('kind') == 'list':
                for elem in dim['selection'].get('elements', []):
                    elements_list.append({
                        'cube_id': cube_id,
                        'dim_id': dim['id'],
                        'elem_key': elem['key'],
                        'elem_name': elem['name']
                    })
    
    with open(os.path.join(output_dir, 'dimension_elements.json'), 'w', encoding='utf-8') as f:
        json.dump(elements_list, f, ensure_ascii=False, indent=2)
    
    return len(cubes_list), len(dimensions_list), len(elements_list)

def create_dictionaries_json(dictionaries_info, output_dir):
    """Создает JSON файл для словарей"""
    
    # Таблица dictionaries (JSON)
    dictionaries_list = []
    for dict_key, dict_info in dictionaries_info.items():
        dictionaries_list.append({
            'dict_key': int(dict_key),
            'dict_id': dict_info['id'],
            'dict_name': dict_info['name']
        })
    
    with open(os.path.join(output_dir, 'dictionaries.json'), 'w', encoding='utf-8') as f:
        json.dump(dictionaries_list, f, ensure_ascii=False, indent=2)
    
    # Таблица dictionary_attributes (JSON)
    attrs_list = []
    for dict_key, dict_info in dictionaries_info.items():
        for attr in dict_info.get('attributes', []):
            attrs_list.append({
                'dict_key': int(dict_key),
                'attr_idx': attr['idx'],
                'attr_id': attr['id'],
                'attr_key': attr['key'],
                'attr_name': attr['name']
            })
    
    with open(os.path.join(output_dir, 'dictionary_attributes.json'), 'w', encoding='utf-8') as f:
        json.dump(attrs_list, f, ensure_ascii=False, indent=2)
    
    # Таблица dictionary_elements (JSON)
    elements_list = []
    for dict_key, dict_info in dictionaries_info.items():
        for elem in dict_info.get('elements', []):
            elements_list.append({
                'dict_key': int(dict_key),
                'elem_idx': elem['idx'],
                'elem_id': elem['id'],
                'elem_name': elem['name'],
                'elem_parent': elem['parent'],
                'elem_level_key': elem['level_key']
            })
    
    with open(os.path.join(output_dir, 'dictionary_elements.json'), 'w', encoding='utf-8') as f:
        json.dump(elements_list, f, ensure_ascii=False, indent=2)
    
    # Таблица dictionary_element_attrs (JSON)
    elem_attrs_list = []
    for dict_key, dict_info in dictionaries_info.items():
        for elem in dict_info.get('elements', []):
            for attr_name, attr_value in elem.get('attrs', {}).items():
                elem_attrs_list.append({
                    'dict_key': int(dict_key),
                    'elem_id': elem['id'],
                    'attr_id': attr_name,
                    'attr_value': attr_value
                })
    
    with open(os.path.join(output_dir, 'dictionary_element_attrs.json'), 'w', encoding='utf-8') as f:
        json.dump(elem_attrs_list, f, ensure_ascii=False, indent=2)
    
    return len(dictionaries_list), len(attrs_list), len(elements_list), len(elem_attrs_list)

def create_csv_files(cubes_info, dictionaries_info, output_dir):
    """Создает CSV файлы для удобного просмотра в Excel"""
    
    # cubes.csv
    with open(os.path.join(output_dir, 'cubes.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['cube_id', 'cube_name', 'cube_key'])
        for cube_id, info in cubes_info.items():
            writer.writerow([info['cube_id'], info['cube_name'], info['cube_key']])
    
    # cube_dimensions.csv
    with open(os.path.join(output_dir, 'cube_dimensions.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['cube_id', 'dim_name', 'dim_id', 'dim_key'])
        for cube_id, info in cubes_info.items():
            for dim in info['dims']:
                writer.writerow([cube_id, dim['name'], dim['id'], dim['key']])
    
    # dimension_elements.csv
    with open(os.path.join(output_dir, 'dimension_elements.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['cube_id', 'dim_id', 'elem_key', 'elem_name'])
        for cube_id, info in cubes_info.items():
            for dim in info['dims']:
                if dim.get('selection') and dim['selection'].get('kind') == 'list':
                    for elem in dim['selection'].get('elements', []):
                        writer.writerow([cube_id, dim['id'], elem['key'], elem['name']])
    
    # dictionaries.csv
    with open(os.path.join(output_dir, 'dictionaries.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['dict_key', 'dict_id', 'dict_name'])
        for dict_key, dict_info in dictionaries_info.items():
            writer.writerow([dict_key, dict_info['id'], dict_info['name']])
    
    # dictionary_attributes.csv
    with open(os.path.join(output_dir, 'dictionary_attributes.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['dict_key', 'attr_idx', 'attr_id', 'attr_key', 'attr_name'])
        for dict_key, dict_info in dictionaries_info.items():
            for attr in dict_info.get('attributes', []):
                writer.writerow([dict_key, attr['idx'], attr['id'], attr['key'], attr['name']])
    
    # dictionary_elements.csv
    with open(os.path.join(output_dir, 'dictionary_elements.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['dict_key', 'elem_idx', 'elem_id', 'elem_name', 'elem_parent', 'elem_level_key'])
        for dict_key, dict_info in dictionaries_info.items():
            for elem in dict_info.get('elements', []):
                writer.writerow([dict_key, elem['idx'], elem['id'], elem['name'], elem['parent'], elem['level_key']])
    
    # dictionary_element_attrs.csv
    with open(os.path.join(output_dir, 'dictionary_element_attrs.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['dict_key', 'elem_id', 'attr_id', 'attr_value'])
        for dict_key, dict_info in dictionaries_info.items():
            for elem in dict_info.get('elements', []):
                for attr_name, attr_value in elem.get('attrs', {}).items():
                    writer.writerow([dict_key, elem['id'], attr_name, attr_value])

def create_sqlite_db(cubes_info, dictionaries_info, output_dir):
    """Создает SQLite базу данных"""
    
    db_path = os.path.join(output_dir, 'fsight_cubes.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cubes (
            cube_id TEXT PRIMARY KEY,
            cube_name TEXT NOT NULL,
            cube_key INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cube_dimensions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cube_id TEXT NOT NULL,
            dim_name TEXT NOT NULL,
            dim_id TEXT NOT NULL,
            dim_key INTEGER NOT NULL,
            FOREIGN KEY (cube_id) REFERENCES cubes(cube_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dimension_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cube_id TEXT NOT NULL,
            dim_id TEXT NOT NULL,
            elem_key TEXT NOT NULL,
            elem_name TEXT NOT NULL,
            FOREIGN KEY (cube_id) REFERENCES cubes(cube_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionaries (
            dict_key INTEGER PRIMARY KEY,
            dict_id TEXT NOT NULL,
            dict_name TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dict_key INTEGER NOT NULL,
            attr_idx INTEGER NOT NULL,
            attr_id TEXT NOT NULL,
            attr_key INTEGER NOT NULL,
            attr_name TEXT NOT NULL,
            FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dict_key INTEGER NOT NULL,
            elem_idx INTEGER NOT NULL,
            elem_id TEXT NOT NULL,
            elem_name TEXT NOT NULL,
            elem_parent INTEGER NOT NULL,
            elem_level_key INTEGER NOT NULL,
            FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary_element_attrs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dict_key INTEGER NOT NULL,
            elem_id TEXT NOT NULL,
            attr_id TEXT NOT NULL,
            attr_value TEXT NOT NULL,
            FOREIGN KEY (dict_key) REFERENCES dictionaries(dict_key)
        )
    ''')
    
    # Вставляем данные о кубах
    for cube_id, info in cubes_info.items():
        cursor.execute(
            'INSERT INTO cubes (cube_id, cube_name, cube_key) VALUES (?, ?, ?)',
            (info['cube_id'], info['cube_name'], info['cube_key'])
        )
    
    # Вставляем данные об измерениях
    for cube_id, info in cubes_info.items():
        for dim in info['dims']:
            cursor.execute(
                'INSERT INTO cube_dimensions (cube_id, dim_name, dim_id, dim_key) VALUES (?, ?, ?, ?)',
                (cube_id, dim['name'], dim['id'], dim['key'])
            )
    
    # Вставляем элементы выбора
    for cube_id, info in cubes_info.items():
        for dim in info['dims']:
            if dim.get('selection') and dim['selection'].get('kind') == 'list':
                for elem in dim['selection'].get('elements', []):
                    cursor.execute(
                        'INSERT INTO dimension_elements (cube_id, dim_id, elem_key, elem_name) VALUES (?, ?, ?, ?)',
                        (cube_id, dim['id'], elem['key'], elem['name'])
                    )
    
    # Вставляем данные о словарях
    for dict_key, dict_info in dictionaries_info.items():
        cursor.execute(
            'INSERT INTO dictionaries (dict_key, dict_id, dict_name) VALUES (?, ?, ?)',
            (dict_key, dict_info['id'], dict_info['name'])
        )
    
    # Вставляем атрибуты словарей
    for dict_key, dict_info in dictionaries_info.items():
        for attr in dict_info.get('attributes', []):
            cursor.execute(
                'INSERT INTO dictionary_attributes (dict_key, attr_idx, attr_id, attr_key, attr_name) VALUES (?, ?, ?, ?, ?)',
                (dict_key, attr['idx'], attr['id'], attr['key'], attr['name'])
            )
    
    # Вставляем элементы словарей
    for dict_key, dict_info in dictionaries_info.items():
        for elem in dict_info.get('elements', []):
            cursor.execute(
                'INSERT INTO dictionary_elements (dict_key, elem_idx, elem_id, elem_name, elem_parent, elem_level_key) VALUES (?, ?, ?, ?, ?, ?)',
                (dict_key, elem['idx'], elem['id'], elem['name'], elem['parent'], elem['level_key'])
            )
    
    # Вставляем атрибуты элементов
    for dict_key, dict_info in dictionaries_info.items():
        for elem in dict_info.get('elements', []):
            for attr_name, attr_value in elem.get('attrs', {}).items():
                # Преобразуем список/объект в JSON строку
                if isinstance(attr_value, (list, dict)):
                    attr_value = json.dumps(attr_value, ensure_ascii=False)
                cursor.execute(
                    'INSERT INTO dictionary_element_attrs (dict_key, elem_id, attr_id, attr_value) VALUES (?, ?, ?, ?)',
                    (dict_key, elem['id'], attr_name, str(attr_value))
                )
    
    conn.commit()
    
    # Показываем статистику
    stats = {}
    for table in ['cubes', 'cube_dimensions', 'dimension_elements', 'dictionaries', 
                  'dictionary_attributes', 'dictionary_elements', 'dictionary_element_attrs']:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        stats[table] = cursor.fetchone()[0]
    
    conn.close()
    
    return stats

def main():
    json_file = 'TEST_ALG.json'
    output_dir = 'tables'
    
    # Создаем директорию
    os.makedirs(output_dir, exist_ok=True)
    
    # Извлекаем данные
    print("Чтение JSON файла...")
    cubes_info, dictionaries_info, algorithm, params = extract_all_data(json_file)
    
    # Создаем JSON файлы
    print("\nСоздание JSON файлов...")
    cubes_json, dims_json, elems_json = create_cubes_json(cubes_info, output_dir)
    dicts_json, attrs_json, dict_elems_json, dict_elem_attrs_json = create_dictionaries_json(dictionaries_info, output_dir)
    print(f"  cubes.json: {cubes_json} записей")
    print(f"  cube_dimensions.json: {dims_json} записей")
    print(f"  dimension_elements.json: {elems_json} записей")
    print(f"  dictionaries.json: {dicts_json} записей")
    print(f"  dictionary_attributes.json: {attrs_json} записей")
    print(f"  dictionary_elements.json: {dict_elems_json} записей")
    print(f"  dictionary_element_attrs.json: {dict_elem_attrs_json} записей")
    
    # Создаем CSV файлы
    print("\nСоздание CSV файлов...")
    create_csv_files(cubes_info, dictionaries_info, output_dir)
    print("  Создано 6 CSV файлов")
    
    # Создаем SQLite базу
    print("\nСоздание SQLite базы данных...")
    stats = create_sqlite_db(cubes_info, dictionaries_info, output_dir)
    print("  Количество записей:")
    for table, count in stats.items():
        print(f"    {table}: {count}")
    
    print(f"\nГотово! Файлы сохранены в папку: {output_dir}")
    print("\nДля просмотра:")
    print("  - JSON файлы: открыть в любом текстовом редакторе")
    print("  - CSV файлы: открыть в Excel")
    print("  - SQLite база: используйте DB Browser for SQLite или sqlite3")

if __name__ == '__main__':
    main()

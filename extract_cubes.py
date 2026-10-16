import json
import os

with open('TEST_ALG.json', 'r', encoding='utf-8') as f:
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

# Выводим информацию
for cube_id, info in cubes_info.items():
    print(f"\n{'='*80}")
    print(f"КУБ: {cube_id}")
    print(f"Название: {info['name']}")
    print(f"Ключ: {info['key']}")
    print(f"\nИзмерения:")
    for dim in info['dims']:
        print(f"  - {dim['name']} ({dim['id']}, ключ: {dim['key']})")
        if dim.get('selection'):
            sel = dim['selection']
            print(f"    Выборка: {sel.get('kind')}")
            if sel.get('elements'):
                for elem in sel['elements']:
                    print(f"      * {elem['key']}: {elem['name']}")

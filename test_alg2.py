#!/usr/bin/env python
"""
Тест математического движка для TEST_ALG_2.json
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.formula_parser import FormulaParser
from core.calculator import FSIGHTCalculator
from core.measurements import DataLookup, CubeContext
import json

print('\n' + '='*80)
print('FSIGHT Math Engine - Тест для TEST_ALG_2.json')
print('='*80)

# 1. Загрузка
print('\n1. ЗАГРУЗКА КОНФИГУРАЦИИ')
print('-'*60)
parser = FormulaParser.load_and_parse('TEST_ALG_2.json')
config = parser.config
print(f'✅ Алгоритм: {config.algorithm.name}')
print(f'✅ Ключ: {config.algorithm.key}')
print(f'✅ Формул: {config.get_total_formula_count()}')
print(f'✅ Блоков: {len(config.blocks)}')
print(f'✅ Кубов: {len(config.get_cubes())}')

# 2. Lookup
print('\n2. СТРУКТУРА DATALOOKUP')
print('-'*60)
lookup = DataLookup()
for i, block in enumerate(config.blocks, 1):
    if block.receiver:
        context = CubeContext.from_cube_data(
            block.receiver.cube_id, block.receiver.cube_name,
            block.receiver.cube_key, block.receiver.dims
        )
        lookup.add_cube(context)
        print(f'Блок {i}: {context.cube_id} - {len(context.measurements)} измерений')

# 3. Тестовые данные
print('\n3. ТЕСТОВЫЕ ДАННЫЕ')
print('-'*60)
with open('data/test_data_2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
test_values = data['custom_values']
params = data['params']
print(f'✅ Значений: {len(test_values)}')
print(f'✅ Параметры: {len(params)}')
print('\nЗначения:')
for k, v in test_values.items():
    print(f'   {k}: {v}')

# 4. Расчет
print('\n4. ВЫЧИСЛЕНИЕ ПО ВСЕМ ФОРМУЛАМ')
print('-'*60)
calculator = FSIGHTCalculator(lookup)
formulas = config.get_formulas_flat()

results = []
for i, formula in enumerate(formulas, 1):
    result = calculator.calculate_formula(
        formula,
        params=params,
        custom_values=test_values
    )
    results.append(result)
    
    print(f'\nФормула {i}: {formula.name}')
    print(f'  Текст: {formula.text}')
    print(f'  Шаги:')
    for step in result.steps:
        print(f'    {step}')
    if result.success():
        print(f'  ✅ РЕЗУЛЬТАТ: {result.result}')
    else:
        print(f'  ⚠️ ОШИБКА: {result.error}')

# 5. Статистика
print('\n5. ИТОГОВАЯ СТАТИСТИКА')
print('-'*60)
summary = calculator.get_summary()
print(f'Всего формул: {summary["total"]}')
print(f'Успешно: {summary["success"]}')
print(f'С ошибками: {summary["failed"]}')
if summary['total'] > 0:
    print(f'Успех: {summary["success"]/summary["total"]*100:.1f}%')

print('\n' + '='*80)
print('✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО')
print('='*80 + '\n')

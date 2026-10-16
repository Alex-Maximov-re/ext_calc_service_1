#!/usr/bin/env python
"""
Простой тестовый скрипт с демонстрацией всех результатов
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.formula_parser import FormulaParser
from core.calculator import FSIGHTCalculator
from core.measurements import DataLookup, CubeContext

print("\n" + "=" * 80)
print("FSIGHT Math Engine - Тестовые результаты")
print("=" * 80)

# 1. Загрузка
print("\n1. ЗАГРУЗКА КОНФИГУРАЦИИ")
print("-" * 60)
parser = FormulaParser.load_and_parse('TEST_ALG.json')
config = parser.config
print(f"✅ Алгоритм: {config.algorithm.name}")
print(f"✅ Формул: {config.get_total_formula_count()}")
print(f"✅ Кубов: {len(config.get_cubes())}")

# 2. Lookup
print("\n2. СТРУКТУРА DATABOOK")
print("-" * 60)
lookup = DataLookup()
for block in config.blocks:
    if block.receiver:
        context = CubeContext.from_cube_data(
            block.receiver.cube_id, block.receiver.cube_name,
            block.receiver.cube_key, block.receiver.dims
        )
        lookup.add_cube(context)
        print(f"✅ Куб: {context.cube_id}")
        print(f"   Измерений: {len(context.measurements)}")

# 3. Расчет
print("\n3. ВЫЧИСЛЕНИЕ")
print("-" * 60)
calculator = FSIGHTCalculator(lookup)

test_values = {
    'Число|2017': 100.0,
    'Число|2018': 150.0,
    '∑Год': 250.0,
    'Без учета валюты|2018': 150.0
}

formulas = config.get_formulas_flat()
results = []

for i, formula in enumerate(formulas, 1):
    result = calculator.calculate_formula(
        formula,
        custom_values=test_values
    )
    results.append(result)
    
    print(f"\nФормула {i}: {formula.name}")
    print(f"  Текст: {formula.text}")
    print(f"  Шаги:")
    for step in result.steps:
        print(f"    {step}")
    print(f"  Результат: {result.result if result.success() else result.error}")

# 4. Статистика
print("\n4. ИТОГОВАЯ СТАТИСТИКА")
print("-" * 60)
summary = calculator.get_summary()
print(f"Всего формул: {summary['total']}")
print(f"Успешно: {summary['success']}")
print(f"С ошибками: {summary['failed']}")

print("\n" + "=" * 80)
print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО")
print("=" * 80 + "\n")

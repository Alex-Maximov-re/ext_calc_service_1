#!/usr/bin/env python
"""
Тестирование калькулятора FSIGHT

Пример использования с TEST_ALG.json
"""

from core.formula_parser import FormulaParser
from core.calculator import FSIGHTCalculator
from core.measurements import DataLookup, CubeContext


def main():
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ КАЛЬКУЛЯТОРА FSIGHT")
    print("=" * 80)
    
    # 1. Загрузка конфигурации
    print("\n1. Загрузка конфигурации...")
    json_file = 'TEST_ALG.json'
    parser = FormulaParser.load_and_parse(json_file)
    config = parser.config
    
    print(f"   Алгоритм: {config.algorithm.name}")
    print(f"   Кубов: {len(config.get_cubes())}")
    print(f"   Формул: {config.get_total_formula_count()}")
    
    # 2. Создание lookup с тестовыми данными
    print("\n2. Создание lookup с тестовыми данными...")
    lookup = DataLookup()
    
    # Добавление кубов из конфигурации
    for block in config.blocks:
        if block.receiver:
            cube_context = CubeContext.from_cube_data(
                cube_id=block.receiver.cube_id,
                cube_name=block.receiver.cube_name,
                cube_key=block.receiver.cube_key,
                dims=block.receiver.dims
            )
            lookup.add_cube(cube_context)
            print(f"   Добавлен куб: {cube_context.cube_id}")
    
    # 3. Добавление тестовых значений
    print("\n3. Добавление тестовых значений...")
    test_values = {
        'Число|2017': 100.0,
        'Число|2018': 150.0,
        'Число|2017|P1': 120.0,
        '∑Год': 250.0,  # Сумма по годам
        'Без учета валюты|2018': 150.0,  # Для формулы с параметрами
        '2018': 150.0  # Для параметра {Параметр Год (блок)}
    }
    
    # Параметры для подстановки
    params = {
        'Параметр Год (блок)': 2018
    }
    
    for key, value in test_values.items():
        print(f"   {key} = {value}")
    
    # 4. Создание калькулятора
    print("\n4. Создание калькулятора...")
    calculator = FSIGHTCalculator(lookup)
    
    # 5. Вычисление всех формул с кастомными значениями
    print("\n5. Вычисление всех формул...")
    results = calculator.calculate_all(config, custom_values=test_values)
    
    # 5b. Вычисление формулы 2 с параметрами
    print("\n5b. Вычисление формулы 2 с параметрами...")
    formula2 = config.blocks[0].formulas[1]  # Вторая формула
    result2 = calculator.calculate_formula(formula2, params=params, custom_values=test_values)
    print(f"   {result2.get_detailed_report()}")
    
    # 6. Вывод результатов
    print("\n")
    calculator.print_results()
    
    # 7. Статистика
    print("\n" + "=" * 80)
    print("СТАТИСТИКА")
    print("=" * 80)
    summary = calculator.get_summary()
    print(f"Всего формул: {summary['total']}")
    print(f"Успешно: {summary['success']}")
    print(f"С ошибками: {summary['failed']}")
    
    if summary['failed'] > 0:
        print("\nФормулы с ошибками:")
        for r in summary['results']:
            if 'ERROR' in str(r['result']):
                print(f"  - {r['name']}: {r['result']}")
    
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

#!/usr/bin/env python
"""
Детальный тестовый скрипт для FSIGHT Math Engine

Выводит полную информацию о каждом шаге вычислений.
"""

import json
import sys
from pathlib import Path

# Добавляем путь
sys.path.insert(0, str(Path(__file__).parent))

from core.formula_parser import FormulaParser
from core.calculator import FSIGHTCalculator
from core.orchestrator import DAGCalculator
from core.measurements import DataLookup, CubeContext


def print_header(title: str):
    """Вывод заголовка секции"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subheader(title: str):
    """Вывод заголовка subsection"""
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print("-" * 60)


def test_configuration_loading():
    """Тест 1: Загрузка конфигурации"""
    print_header("Тест 1: ЗАГРУЗКА КОНФИГУРАЦИИ")
    
    parser = FormulaParser.load_and_parse('TEST_ALG.json')
    config = parser.config
    
    print(f"✅ Алгоритм загружен:")
    print(f"   ID: {config.algorithm.id}")
    print(f"   Название: {config.algorithm.name}")
    print(f"   Ключ: {config.algorithm.key}")
    print(f"   Параметры алгоритма: {len(config.algorithm.params)}")
    
    for param in config.algorithm.params:
        print(f"      - {param.name} ({param.id})")
    
    print(f"\n✅ Блоков расчёта: {len(config.blocks)}")
    for block in config.blocks:
        print(f"   Блок {block.seq}: {block.name} ({block.id})")
        print(f"      Формул: {len(block.formulas)}")
    
    print(f"\n✅ Кубов: {len(config.get_cubes())}")
    for cube in config.get_cubes():
        print(f"   - {cube}")
    
    print(f"\n✅ Всего формул: {config.get_total_formula_count()}")
    
    return parser, config


def test_lookup_structure():
    """Тест 2: Структура данных lookup"""
    print_header("Тест 2: СТРУКТУРА ДАННЫХ LOOKUP")
    
    parser, config = test_configuration_loading()
    
    lookup = DataLookup()
    
    for block in config.blocks:
        if block.receiver:
            cube_context = CubeContext.from_cube_data(
                cube_id=block.receiver.cube_id,
                cube_name=block.receiver.cube_name,
                cube_key=block.receiver.cube_key,
                dims=block.receiver.dims
            )
            lookup.add_cube(cube_context)
            
            print(f"\n✅ Куб: {cube_context.cube_id}")
            print(f"   Название: {cube_context.cube_name}")
            print(f"   Ключ: {cube_context.cube_key}")
            print(f"   Измерений: {len(cube_context.measurements)}")
            
            print("\n   Измерения:")
            for i, meas in enumerate(cube_context.measurements, 1):
                print(f"      {i}. {meas.dim_name} ({meas.dim_id})")
                print(f"         Ключ: {meas.key}, Значение: {meas.elem_name}")
    
    return lookup


def test_formula_details():
    """Тест 3: Детализация формул"""
    print_header("Тест 3: ДЕТАЛИЗАЦИЯ ФОРМУЛ")
    
    parser, config = test_configuration_loading()
    
    formulas = config.get_formulas_flat()
    
    for i, formula in enumerate(formulas, 1):
        print_subheader(f"Формула {i}: {formula.name}")
        print(f"   ID: {formula.id}")
        print(f"   Ключ: {formula.key}")
        print(f"   Текст: {formula.text}")
        print(f"   Text_inner: {formula.text_inner}")
        print(f"   Параметры: {formula.get_parameter_names()}")
        print(f"   Кубы: {formula.get_cube_refs()}")
        print(f"   Успешность: {formula.is_exclusive}")
        
        if formula.terms:
            print(f"\n   Термов: {len(formula.terms)}")
            for term in formula.terms:
                print(f"      Терм {term.n}:")
                print(f"         Текст: {term.text}")
                print(f"         Inner: {term.inner}")
                print(f"         Self: {term.self_ref}, Lag: {term.lag}")
                print(f"         Сечения: {len(term.slice)}")
                for slice in term.slice:
                    print(f"            - {slice.dim} ({slice.dim_id})")
                    print(f"              Выбор: {slice.get_selection()}")


def test_calculation_with_values():
    """Тест 4: Расчет с тестовыми значениями"""
    print_header("Тест 4: РАСЧЕТ С ТЕСТОВЫМИ ЗНАЧЕНИЯМИ")
    
    parser, config = test_configuration_loading()
    
    lookup = test_lookup_structure()
    
    print("\n✅ Добавление тестовых значений...")
    test_values = {
        'Число|2017': 100.0,
        'Число|2018': 150.0,
        'Число|2017|P1': 120.0,
        '∑Год': 250.0,
        'Без учета валюты|2018': 150.0,
        '2018': 150.0
    }
    
    for key, value in test_values.items():
        print(f"   {key:40} = {value}")
    
    # Создание калькулятора
    calculator = FSIGHTCalculator(lookup)
    
    print("\n🔢 ВЫЧИСЛЕНИЕ КАЖДОЙ ФОРМУЛЫ ПО ОЧЕРЕДИ:")
    print("=" * 80)
    
    formulas = config.get_formulas_flat()
    for i, formula in enumerate(formulas, 1):
        print(f"\n--- ФОРМУЛА {i}: {formula.name} ---")
        print(f"Текст: {formula.text}")
        
        result = calculator.calculate_formula(
            formula,
            params={'Параметр Год (блок)': 2018},
            custom_values=test_values
        )
        
        print("\nШаги расчета:")
        for step in result.steps:
            print(f"  {step}")
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        if result.success():
            print(f"  ✅ Успешно: {result.result}")
        else:
            print(f"  ⚠️  Ошибка: {result.error}")
        
        print("\n" + "=" * 80)


def test_full_integration():
    """Тест 5: Полная интеграция"""
    print_header("Тест 5: ПОЛНАЯ ИНТЕГРАЦИЯ")
    
    parser, config = test_configuration_loading()
    lookup = test_lookup_structure()
    
    calculator = FSIGHTCalculator(lookup)
    orchestrator = DAGCalculator(calculator)
    
    test_values = {
        'Число|2017': 100.0,
        'Число|2018': 150.0,
        'Число|2017|P1': 120.0,
        '∑Год': 250.0,
        'Без учета валюты|2018': 150.0,
        '2018': 150.0
    }
    
    print("\n📊 ПОРЯДОК ВЫЧИСЛЕНИЙ (DAG):")
    print("-" * 60)
    
    results = orchestrator.execute_all(
        config,
        custom_values=test_values,
        params={'Параметр Год (блок)': 2018}
    )
    
    print("\n" + "=" * 80)
    print("📈 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 80)
    
    summary = calculator.get_summary()
    print(f"\nВсего формул: {summary['total']}")
    print(f"Успешно: {summary['success']}")
    print(f"С ошибками: {summary['failed']}")
    print(f"Успех: {summary['success']/summary['total']*100:.1f}%")
    
    print("\n📋 ДЕТАЛИЗАЦИЯ ПО ФОРМУЛАМ:")
    print("-" * 60)
    
    for r in summary['results']:
        status = "✅" if 'ERROR' not in str(r['result']) else "⚠️"
        print(f"{status} {r['name']}: {r['result']}")


def main():
    """Главная функция"""
    print("\n" + "🎌" * 40)
    print("  FSIGHT Math Engine - Детальные тестовые запуски")
    print("🎌" * 40)
    
    test_configuration_loading()
    test_lookup_structure()
    test_formula_details()
    test_calculation_with_values()
    test_full_integration()
    
    print("\n" + "=" * 80)
    print("  ✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
    print("=" * 80)


if __name__ == '__main__':
    main()

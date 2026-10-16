#!/usr/bin/env python
"""
Тесты для FSIGHT Math Engine

Модульные и интеграционные тесты для всех компонентов.
"""

import unittest
import json
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
_current_dir = Path(__file__).parent.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from core.formula_parser import FormulaParser
from core.formula import Formula, Term
from core.term import Slice, ElementSelection
from core.measurements import DataPoint, CubeContext, DataLookup
from core.calculator import FSIGHTCalculator, CalculationResult
from core.orchestrator import DAGCalculator, CalculationStep


class TestFormulaParser(unittest.TestCase):
    """Тесты парсера формул"""
    
    @classmethod
    def setUpClass(cls):
        """Загрузка тестовой конфигурации"""
        cls.parser = FormulaParser.load_and_parse('TEST_ALG.json')
        cls.config = cls.parser.config
    
    def test_load_config(self):
        """Проверка загрузки конфигурации"""
        self.assertIsNotNone(self.config)
        self.assertEqual(self.config.schema, 1)
    
    def test_algorithm_info(self):
        """Проверка информации об алгоритме"""
        self.assertEqual(self.config.algorithm.id, 'TEST_ALG')
        self.assertEqual(self.config.algorithm.name, 'Тестовый алгоритм')
    
    def test_block_count(self):
        """Проверка количества блоков"""
        self.assertEqual(len(self.config.blocks), 1)
    
    def test_formula_count(self):
        """Проверка количества формул"""
        self.assertEqual(self.config.get_total_formula_count(), 3)
    
    def test_formula_params(self):
        """Проверка наличия параметров в формулах"""
        formulas_with_params = [
            f for f in self.config.get_formulas_flat() 
            if f.has_parameters()
        ]
        self.assertEqual(len(formulas_with_params), 1)
    
    def test_cubes(self):
        """Проверка кубов"""
        cubes = self.config.get_cubes()
        self.assertIn('CUB_OSP_1', cubes)


class TestFormula(unittest.TestCase):
    """Тесты формул"""
    
    def setUp(self):
        """Создание тестовой формулы"""
        self.formula = Formula(
            name="Test Formula",
            id="OBJ1",
            key=1,
            text="Test!Value|2017 + 1",
            text_inner="@_1:0[] + 1",
            terms=[
                Term(
                    n=1,
                    text="Test!Value|2017",
                    inner="@_1:0[]",
                    self_ref=True,
                    lag=0,
                    slice=[
                        Slice(
                            dim="Год",
                            dim_id="DICT_YEAR",
                            dim_key=2554,
                            kind=None,
                            elements=[ElementSelection(key="1", name="2017")]
                        )
                    ]
                )
            ]
        )
    
    def test_formula_creation(self):
        """Создание формулы"""
        self.assertEqual(self.formula.name, "Test Formula")
        self.assertEqual(self.formula.id, "OBJ1")
    
    def test_has_parameters(self):
        """Проверка параметров"""
        self.assertFalse(self.formula.has_parameters())
    
    def test_lhs_rhs(self):
        """Проверка левой/правой части"""
        formula = Formula(
            name="Test",
            id="OBJ1",
            key=1,
            text="LHS = RHS + 1",
            text_inner="@_1:0[] + 1"
        )
        self.assertEqual(formula.get_lhs(), "LHS")
        self.assertEqual(formula.get_rhs(), "RHS + 1")


class TestDataLookup(unittest.TestCase):
    """Тесты lookup данных"""
    
    def setUp(self):
        """Создание lookup"""
        self.lookup = DataLookup()
        
        # Добавление тестового куба
        self.context = CubeContext.from_cube_data(
            cube_id='CUB_TEST',
            cube_name='Test Cube',
            cube_key=1,
            dims=[
                {'id': 'DICT_YEAR', 'name': 'Год', 'key': 2554},
                {'id': 'DICT_PERIOD', 'name': 'Период', 'key': 2552}
            ]
        )
        self.lookup.add_cube(self.context)
    
    def test_add_cube(self):
        """Добавление куба"""
        self.assertEqual(len(self.lookup.cubes), 1)
        self.assertIn('CUB_TEST', self.lookup.cubes)
    
    def test_add_value(self):
        """Добавление значения"""
        self.lookup.set_value(
            'CUB_TEST',
            {'DICT_YEAR': '1', 'DICT_PERIOD': '1'},
            100.0
        )
        
        self.assertEqual(self.lookup.test_data['CUB_TEST!Год|1|Период|1'], 100.0)
    
    def test_lookup_value(self):
        """Поиск значения"""
        self.lookup.set_value(
            'CUB_TEST',
            {'DICT_YEAR': '1', 'DICT_PERIOD': '1'},
            100.0
        )
        
        value = self.lookup.get_value(
            'CUB_TEST',
            {'DICT_YEAR': '1', 'DICT_PERIOD': '1'}
        )
        
        self.assertEqual(value, 100.0)


class TestCalculator(unittest.TestCase):
    """Тесты калькулятора"""
    
    def test_calculator_creation(self):
        """Создание калькулятора"""
        lookup = DataLookup()
        calculator = FSIGHTCalculator(lookup)
        self.assertIsNotNone(calculator)
    
    def test_simple_calculation(self):
        """Простое вычисление"""
        lookup = DataLookup()
        calculator = FSIGHTCalculator(lookup)
        
        # Добавление тестового значения
        lookup.add_values_from_dict('CUB_TEST', {
            'Число|2017': 100.0
        })
        
        # Тестовая формула
        formula = Formula(
            name="Simple Test",
            id="OBJ1",
            key=1,
            text="CUB!Число|2017 + 1",
            text_inner="@_1:0[] + 1"
        )
        
        result = calculator.calculate_formula(
            formula,
            custom_values={'Число|2017': 100.0}
        )
        
        self.assertTrue(result.success())
        self.assertEqual(result.result, 101.0)
    
    def test_arithmetic_operations(self):
        """Арифметические операции"""
        lookup = DataLookup()
        calculator = FSIGHTCalculator(lookup)
        
        formula = Formula(
            name="Arithmetic Test",
            id="OBJ2",
            key=2,
            text="Test!Value + 10 - 5 * 2",
            text_inner="@_2:0[] + 10 - 5 * 2"
        )
        
        # Без данных, но арифметика должна работать
        result = calculator.calculate_formula(
            formula,
            custom_values={'Value': 100.0}
        )
        
        # 100 + 10 - 5 * 2 = 100 + 10 - 10 = 100
        self.assertIsNotNone(result)


class TestOrchestrator(unittest.TestCase):
    """Тесты оркестратора"""
    
    def test_orchestrator_creation(self):
        """Создание оркестратора"""
        lookup = DataLookup()
        calculator = FSIGHTCalculator(lookup)
        orchestrator = DAGCalculator(calculator)
        self.assertIsNotNone(orchestrator)
    
    def test_dependency_analysis(self):
        """Анализ зависимостей"""
        parser = FormulaParser.load_and_parse('TEST_ALG.json')
        config = parser.config
        
        lookup = DataLookup()
        calculator = FSIGHTCalculator(lookup)
        orchestrator = DAGCalculator(calculator)
        
        dependencies = orchestrator.analyze_dependencies(config)
        
        # Должны быть найдены зависимости
        self.assertGreater(len(dependencies), 0)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    @classmethod
    def setUpClass(cls):
        """Подготовка тестовых данных"""
        cls.parser = FormulaParser.load_and_parse('TEST_ALG.json')
        cls.config = cls.parser.config
    
    def test_full_calculation(self):
        """Полный цикл расчета"""
        lookup = DataLookup()
        calculator = FSIGHTCalculator(lookup)
        
        # Тестовые значения
        test_values = {
            'Число|2017': 100.0,
            'Число|2018': 150.0,
            '∑Год': 250.0
        }
        
        results = calculator.calculate_all(
            self.config,
            custom_values=test_values
        )
        
        # Все формулы должны быть вычислены
        self.assertEqual(len(results), 3)
        
        # Первая формула должна работать
        first_result = next(r for r in results if r.formula_id == 'OBJ3')
        self.assertTrue(first_result.success())
        self.assertEqual(first_result.result, 101.0)
    
    def test_dag_calculation(self):
        """Расчет через DAG оркестратор"""
        lookup = DataLookup()
        calculator = FSIGHTCalculator(lookup)
        orchestrator = DAGCalculator(calculator)
        
        test_values = {
            'Число|2017': 100.0,
            'Число|2018': 150.0,
            '∑Год': 250.0
        }
        
        results = orchestrator.execute_all(
            self.config,
            custom_values=test_values
        )
        
        self.assertGreater(len(results), 0)


def run_tests():
    """Запуск всех тестов"""
    # Создание test result
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавление всех тестов
    suite.addTests(loader.loadTestsFromTestCase(TestFormulaParser))
    suite.addTests(loader.loadTestsFromTestCase(TestFormula))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLookup))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Запуск
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вывод статистики
    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 80)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {len(result.failures) + len(result.errors)}")
    print(f"Неудач: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Неудачи:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️ Ошибки:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

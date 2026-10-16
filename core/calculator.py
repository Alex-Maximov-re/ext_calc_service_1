"""
Вычислительное ядро FSIGHT

Калькулятор для выполнения формул с:
- Арифметическими операциями (+, -, *, /)
- Подстановкой параметров
- Обработкой точек данных
- Агрегацией (∑)
"""

import re
import math
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass

from .term import Term
from .formula import Formula
from .measurements import DataLookup, DataPoint, CubeContext
from .formula_parser import FormulaParser


@dataclass
class CalculationResult:
    """Результат вычисления формулы"""
    formula_id: str
    formula_name: str
    text: str
    steps: List[str]  # Шаги расчета
    result: Optional[float]
    error: Optional[str] = None
    
    def success(self) -> bool:
        return self.error is None
    
    def __str__(self) -> str:
        if self.success():
            return f"Formula({self.formula_id}): {self.result}"
        return f"Formula({self.formula_id}): ERROR - {self.error}"
    
    def get_detailed_report(self) -> str:
        """Детальный отчет о расчете"""
        lines = [
            f"Формула: {self.formula_name} ({self.formula_id})",
            f"Текст: {self.text}",
            "Шаги расчета:",
        ]
        for step in self.steps:
            lines.append(f"  {step}")
        
        if self.success():
            lines.append(f"Результат: {self.result}")
        else:
            lines.append(f"Ошибка: {self.error}")
        
        return "\n".join(lines)


class ArithmeticExpression:
    """Арифметическое выражение для парсинга"""
    
    # Паттерны для распознавания
    PATTERN_NUMBER = r'[-+]?\d+\.?\d*'
    PATTERN_OPERATOR = r'[+\-*/]'
    PATTERN_MEASUREMENT = r'(\S+)[!=\+\-\*/]'
    PATTERN_PARAM = r'\{([^}]+)\}'
    PATTERN_AGGREGATION = r'∑(\w+)'
    
    def __init__(self, text: str, data_lookup: DataLookup):
        self.text = text
        self.data_lookup = data_lookup
        self.parts = self._tokenize(text)
    
    def _tokenize(self, text: str) -> List[Dict[str, Any]]:
        """Разбить текст на токены"""
        tokens = []
        
        # Разделение на части по операторам
        parts = re.split(r'([+\-*/])', text)
        
        i = 0
        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue
            
            # Проверка на оператор
            if part in ['+', '-', '*', '/']:
                tokens.append({'type': 'operator', 'value': part})
                i += 1
                continue
            
            # Проверка на агрегацию
            agg_match = re.match(r'∑(\w+)', part)
            if agg_match:
                tokens.append({
                    'type': 'aggregation',
                    'operator': 'sum',
                    'dim': agg_match.group(1)
                })
                i += 1
                continue
            
            # Проверка на параметр
            if re.match(r'\{.*\}', part):
                param_match = re.search(self.PATTERN_PARAM, part)
                if param_match:
                    tokens.append({
                        'type': 'parameter',
                        'name': param_match.group(1)
                    })
                    i += 1
                    continue
            
            # Проверка на число
            if re.match(rf'^{self.PATTERN_NUMBER}$', part):
                tokens.append({
                    'type': 'number',
                    'value': float(part)
                })
                i += 1
                continue
            
            # Проверка на измерение (куб!измерение|фильтры)
            tokens.append({
                'type': 'measurement',
                'text': part
            })
            i += 1
        
        return tokens
    
    def substitute_parameters(self, params: Dict[str, float]) -> List[Dict[str, Any]]:
        """Подставить значения параметров"""
        result = []
        for token in self.parts:
            if token.get('type') == 'parameter':
                param_name = token['name']
                if param_name in params:
                    result.append({
                        'type': 'number',
                        'value': params[param_name]
                    })
                else:
                    result.append({
                        'type': 'parameter',
                        'name': param_name,
                        'error': f"Параметр '{param_name}' не найден"
                    })
            else:
                result.append(token)
        return result
    
    def lookup_measurement(self, token: Dict[str, Any], custom_values: Dict[str, float] = None) -> Optional[float]:
        """Получить значение измерения из lookup или кастомных значений
        
        Args:
            token: Токен измерения
            custom_values: Кастомные значения для lookup
            
        Returns:
            Значение или None
        """
        if token['type'] != 'measurement':
            return None
        
        measurement_text = token['text']
        
        # Сначала проверяем кастомные значения
        if custom_values:
            # Прямой поиск
            if measurement_text in custom_values:
                return custom_values[measurement_text]
            
            # Парсинг: Куб OSP 1!Число|2017
            # Разделяем по !
            if '!' in measurement_text:
                cube_part, measure_part = measurement_text.split('!', 1)
                cube_id = cube_part.strip()
                
                # Парсинг измерений из measure_part
                # Формат: Измерение|Фильтр1|Фильтр2
                parts = measure_part.split('|')
                if len(parts) >= 2:
                    measure_name = parts[0].strip()
                    filters = parts[1:]
                    
                    # Формируем варианты ключей для поиска
                    # Вариант 1: Измерение|фильтр1
                    if filters:
                        variant1 = f"{measure_name}|{filters[0].strip()}"
                        if variant1 in custom_values:
                            return custom_values[variant1]
                    
                    # Вариант 2: Измерение|фильтр1|фильтр2
                    if len(filters) >= 2:
                        variant2 = f"{measure_name}|{filters[0].strip()}|{filters[1].strip()}"
                        if variant2 in custom_values:
                            return custom_values[variant2]
                    
                    # Вариант 3: cube_id!измерение|фильтр1
                    if filters:
                        variant3 = f"{cube_id}!{measure_name}|{filters[0].strip()}"
                        if variant3 in custom_values:
                            return custom_values[variant3]
        
        return None
    
    def _try_lookup(self, key: str) -> Optional[float]:
        """Попробовать получить значение по ключу"""
        # Инициализация test данных если нет
        if not hasattr(self.data_lookup, 'test_data'):
            self.data_lookup.test_data = {}
        
        if key in self.data_lookup.test_data:
            return self.data_lookup.test_data[key]
        return None
    
    def evaluate(self, params: Dict[str, float] = None, custom_values: Dict[str, float] = None) -> Tuple[Optional[float], List[str]]:
        """
        Вычислить выражение
        
        Args:
            params: Параметры для подстановки
            custom_values: Кастомные значения для lookup
            
        Returns:
            (результат, шаги)
        """
        if params is None:
            params = {}
        if custom_values is None:
            custom_values = {}
            
        steps = []
        substituted = self.substitute_parameters(params)
        
        # Преобразование в числа и вычисление
        numbers = []
        operators = []
        
        for i, token in enumerate(substituted):
            if token.get('type') == 'number':
                numbers.append(token['value'])
            elif token.get('type') == 'parameter':
                if 'error' in token:
                    return None, [f"Ошибка: {token['error']}"]
                # Если это параметр, попробуем получить из custom_values или params
                param_name = token['name']
                if param_name in custom_values:
                    numbers.append(custom_values[param_name])
                    steps.append(f"  Parameter {param_name} = {custom_values[param_name]}")
                elif param_name in params:
                    numbers.append(params[param_name])
                    steps.append(f"  Parameter {param_name} = {params[param_name]}")
                else:
                    # Возвращаем 0 если параметр не найден
                    numbers.append(0)
                    steps.append(f"  Parameter {param_name} = 0 (не найден)")
            elif token.get('type') == 'measurement':
                value = self.lookup_measurement(token, custom_values)
                if value is not None:
                    numbers.append(value)
                    steps.append(f"  Lookup {token['text']} = {value}")
                else:
                    steps.append(f"  Lookup {token['text']} = NOT FOUND")
                    # Добавляем 0 для продолжения вычислений
                    numbers.append(0)
            elif token.get('type') == 'operator':
                operators.append(token['value'])
        
        if len(numbers) < 2:
            return None, steps
        
        # Вычисление
        result = numbers[0]
        for i, op in enumerate(operators):
            if i + 1 >= len(numbers):
                break
            
            next_val = numbers[i + 1]
            step_text = f"  {result} {op} {next_val} = "
            
            if op == '+':
                result = result + next_val
            elif op == '-':
                result = result - next_val
            elif op == '*':
                result = result * next_val
            elif op == '/':
                if next_val != 0:
                    result = result / next_val
                else:
                    return None, steps + [step_text + "ERROR: division by zero"]
            
            step_text += str(result)
            steps.append(step_text)
        
        return result, steps


class FSIGHTCalculator:
    """Калькулятор для вычисления формул FSIGHT"""
    
    def __init__(self, data_lookup: DataLookup):
        """
        Инициализация калькулятора
        
        Args:
            data_lookup: Lookup для поиска значений
        """
        self.data_lookup = data_lookup
        self.results: List[CalculationResult] = []
    
    def calculate_formula(self, formula: Formula, params: Dict[str, float] = None,
                          custom_values: Dict[str, float] = None) -> CalculationResult:
        """
        Вычислить одну формулу
        
        Args:
            formula: Формула для расчета
            params: Параметры для подстановки
            custom_values: Кастомные значения для lookup
        
        Returns:
            CalculationResult - результат расчета
        """
        if params is None:
            params = {}
        if custom_values is None:
            custom_values = {}
        
        # Добавление кастомных значений в lookup
        for key, value in custom_values.items():
            self.data_lookup.test_data[key] = value
        
        # Получение выражения
        text = formula.get_expression()
        
        # Создание выражения
        expr = ArithmeticExpression(text, self.data_lookup)
        
        # Вычисление с кастомными значениями
        result, steps = expr.evaluate(params, custom_values)
        
        # Создание результата
        calculation_result = CalculationResult(
            formula_id=formula.id,
            formula_name=formula.name,
            text=text,
            steps=steps,
            result=result
        )
        
        self.results.append(calculation_result)
        
        return calculation_result
    
    def calculate_block(self, block, params: Dict[str, float] = None,
                        custom_values: Dict[str, float] = None) -> List[CalculationResult]:
        """
        Вычислить все формулы в блоке
        
        Args:
            block: Блок расчёта
            params: Параметры
            custom_values: Кастомные значения
        
        Returns:
            List[CalculationResult]
        """
        if params is None:
            params = {}
        if custom_values is None:
            custom_values = {}
        
        results = []
        for formula in block.formulas:
            result = self.calculate_formula(formula, params, custom_values)
            results.append(result)
        
        return results
    
    def calculate_all(self, config, custom_values: Dict[str, float] = None) -> List[CalculationResult]:
        """
        Вычислить все формулы в конфигурации
        
        Args:
            config: FSIGHTConfig
            custom_values: Кастомные значения
        
        Returns:
            List[CalculationResult]
        """
        if custom_values is None:
            custom_values = {}
        
        all_results = []
        
        for block in config.blocks:
            results = self.calculate_block(block, custom_values=custom_values)
            all_results.extend(results)
        
        return all_results
    
    def get_summary(self) -> Dict[str, Any]:
        """Получить сводку результатов"""
        success = sum(1 for r in self.results if r.success())
        failed = len(self.results) - success
        
        return {
            'total': len(self.results),
            'success': success,
            'failed': failed,
            'results': [
                {
                    'id': r.formula_id,
                    'name': r.formula_name,
                    'result': r.result if r.success() else r.error
                }
                for r in self.results
            ]
        }
    
    def print_results(self):
        """Вывод результатов в консоль"""
        print("=" * 80)
        print("РЕЗУЛЬТАТЫ РАСЧЕТА")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n{result.get_detailed_report()}")
        
        print("\n" + "=" * 80)
        summary = self.get_summary()
        print(f"Всего формул: {summary['total']}")
        print(f"Успешно: {summary['success']}")
        print(f"С ошибкой: {summary['failed']}")
        print("=" * 80)


# Пример использования
if __name__ == '__main__':
    from .formula_parser import FormulaParser
    
    # Загрузка конфигурации
    parser = FormulaParser.load_and_parse('TEST_ALG.json')
    config = parser.config
    
    # Создание lookup с тестовыми данными
    from .measurements import DataLookup, CubeContext
    
    lookup = DataLookup()
    
    # Добавление тестовых кубов с данными
    for block in config.blocks:
        if block.receiver:
            cube_context = CubeContext.from_cube_data(
                cube_id=block.receiver.cube_id,
                cube_name=block.receiver.cube_name,
                cube_key=block.receiver.cube_key,
                dims=block.receiver.dims
            )
            lookup.add_cube(cube_context)
    
    # Добавление тестовых значений
    lookup.add_values_from_dict('CUB_OSP_1', {
        'CUB_OSP_1!Число|2017': 100.0,
        'CUB_OSP_1!Число|2018': 150.0,
        'CUB_OSP_1!∑Год': 250.0  # Сумма по годам
    })
    
    # Создание калькулятора
    calculator = FSIGHTCalculator(lookup)
    
    # Вычисление всех формул
    results = calculator.calculate_all(config)
    
    # Вывод результатов
    calculator.print_results()

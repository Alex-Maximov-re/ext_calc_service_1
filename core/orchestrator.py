"""
Оркестратор расчетов FSIGHT

Управляет порядком вычисления формул с учетом зависимостей:
- Построение DAG (Directed Acyclic Graph)
- Топологическая сортировка
- Последовательное выполнение
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import deque

from .formula import Formula
from .block import Block
from .algorithm import FSIGHTConfig
from .calculator import FSIGHTCalculator, CalculationResult


@dataclass
class FormulaDependency:
    """Зависимость между формулами"""
    from_formula: str
    to_formula: str
    dependency_type: str  # 'data', 'parameter', 'block'
    
    def __str__(self):
        return f"{self.from_formula} → {self.to_formula} ({self.dependency_type})"


@dataclass
class CalculationStep:
    """Шаг расчета"""
    block_id: str
    block_name: str
    formula: Formula
    order: int
    dependencies: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"Step {self.order}: {self.block_name}.{self.formula.name}"


class DAGCalculator:
    """Древовидный оркестратор для расчетов"""
    
    def __init__(self, calculator: FSIGHTCalculator):
        """
        Инициализация оркестратора
        
        Args:
            calculator: Калькулятор для выполнения вычислений
        """
        self.calculator = calculator
        self.formulas: List[Formula] = []
        self.blocks: List[Block] = []
        self.dependencies: Dict[str, List[str]] = {}  # formula_id → [dependent_formula_ids]
        self.order: List[str] = []  # Топологический порядок
        self.steps: List[CalculationStep] = []
    
    def analyze_dependencies(self, config: FSIGHTConfig) -> Dict[str, Set[str]]:
        """
        Анализ зависимостей между формулами
        
        Returns:
            Dict: formula_id → set of dependent formula_ids
        """
        deps: Dict[str, Set[str]] = {}
        self.formulas = config.get_formulas_flat()
        self.blocks = config.blocks
        
        # Создаем карту formula_id → formula
        formula_map = {f.id: f for f in self.formulas}
        
        # Анализ зависимостей
        for formula in self.formulas:
            deps[formula.id] = set()
            
            # 1. Поиск зависимостей по общим кубам
            current_cubes = set(formula.get_cube_refs())
            
            for other_formula in self.formulas:
                if other_formula.id == formula.id:
                    continue
                
                other_cubes = set(other_formula.get_cube_refs())
                
                # Если есть общие кубы и formula2 появляется раньше в блоке
                if current_cubes & other_cubes:
                    deps[formula.id].add(other_formula.id)
            
            # 2. Поиск зависимостей по параметрам
            current_params = set(formula.get_parameter_names())
            
            for other_formula in self.formulas:
                if other_formula.id != formula.id:
                    other_params = set(other_formula.get_parameter_names())
                    
                    # Если есть общие параметры
                    if current_params & other_params:
                        deps[formula.id].add(other_formula.id)
        
        return deps
    
    def topological_sort(self, deps: Dict[str, Set[str]]) -> List[str]:
        """
        Топологическая сортировка формул
        
        Args:
            deps: Зависимости между формулами
            
        Returns:
            Список формул в порядке вычисления
        """
        # Вычисляем индексы (количество входящих ребер)
        in_degree: Dict[str, int] = {f: 0 for f in deps}
        
        for formula_id, dependent_ids in deps.items():
            for dep_id in dependent_ids:
                if dep_id in in_degree:
                    in_degree[dep_id] += 1
        
        # Queue формул без зависимостей
        queue = deque([f for f, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Уменьшаем индексы для зависимых
            for formula_id, dependent_ids in deps.items():
                if current in dependent_ids:
                    in_degree[formula_id] -= 1
                    if in_degree[formula_id] == 0:
                        queue.append(formula_id)
        
        # Проверка на циклы
        if len(result) != len(deps):
            raise ValueError("Циклические зависимости обнаружены!")
        
        return result
    
    def create_calculation_steps(self) -> List[CalculationStep]:
        """Создание шагов расчета"""
        self.steps = []
        order = 1
        
        for formula_id in self.order:
            formula = next(f for f in self.formulas if f.id == formula_id)
            
            # Найти блок формулы
            block = next((b for b in self.blocks if formula.id in [f.id for f in b.formulas]), None)
            
            # Найти зависимости
            dep_ids = self.dependencies.get(formula_id, set())
            dep_names = [fid for fid in dep_ids if fid in [f.id for f in self.formulas]]
            
            step = CalculationStep(
                block_id=block.id if block else "",
                block_name=block.name if block else "Unknown",
                formula=formula,
                order=order,
                dependencies=dep_names
            )
            
            self.steps.append(step)
            order += 1
        
        return self.steps
    
    def execute_all(self, config: FSIGHTConfig, custom_values: Dict[str, float] = None,
                    params: Dict[str, float] = None) -> List[CalculationResult]:
        """
        Выполнить все расчеты в правильном порядке
        
        Args:
            config: Конфигурация FSIGHT
            custom_values: Кастомные значения
            params: Параметры
        
        Returns:
            List[CalculationResult]
        """
        if custom_values is None:
            custom_values = {}
        if params is None:
            params = {}
        
        # Анализ зависимостей
        print("Анализ зависимостей...")
        self.analyze_dependencies(config)
        
        # Топологическая сортировка
        print("Построение порядка вычислений...")
        self.order = self.topological_sort(self.dependencies)
        
        # Создание шагов
        print("Создание шагов расчета...")
        self.create_calculation_steps()
        
        # Выполнение
        print("\nВыполнение расчетов...")
        all_results = []
        
        for step in self.steps:
            print(f"\n{step}")
            print(f"  Зависимости: {step.dependencies}")
            
            # Выполнение формулы
            result = self.calculator.calculate_formula(
                step.formula,
                params=params,
                custom_values=custom_values
            )
            
            all_results.append(result)
            
            if result.success():
                print(f"  ✓ Результат: {result.result}")
            else:
                print(f"  ✗ Ошибка: {result.error}")
        
        return all_results
    
    def print_order(self):
        """Вывести порядок вычислений"""
        print("\n" + "=" * 80)
        print("ПОРЯДОК ВЫЧИСЛЕНИЙ")
        print("=" * 80)
        
        for step in self.steps:
            print(f"\n{step}")
            if step.dependencies:
                print(f"  Зависит от: {', '.join(step.dependencies)}")
        
        print("=" * 80)


# Пример использования
if __name__ == '__main__':
    from .formula_parser import FormulaParser
    
    # Загрузка конфигурации
    parser = FormulaParser.load_and_parse('TEST_ALG.json')
    config = parser.config
    
    # Создание калькулятора
    from .calculator import FSIGHTCalculator
    from .measurements import DataLookup
    
    lookup = DataLookup()
    calculator = FSIGHTCalculator(lookup)
    
    # Добавление тестовых данных
    lookup.add_values_from_dict('CUB_OSP_1', {
        'Число|2017': 100.0,
        'Число|2018': 150.0,
        '∑Год': 250.0,
        '2018': 150.0
    })
    
    # Создание оркестратора
    orchestrator = DAGCalculator(calculator)
    
    # Выполнение
    results = orchestrator.execute_all(
        config,
        custom_values={
            'Число|2017': 100.0,
            'Число|2018': 150.0,
            '∑Год': 250.0
        },
        params={
            'Параметр Год (блок)': 2018
        }
    )
    
    # Вывод порядка
    orchestrator.print_order()
    
    # Вывод результатов
    print("\n")
    calculator.print_results()

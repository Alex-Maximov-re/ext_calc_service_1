"""
Парсер формул FSIGHT

Парсит JSON конфигурацию и извлекает:
- алгоритм и его параметры
- блоки расчёта
- формулы с термами и периодическими выражениями
"""

import json
from typing import Optional, Dict, Any, List

from .algorithm import FSIGHTConfig
from .formula import Formula
from .term import Term, Slice, ElementSelection
from .period_expr import PeriodExpr
from .block import Block


class FormulaParser:
    """Парсер формул FSIGHT"""
    
    def __init__(self, json_file: str):
        """
        Инициализация парсера
        
        Args:
            json_file: Путь к JSON файлу конфигурации
        """
        self.json_file = json_file
        self.config: Optional[FSIGHTConfig] = None
        self.formulas: List[Formula] = []
        self.blocks: List[Block] = []
    
    def parse(self) -> FSIGHTConfig:
        """
        Основная функция парсинга
        
        Returns:
            FSIGHTConfig - распаршенная конфигурация
        
        Raises:
            FileNotFoundError: Если файл не найден
            json.JSONDecodeError: Если JSON некорректен
        """
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.config = FSIGHTConfig.from_dict(data)
        self.formulas = self.config.get_formulas_flat()
        self.blocks = self.config.blocks
        
        return self.config
    
    def parse_formula(self, formula_data: Dict[str, Any]) -> Formula:
        """
        Парсинг отдельной формулы
        
        Args:
            formula_data: Словарь с данными формулы
            
        Returns:
            Formula - распаршенная формула
        """
        return Formula.from_dict(formula_data)
    
    def parse_term(self, term_data: Dict[str, Any]) -> Term:
        """
        Парсинг отдельного терма
        
        Args:
            term_data: Словарь с данными терма
            
        Returns:
            Term - распаршенный терм
        """
        return Term.from_dict(term_data)
    
    def parse_slice(self, slice_data: Dict[str, Any]) -> Slice:
        """
        Парсинг сечения (измерения)
        
        Args:
            slice_data: Словарь с данными сечения
            
        Returns:
            Slice - распаршенное сечение
        """
        return Slice.from_dict(slice_data)
    
    def analyze_formula(self, formula: Formula) -> Dict[str, Any]:
        """
        Анализ формулы
        
        Args:
            formula: Формула для анализа
            
        Returns:
            Dict с результатами анализа
        """
        return {
            'id': formula.id,
            'name': formula.name,
            'text': formula.text,
            'text_inner': formula.text_inner,
            'has_parameters': formula.has_parameters(),
            'parameters': formula.get_parameter_names(),
            'cube_refs': formula.get_cube_refs(),
            'term_count': len(formula.terms),
            'terms_detail': [
                {
                    'n': term.n,
                    'text': term.text,
                    'inner': term.inner,
                    'self': term.self_ref,
                    'lag': term.lag,
                    'slice_count': len(term.slice)
                }
                for term in formula.terms
            ],
            'period_expr_count': len(formula.period_exprs)
        }
    
    def analyze_all_formulas(self) -> List[Dict[str, Any]]:
        """
        Анализ всех формул
        
        Returns:
            List[Dict] - список результатов анализа
        """
        return [self.analyze_formula(f) for f in self.formulas]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Статистика по конфигурации
        
        Returns:
            Dict со статистикой
        """
        stats = {
            'schema': self.config.schema,
            'algorithm': {
                'id': self.config.algorithm.id,
                'name': self.config.algorithm.name,
                'param_count': len(self.config.algorithm.params)
            },
            'blocks': {
                'count': len(self.blocks),
                'total_formulas': sum(b.get_formula_count() for b in self.blocks)
            },
            'cubes': list(self.config.get_cubes()),
            'formulas': {
                'total': len(self.formulas),
                'with_parameters': sum(1 for f in self.formulas if f.has_parameters()),
                'with_aggregation': sum(
                    1 for f in self.formulas 
                    for term in f.terms 
                    if '∑' in term.text
                )
            }
        }
        return stats
    
    def print_analysis(self):
        """Вывести анализ в консоль"""
        print("=" * 80)
        print("АНАЛИЗ КОНФИГУРАЦИИ FSIGHT")
        print("=" * 80)
        
        stats = self.get_statistics()
        
        print(f"\nСхема: {stats['schema']}")
        print(f"Алгоритм: {stats['algorithm']['name']} ({stats['algorithm']['id']})")
        print(f"Параметры алгоритма: {stats['algorithm']['param_count']}")
        
        print(f"\nБлоков: {stats['blocks']['count']}")
        print(f"Всего формул: {stats['blocks']['total_formulas']}")
        
        print(f"\nКубы: {', '.join(stats['cubes'])}")
        
        formulas = stats['formulas']
        print(f"\nФормулы:")
        print(f"  Всего: {formulas['total']}")
        print(f"  С параметрами: {formulas['with_parameters']}")
        print(f"  С агрегацией: {formulas['with_aggregation']}")
        
        print("\n" + "-" * 80)
        print("ДЕТАЛИЗАЦИЯ ФОРМУЛ")
        print("-" * 80)
        
        for formula in self.formulas:
            print(f"\n[{formula.id}] {formula.name}")
            print(f"  Текст: {formula.text}")
            print(f"  Text_inner: {formula.text_inner}")
            if formula.has_parameters():
                print(f"  Параметры: {formula.get_parameter_names()}")
            if formula.terms:
                print(f"  Термов: {len(formula.terms)}")
                for term in formula.terms:
                    cubes = term.get_cube_id()
                    print(f"    - Терм {term.n}: {term.text} → {cubes}")
            
            if formula.period_exprs:
                print(f"  Периодические выражения: {len(formula.period_exprs)}")
    
    @staticmethod
    def load_and_parse(json_file: str) -> 'FormulaParser':
        """
        Загрузить и распарсить конфигурацию
        
        Args:
            json_file: Путь к файлу
            
        Returns:
            FormulaParser с распаршенной конфигурацией
        """
        parser = FormulaParser(json_file)
        parser.parse()
        return parser


# Пример использования
if __name__ == '__main__':
    import os
    
    # Проверка существования TEST_ALG.json
    json_file = 'TEST_ALG.json'
    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден!")
        exit(1)
    
    # Парсинг и анализ
    parser = FormulaParser.load_and_parse(json_file)
    parser.print_analysis()
    
    # Сохранение статистики
    stats = parser.get_statistics()
    print("\n" + "=" * 80)
    print("СТАТИСТИКА")
    print("=" * 80)
    print(f"Кубы: {stats['cubes']}")
    print(f"Формул с параметрами: {stats['formulas']['with_parameters']}")
    print(f"Формул с агрегацией: {stats['formulas']['with_aggregation']}")

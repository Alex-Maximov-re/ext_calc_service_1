"""
Генератор Markdown отчетов для FSIGHT

Генерирует подробные отчеты о расчетах в формате Markdown с:
- Визуализацией цепочек вычислений
- Таблицами промежуточных значений
- Итогами по каждому блоку
"""

from typing import Dict, List, Optional
from datetime import datetime

import sys
from pathlib import Path

# Добавляем путь для импортов
_current_dir = Path(__file__).parent.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from core.formula import Formula
from core.block import Block
from core.algorithm import FSIGHTConfig
from core.calculator import FSIGHTCalculator, CalculationResult
from core.orchestrator import DAGCalculator, CalculationStep


class MarkdownGenerator:
    """Генератор Markdown отчетов"""
    
    def __init__(self, calculator: FSIGHTCalculator):
        """
        Инициализация генератора
        
        Args:
            calculator: Калькулятор для доступа к результатам
        """
        self.calculator = calculator
    
    def generate_report(self, 
                       config: FSIGHTConfig, 
                       results: List[CalculationResult],
                       steps: List[CalculationStep] = None,
                       dependencies: Dict[str, List[str]] = None) -> str:
        """
        Генерация отчета
        
        Args:
            config: Конфигурация FSIGHT
            results: Результаты расчетов
            steps: Шаги расчета
            dependencies: Зависимости между формулами
        
        Returns:
            Markdown строка
        """
        lines = []
        
        # Заголовок
        lines.append("# Отчет о расчетах FSIGHT")
        lines.append("")
        lines.append(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Алгоритм:** {config.algorithm.name} ({config.algorithm.id})")
        lines.append("")
        
        # Статистика
        lines.extend(self._generate_statistics(config, results))
        lines.append("")
        
        # Порядок вычислений (если есть DAG)
        if steps:
            lines.extend(self._generate_execution_order(steps))
            lines.append("")
        
        # Блоки расчета
        for block in config.blocks:
            lines.extend(self._generate_block_report(block, results, steps))
            lines.append("")
        
        # Детальный вывод по всем формулам
        lines.append("## Детализация формул")
        lines.append("")
        lines.extend(self._generate_formula_details(results))
        
        return "\n".join(lines)
    
    def _generate_statistics(self, config: FSIGHTConfig, results: List[CalculationResult]) -> List[str]:
        """Генерация статистики"""
        lines = []
        
        lines.append("## Статистика")
        lines.append("")
        
        total = len(results)
        success = sum(1 for r in results if r.success())
        failed = total - success
        
        lines.append(f"- **Всего формул:** {total}")
        lines.append(f"- **Успешно:** {success}")
        lines.append(f"- **С ошибками:** {failed}")
        lines.append(f"- **Успех:** {success/total*100:.1f}%" if total > 0 else "")
        lines.append("")
        
        # Блоки
        lines.append("**Блоки:**")
        for block in config.blocks:
            formula_count = sum(1 for r in results if any(f.id in r.formula_id for f in block.formulas))
            lines.append(f"- {block.name}: {formula_count} формул")
        lines.append("")
        
        return lines
    
    def _generate_execution_order(self, steps: List[CalculationStep]) -> List[str]:
        """Генерация порядка выполнения"""
        lines = []
        
        lines.append("## Порядок выполнения расчетов")
        lines.append("")
        
        for step in steps:
            lines.append(f"### Шаг {step.order}")
            lines.append("")
            lines.append(f"**Блок:** {step.block_name}")
            lines.append(f"**Формула:** {step.formula.name} ({step.formula.id})")
            lines.append(f"**Текст:** `{step.formula.text}`")
            
            if step.dependencies:
                lines.append(f"**Зависит от:** {', '.join(step.dependencies)}")
            
            lines.append("")
        
        return lines
    
    def _generate_block_report(self, block: Block, results: List[CalculationResult],
                               steps: List[CalculationStep] = None) -> List[str]:
        """Генерация отчета по блоку"""
        lines = []
        
        lines.append(f"## Блок {block.seq}: {block.name}")
        lines.append("")
        
        # Информация о блоке
        lines.append(f"- **ID:** {block.id}")
        lines.append(f"- **Тип:** {block.type}")
        lines.append(f"- **Формул:** {len(block.formulas)}")
        lines.append("")
        
        # Receiver (куб)
        if block.receiver:
            lines.append("**Receiver (куб):**")
            lines.append(f"- Cube: {block.receiver.cube_id}")
            lines.append(f"- Name: {block.receiver.cube_name}")
            lines.append(f"- Key: {block.receiver.cube_key}")
            lines.append("")
            
            # Измерения
            lines.append("**Измерения:**")
            for dim in block.receiver.dims:
                lines.append(f"- {dim.get('name', '')} ({dim.get('id', '')})")
            lines.append("")
        
        # Формулы блока
        lines.append("**Формулы:**")
        lines.append("")
        
        for formula in block.formulas:
            # Найти результат этой формулы
            result = next((r for r in results if r.formula_id == formula.id), None)
            
            lines.extend(self._generate_formula_report(formula, result, block.seq))
            lines.append("")
        
        return lines
    
    def _generate_formula_report(self, formula: Formula, result: Optional[CalculationResult],
                                 block_seq: int) -> List[str]:
        """Генерация отчета по формуле"""
        lines = []
        
        status_icon = "✅" if result and result.success() else "⚠️"
        
        lines.append(f"### {status_icon} Формула {block_seq}.{formula.key}: {formula.name}")
        lines.append("")
        
        # Основная информация
        lines.append(f"- **ID:** {formula.id}")
        lines.append(f"- **Ключ:** {formula.key}")
        lines.append(f"- **Текст:** `{formula.text}`")
        lines.append(f"- **Text_inner:** `{formula.text_inner}`")
        lines.append("")
        
        # Параметры
        if formula.has_parameters():
            params = formula.get_parameter_names()
            lines.append(f"**Параметры:** {', '.join(params)}")
            lines.append("")
        
        # Термы
        if formula.terms:
            lines.append("**Термы:**")
            for term in formula.terms:
                lines.append(f"- Терм {term.n}: `{term.text}` → {term.get_cube_id()}")
            lines.append("")
        
        # Результат
        if result:
            lines.append("**Результат:**")
            if result.success():
                lines.append(f"```")
                lines.append(f"{result.text}")
                lines.append(f"")
                for step in result.steps:
                    lines.append(f"{step}")
                lines.append(f"")
                lines.append(f"Итог: {result.result}")
                lines.append(f"```")
            else:
                lines.append(f"⚠️ **Ошибка:** {result.error}")
            
            lines.append("")
        
        return lines
    
    def _generate_formula_details(self, results: List[CalculationResult]) -> List[str]:
        """Детализация всех формул в таблице"""
        lines = []
        
        lines.append("| № | Формула | Результат | Статус |")
        lines.append("|-----|---------|-----------|--------|")
        
        for i, result in enumerate(results, 1):
            name = result.formula_name[:30] if len(result.formula_name) > 30 else result.formula_name
            status = "✅" if result.success() else "⚠️"
            value = f"{result.result:.2f}" if result.result else "ERROR"
            
            lines.append(f"| {i} | {name} | {value} | {status} |")
        
        lines.append("")
        
        return lines


# Пример использования
if __name__ == '__main__':
    from .formula_parser import FormulaParser
    from .calculator import FSIGHTCalculator
    from .measurements import DataLookup
    
    # Загрузка конфигурации
    parser = FormulaParser.load_and_parse('TEST_ALG.json')
    config = parser.config
    
    # Создание калькулятора
    lookup = DataLookup()
    calculator = FSIGHTCalculator(lookup)
    
    # Добавление данных
    lookup.add_values_from_dict('CUB_OSP_1', {
        'Число|2017': 100.0,
        'Число|2018': 150.0,
        '∑Год': 250.0
    })
    
    # Вычисление
    results = calculator.calculate_all(config, custom_values={
        'Число|2017': 100.0,
        'Число|2018': 150.0,
        '∑Год': 250.0
    })
    
    # Создание генератора
    generator = MarkdownGenerator(calculator)
    
    # Генерация отчета
    report = generator.generate_report(config, results)
    
    # Сохранение
    output_file = 'output/report.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Отчет сохранен: {output_file}")
    print("\n" + "=" * 80)
    print(report)

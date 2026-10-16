"""
Визуализация для FSIGHT

Генерация графов зависимостей между формулами и блоками.
Использует Graphviz для создания визуальных диаграмм.
"""

from typing import Dict, List, Optional
import os

import sys
from pathlib import Path

# Добавляем путь для импортов
_current_dir = Path(__file__).parent.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from core.formula import Formula
from core.block import Block
from core.algorithm import FSIGHTConfig


class GraphVisualizer:
    """Визуализатор зависимостей"""
    
    def __init__(self, output_dir: str = 'output'):
        """
        Инициализация визуализатора
        
        Args:
            output_dir: Директория для сохранения графов
        """
        self.output_dir = output_dir
        self.formulas: List[Formula] = []
        self.blocks: List[Block] = []
        self.dependencies: Dict[str, List[str]] = {}
        
        # Проверка наличия graphviz
        self.graphviz_available = self._check_graphviz()
    
    def _check_graphviz(self) -> bool:
        """Проверить наличие Graphviz"""
        try:
            import graphviz
            return True
        except ImportError:
            return False
    
    def analyze_dependencies(self, config: FSIGHTConfig):
        """Анализ зависимостей"""
        self.formulas = config.get_formulas_flat()
        self.blocks = config.blocks
        
        # Создаем карту зависимости
        self.dependencies = {}
        for formula in self.formulas:
            self.dependencies[formula.id] = []
            
            # Поиск зависимостей по общим кубам
            current_cubes = formula.get_cube_refs()
            
            for other_formula in self.formulas:
                if other_formula.id != formula.id:
                    other_cubes = other_formula.get_cube_refs()
                    
                    # Если есть общие кубы
                    if current_cubes & other_cubes:
                        self.dependencies[formula.id].append(other_formula.id)
                    
                    # Проверка по параметрам
                    current_params = formula.get_parameter_names()
                    other_params = other_formula.get_parameter_names()
                    
                    if set(current_params) & set(other_params):
                        if other_formula.id not in self.dependencies[formula.id]:
                            self.dependencies[formula.id].append(other_formula.id)
    
    def generate_dependency_graph(self, output_file: str = 'dependencies.dot') -> Optional[str]:
        """
        Генерация графа зависимостей
        
        Args:
            output_file: Имя файла для сохранения (DOT формат)
        
        Returns:
            Путь к файлу или None если Graphviz недоступен
        """
        if not self.graphviz_available:
            return None
        
        import graphviz
        
        dot = graphviz.Digraph(comment='FSIGHT Dependencies')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='box', style='filled', fillcolor='#e1f5fe')
        
        # Добавить узлы формул
        for formula in self.formulas:
            dot.node(formula.id, formula.name[:20])
        
        # Добавить связи
        for formula_id, deps in self.dependencies.items():
            for dep_id in deps:
                dot.edge(dep_id, formula_id)
        
        # Сохранение
        filepath = os.path.join(self.output_dir, output_file)
        dot.render(filepath, view=False, cleanup=True)
        
        return filepath
    
    def generate_block_graph(self, output_file: str = 'blocks.dot') -> Optional[str]:
        """
        Генерация графа блоков
        
        Args:
            output_file: Имя файла для сохранения
        
        Returns:
            Путь к файлу или None
        """
        if not self.graphviz_available:
            return None
        
        import graphviz
        
        dot = graphviz.Digraph(comment='FSIGHT Blocks')
        dot.attr(rankdir='TB')
        dot.attr('node', shape='box', style='rounded', fillcolor='#fff9c4')
        dot.attr('edge', style='dashed')
        
        # Добавить узлы блоков
        for block in self.blocks:
            formula_count = len(block.formulas)
            label = f"{block.name}\\n({formula_count} формулы)"
            dot.node(block.id, label)
        
        # Сохранение
        filepath = os.path.join(self.output_dir, output_file)
        dot.render(filepath, view=False, cleanup=True)
        
        return filepath
    
    def generate_html_report(self, output_file: str = 'visualization.html') -> Optional[str]:
        """
        Генерация HTML с графами
        
        Args:
            output_file: Имя HTML файла
        
        Returns:
            Путь к файлу или None
        """
        if not self.graphviz_available:
            return None
        
        # Генерация DOT файлов
        dep_dot = self.generate_dependency_graph()
        block_dot = self.generate_block_graph()
        
        if not dep_dot or not block_dot:
            return None
        
        # Создание HTML
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Визуализация FSIGHT</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
        }}
        .graph-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #1976D2;
            margin-top: 0;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #1976D2;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        img {{
            max-width: 100%;
            border-radius: 4px;
        }}
        .note {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <h1>📊 Визуализация зависимостей FSIGHT</h1>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{len(self.blocks)}</div>
            <div class="stat-label">Блоков</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(self.formulas)}</div>
            <div class="stat-label">Формул</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(len(deps) for deps in self.dependencies.values())}</div>
            <div class="stat-label">Зависимостей</div>
        </div>
    </div>
    
    <div class="graph-container">
        <h2>🔗 Зависимости между формулами</h2>
        <p>Стрелка показывает направление зависимости (A → B означает, что B зависит от A)</p>
        <img src="{dep_dot}" alt="Граф зависимостей">
    </div>
    
    <div class="graph-container">
        <h2>📦 Структура блоков</h2>
        <p>Блоки расчёта и количество формул в каждом</p>
        <img src="{block_dot}" alt="Граф блоков">
    </div>
    
    <div class="note">
        <strong>Примечание:</strong> Для генерации графов требуется Graphviz. 
        Установите через: <code>pip install graphviz</code> и скачайте Graphviz с <a href="https://graphviz.org" target="_blank">graphviz.org</a>
    </div>
</body>
</html>
"""
        
        filepath = os.path.join(self.output_dir, output_file)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def generate_text_visualization(self) -> str:
        """Генерация текстового представления зависимостей"""
        lines = []
        lines.append("=" * 80)
        lines.append("ГРАФ ЗАВИСИМОСТЕЙ (текстовое представление)")
        lines.append("=" * 80)
        
        for formula in self.formulas:
            deps = self.dependencies.get(formula.id, [])
            if deps:
                lines.append(f"\n{formula.id}: {formula.name[:40]}")
                lines.append(f"  зависит от:")
                for dep in deps:
                    dep_formula = next((f for f in self.formulas if f.id == dep), None)
                    if dep_formula:
                        lines.append(f"    ← {dep_formula.id}: {dep_formula.name[:40]}")
            else:
                lines.append(f"\n{formula.id}: {formula.name[:40]} (независимая)")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)


# Пример использования
if __name__ == '__main__':
    from core.formula_parser import FormulaParser
    from core.calculator import FSIGHTCalculator
    from core.orchestrator import DAGCalculator
    
    # Загрузка конфигурации
    parser = FormulaParser.load_and_parse('TEST_ALG.json')
    config = parser.config
    
    # Визуализация
    visualizer = GraphVisualizer(output_dir='output')
    visualizer.analyze_dependencies(config)
    
    # Генерация текстового представления
    print(visualizer.generate_text_visualization())
    
    # Генерация графов
    if visualizer.graphviz_available:
        dep_dot = visualizer.generate_dependency_graph()
        block_dot = visualizer.generate_block_graph()
        html = visualizer.generate_html_report()
        
        print(f"\n✅ Графы созданы:")
        print(f"   - {dep_dot}")
        print(f"   - {block_dot}")
        print(f"   - {html}")
    else:
        print("\n⚠️ Graphviz не установлен. Установите для генерации графов:")
        print("   pip install graphviz")
        print("   (также нужна установка Graphviz с graphviz.org)")

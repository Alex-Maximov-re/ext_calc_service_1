#!/usr/bin/env python
"""
FSIGHT Math Engine - Командная строка

Основной CLI для запуска расчетов и генерации отчетов.
"""

import argparse
import sys
import os
import json
from datetime import datetime

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.formula_parser import FormulaParser
from core.calculator import FSIGHTCalculator
from core.orchestrator import DAGCalculator
from report.markdown_generator import MarkdownGenerator
from report.visualizer import GraphVisualizer


def load_data_file(filepath: str) -> dict:
    """Загрузка файла с данными"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл данных не найден: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_calculation(config_path: str, 
                   data_path: str, 
                   output_path: str,
                   format: str = 'md',
                   visualize: bool = False):
    """
    Запуск расчета
    
    Args:
        config_path: Путь к конфигурации JSON
        data_path: Путь к файлу данных
        output_path: Путь к выходному файлу
        format: Формат вывода (md, html, json)
        visualize: Генерировать ли визуализацию
    """
    print("=" * 80)
    print("FSIGHT Math Engine")
    print("=" * 80)
    print(f"\nЗапуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Загрузка конфигурации
    print("\n1. Загрузка конфигурации...")
    try:
        parser = FormulaParser.load_and_parse(config_path)
        config = parser.config
        print(f"   ✅ Алгоритм: {config.algorithm.name}")
        print(f"   ✅ Кубов: {len(config.get_cubes())}")
        print(f"   ✅ Формул: {config.get_total_formula_count()}")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки: {e}")
        sys.exit(1)
    
    # 2. Загрузка данных
    print("\n2. Загрузка данных...")
    try:
        data = load_data_file(data_path)
        print(f"   ✅ Данные загружены")
    except Exception as e:
        print(f"   ❌ Ошибка загрузки данных: {e}")
        sys.exit(1)
    
    # 3. Создание калькулятора и вычисление
    print("\n3. Вычисление формул...")
    try:
        calculator = FSIGHTCalculator(parser.config)
        
        # Использование данных из файла или тестовых значений
        if 'custom_values' in data:
            custom_values = data['custom_values']
        else:
            custom_values = {}
        
        if 'params' in data:
            params = data['params']
        else:
            params = {}
        
        # Создание оркестратора
        orchestrator = DAGCalculator(calculator)
        results = orchestrator.execute_all(config, custom_values=custom_values, params=params)
        
        print(f"   ✅ Вычислено {len(results)} формул")
        
        # 4. Проверка результатов
        success_count = sum(1 for r in results if r.success())
        failed_count = len(results) - success_count
        
        if failed_count > 0:
            print(f"   ⚠️  Ошибок: {failed_count}")
            for r in results:
                if not r.success():
                    print(f"      - {r.formula_name}: {r.error}")
        
        print(f"   ✅ Успешно: {success_count}")
        
    except Exception as e:
        print(f"   ❌ Ошибка вычисления: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 5. Генерация отчета
    print("\n4. Генерация отчета...")
    try:
        generator = MarkdownGenerator(calculator)
        report = generator.generate_report(config, results, orchestrator.steps, orchestrator.dependencies)
        
        # Сохранение
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        if format == 'md':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"   ✅ Markdown отчет: {output_path}")
        
        elif format == 'json':
            # Экспорт результатов в JSON
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'algorithm': {
                    'id': config.algorithm.id,
                    'name': config.algorithm.name
                },
                'statistics': calculator.get_summary(),
                'results': [
                    {
                        'id': r.formula_id,
                        'name': r.formula_name,
                        'result': r.result,
                        'success': r.success(),
                        'error': r.error,
                        'steps': r.steps
                    }
                    for r in results
                ]
            }
            
            output_path = output_path.replace('.json', '') + '.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"   ✅ JSON результат: {output_path}")
        
        elif format == 'html':
            # Конвертация Markdown в HTML
            from markdown import Markdown
            md = Markdown(extensions=['tables', 'fenced_code'])
            html_content = md.convert(report)
            
            full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет FSIGHT - {config.algorithm.name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1976D2; border-bottom: 3px solid #1976D2; padding-bottom: 10px; }}
        h2 {{ color: #1976D2; margin-top: 30px; }}
        h3 {{ color: #0277BD; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background: #1976D2;
            color: white;
        }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        pre {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .success {{ color: #4CAF50; font-weight: bold; }}
        .error {{ color: #f44336; }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
        <div class="timestamp">
            Сгенерировано FSIGHT Math Engine • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            print(f"   ✅ HTML отчет: {output_path}")
    
    except Exception as e:
        print(f"   ❌ Ошибка генерации отчета: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 6. Визуализация (если включена)
    if visualize:
        print("\n5. Генерация визуализации...")
        try:
            visualizer = GraphVisualizer(output_dir='output')
            visualizer.analyze_dependencies(config)
            
            # Текстовая визуализация
            print(visualizer.generate_text_visualization())
            
            # HTML с графами (если Graphviz установлен)
            if visualizer.graphviz_available:
                html_vis = visualizer.generate_html_report('visualization.html')
                print(f"   ✅ Визуализация: {html_vis}")
            else:
                print("   ⚠️  Graphviz не установлен (установите для графов)")
        
        except Exception as e:
            print(f"   ⚠️  Визуализация: {e}")
    
    # Финал
    print("\n" + "=" * 80)
    print("✅ Расчет завершен!")
    print("=" * 80)
    
    return 0


def main():
    """Точка входа CLI"""
    parser = argparse.ArgumentParser(
        description='FSIGHT Math Engine - расчет формул и генерация отчетов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python main.py config.json --data data.json --output report.md
  python main.py config.json -d data.json -o report.html --visualize
  python main.py config.json -d data.json -o results.json --format json
        """
    )
    
    parser.add_argument(
        'config',
        help='JSON файл конфигурации алгоритма'
    )
    
    parser.add_argument(
        '-d', '--data',
        required=True,
        help='JSON файл с данными для расчета (path/to/data.json)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output/report.md',
        help='Путь к выходному файлу (по умолчанию: output/report.md)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['md', 'html', 'json'],
        default='md',
        help='Формат вывода (по умолчанию: md)'
    )
    
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Генерировать визуализацию зависимостей'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Выводить дополнительную информацию'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Режим отладки'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='FSIGHT Math Engine v0.3.0'
    )
    
    args = parser.parse_args()
    
    # Проверка файлов
    if not os.path.exists(args.config):
        print(f"Ошибка: Файл конфигурации не найден: {args.config}")
        sys.exit(1)
    
    if not os.path.exists(args.data):
        print(f"Ошибка: Файл данных не найден: {args.data}")
        sys.exit(1)
    
    # Запуск
    try:
        return run_calculation(
            config_path=args.config,
            data_path=args.data,
            output_path=args.output,
            format=args.format,
            visualize=args.visualize
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())

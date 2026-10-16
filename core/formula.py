"""
Представление формулы FSIGHT

Формула содержит:
- text: человеко-читаемое представление
- text_inner: внутреннее представление для вычислений
- terms: термы (ссылки на данные)
- period_exprs: периодические выражения
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .term import Term
from .period_expr import PeriodExpr


@dataclass
class Formula:
    """Формула расчета"""
    name: str                       # Название формулы
    id: str                         # ID формулы
    key: int                        # Ключ формулы
    entry_key: int                  # Ключ входа
    is_exclusive: bool              # Эксклюзивная формула
    parent_id: Optional[str] = None # ID родительской формулы
    parent_key: Optional[int] = None# Ключ родительской формулы
    slice_id: str = ""              # ID сечения (например, "CUB_OSP_1!")
    slice_key: int = 0              # Ключ сечения
    calendar_level: int = 1         # Уровень календаря
    text: str = ""                  # Текстовое представление
    text_inner: str = ""            # Внутреннее представление
    target: List[Dict[str, Any]] = field(default_factory=list)  # Целевые измерения
    target_parametrized: List[Dict[str, Any]] = field(default_factory=list)  # Параметризованные цели
    terms: List[Term] = field(default_factory=list)  # Термы формулы
    period_exprs: List[PeriodExpr] = field(default_factory=list)  # Периодические выражения
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Formula':
        # Парсинг термов
        terms = [
            Term.from_dict(t) 
            for t in data.get('terms', [])
        ]
        
        # Парсинг периодических выражений
        period_exprs = [
            PeriodExpr.from_dict(pe) 
            for pe in data.get('period_exprs', [])
        ]
        
        return cls(
            name=data.get('name', ''),
            id=data.get('id', ''),
            key=data.get('key', 0),
            entry_key=data.get('entry_key', 0),
            is_exclusive=data.get('is_exclusive', False),
            parent_id=data.get('parent_id'),
            parent_key=data.get('parent_key'),
            slice_id=data.get('slice_id', ''),
            slice_key=data.get('slice_key', 0),
            target=data.get('target', []),
            target_parametrized=data.get('target_parametrized', []),
            calendar_level=data.get('calendar_level', 1),
            text=data.get('text', ''),
            text_inner=data.get('text_inner', ''),
            terms=terms,
            period_exprs=period_exprs
        )
    
    def get_expression(self) -> str:
        """Получить основное выражение (first period_expr)"""
        if self.period_exprs:
            return self.period_exprs[0].text
        return self.text
    
    def get_lhs(self) -> str:
        """Получить левую часть уравнения (до =)"""
        if '=' in self.text:
            return self.text.split('=')[0].strip()
        return self.text
    
    def get_rhs(self) -> str:
        """Получить правую часть уравнения (после =)"""
        if '=' in self.text:
            return '='.join(self.text.split('=')[1:]).strip()
        return self.text
    
    def has_parameters(self) -> bool:
        """Проверить наличие параметров в тексте"""
        return '{' in self.text and '}' in self.text
    
    def get_parameter_names(self) -> List[str]:
        """Извлечь имена параметров"""
        import re
        params = re.findall(r'\{([^}]+)\}', self.text)
        return list(set(params))
    
    def get_cube_refs(self) -> List[str]:
        """Извлечь ссылки на кубы из всех термов"""
        cubes = set()
        for term in self.terms:
            cubes.add(term.get_cube_id())
        return list(cubes)
    
    def __str__(self) -> str:
        return f"Formula(id='{self.id}', name='{self.name}', text='{self.text[:50]}...')"
    
    def __repr__(self) -> str:
        return self.__str__()

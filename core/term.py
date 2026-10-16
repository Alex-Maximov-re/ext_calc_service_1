"""
Представление терма формулы FSIGHT

Терм - это основная единица формулы, представляющая ссылку на точку данных в кубе.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class SelectionKind(Enum):
    """Тип выбора элементов измерения"""
    LIST = "list"
    ALL = "all"
    RANGE = "range"


@dataclass
class ElementSelection:
    """Элемент выбора (значение измерения)"""
    key: str
    name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElementSelection':
        return cls(
            key=data.get('key', ''),
            name=data.get('name', '')
        )


@dataclass
class Slice:
    """Сечение (измерение с фильтрами)"""
    dim: str                    # Название измерения
    dim_id: str                 # ID измерения (DICT_XXX)
    dim_key: int                # Ключ измерения
    kind: SelectionKind         # Тип выбора
    elements: List[ElementSelection] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Slice':
        elements = [
            ElementSelection.from_dict(e) 
            for e in data.get('elements', [])
        ]
        kind = data.get('kind', 'list')
        return cls(
            dim=data.get('dim', ''),
            dim_id=data.get('dim_id', ''),
            dim_key=data.get('dim_key', 0),
            kind=SelectionKind(kind) if kind in [e.value for e in SelectionKind] else SelectionKind.LIST,
            elements=elements
        )
    
    def get_selection(self) -> str:
        """Получить строковое представление выбора"""
        if self.kind == SelectionKind.ALL:
            return "all"
        elif self.kind == SelectionKind.LIST:
            return ", ".join([e.name for e in self.elements])
        return ""


@dataclass
class Term:
    """Терм формулы - ссылка на точку данных в кубе"""
    n: int                      # Номер терма
    text: str                   # Текстовое представление
    inner: str                  # Внутреннее представление (@_2:0[])
    self_ref: bool              # Самореферентный
    lag: int                    # Лаг (сдвиг по времени)
    slice: List[Slice] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Term':
        slices = [
            Slice.from_dict(s) 
            for s in data.get('slice', [])
        ]
        return cls(
            n=data.get('n', 1),
            text=data.get('text', ''),
            inner=data.get('inner', ''),
            self_ref=data.get('self', False),
            lag=data.get('lag', 0),
            slice=slices
        )
    
    def get_cube_id(self) -> str:
        """Извлечь cube_id из внутреннего представления"""
        # Inner формат: @_2:0[] или @_2:0[]|param
        # @ - начало, затем <cube_key>:<index>[filters]
        if self.inner.startswith('@'):
            inner_part = self.inner[1:]  # Удалить @
            if ':' in inner_part:
                cube_key = inner_part.split(':')[0]
                # Преобразовать восьмеричное в десятичное
                if cube_key.startswith('_'):
                    cube_key = cube_key[1:]
                try:
                    cube_key_int = int(cube_key, 8)
                    return f"CUB_{cube_key_int}"
                except ValueError:
                    pass
        return "UNKNOWN"
    
    def get_measurements(self) -> List[Dict[str, Any]]:
        """Получить измерения из сечений"""
        return [{
            'dim': s.dim,
            'dim_id': s.dim_id,
            'dim_key': s.dim_key,
            'selection': s.get_selection()
        } for s in self.slice]
    
    def __str__(self) -> str:
        return f"Term(n={self.n}, text='{self.text}', inner='{self.inner}', self={self.self_ref}, lag={self.lag})"
    
    def __repr__(self) -> str:
        return self.__str__()

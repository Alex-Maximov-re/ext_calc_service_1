"""
Представление блока расчёта FSIGHT

Блок содержит:
- параметры
- receiver (куб и измерения)
- формулы
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .formula import Formula


@dataclass
class BlockParam:
    """Параметр блока"""
    id: str
    name: str
    linked: str
    linked_id: str
    linked_key: int
    object_param_linked: bool
    object_param: Optional[str] = field(default_factory=lambda: None)
    object_param_id: Optional[str] = field(default_factory=lambda: None)
    default: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlockParam':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            linked=data.get('linked', ''),
            linked_id=data.get('linked_id', ''),
            linked_key=data.get('linked_key', 0),
            object_param_linked=data.get('object_param_linked', False),
            object_param=data.get('object_param'),
            object_param_id=data.get('object_param_id'),
            default=data.get('default', '')
        )


@dataclass
class BlockReceiver:
    """Приемник блока (куб с измерениями)"""
    cube_id: str
    cube_name: str
    cube_key: int
    dims: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BlockReceiver':
        return cls(
            cube_id=data.get('cube_id', ''),
            cube_name=data.get('cube_name', ''),
            cube_key=data.get('cube_key', 0),
            dims=data.get('dims', [])
        )


@dataclass
class Block:
    """Блок расчёта"""
    seq: int                    # Последовательность
    name: str                   # Название
    id: str                     # ID блока
    key: int                    # Ключ
    params: List[BlockParam] = field(default_factory=list)  # Параметры
    type: str = "calc"          # Тип блока
    receiver: Optional[BlockReceiver] = None  # Приемник
    sources: List = field(default_factory=list)  # Источники
    aggregation: Optional[Any] = None  # Агрегация
    formulas: List[Formula] = field(default_factory=list)  # Формулы
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        # Парсинг параметров
        params = [
            BlockParam.from_dict(p) 
            for p in data.get('params', [])
        ]
        
        # Парсинг receiver
        receiver = None
        if data.get('receiver'):
            receiver = BlockReceiver.from_dict(data['receiver'])
        
        # Парсинг формул
        formulas = [
            Formula.from_dict(f) 
            for f in data.get('formulas', [])
        ]
        
        return cls(
            seq=data.get('seq', 0),
            name=data.get('name', ''),
            id=data.get('id', ''),
            key=data.get('key', 0),
            params=params,
            type=data.get('type', 'calc'),
            receiver=receiver,
            sources=data.get('sources', []),
            aggregation=data.get('aggregation'),
            formulas=formulas
        )
    
    def get_receiver_cube(self) -> Optional[str]:
        """Получить cube_id из receiver"""
        return self.receiver.cube_id if self.receiver else None
    
    def get_formula_count(self) -> int:
        """Количество формул в блоке"""
        return len(self.formulas)
    
    def __str__(self) -> str:
        return f"Block(id='{self.id}', name='{self.name}', formulas={self.get_formula_count()})"
    
    def __repr__(self) -> str:
        return self.__str__()

"""
Представление алгоритма FSIGHT

Алгоритм содержит:
- параметры алгоритма
- блоки расчёта
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .block import Block


@dataclass
class AlgorithmParam:
    """Параметр алгоритма"""
    id: str
    name: str
    linked: str
    linked_id: str
    linked_key: int
    object_param_linked: bool
    default: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlgorithmParam':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            linked=data.get('linked', ''),
            linked_id=data.get('linked_id', ''),
            linked_key=data.get('linked_key', 0),
            object_param_linked=data.get('object_param_linked', False),
            default=data.get('default', '')
        )


@dataclass
class Algorithm:
    """Алгоритм"""
    id: str
    key: int
    name: str
    params: List[AlgorithmParam] = field(default_factory=list)  # Параметры
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Algorithm':
        params = [
            AlgorithmParam.from_dict(p) 
            for p in data.get('params', [])
        ]
        
        return cls(
            id=data.get('id', ''),
            key=data.get('key', 0),
            name=data.get('name', ''),
            params=params
        )


@dataclass
class FSIGHTConfig:
    """Конфигурация FSIGHT - главный класс"""
    schema: int                 # Версия схемы
    algorithm: Algorithm        # Алгоритм
    blocks: List[Block]         # Блоки расчёта
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FSIGHTConfig':
        algorithm = Algorithm.from_dict(data.get('algorithm', {}))
        blocks = [
            Block.from_dict(b) 
            for b in data.get('blocks', [])
        ]
        
        return cls(
            schema=data.get('schema', 1),
            algorithm=algorithm,
            blocks=blocks
        )
    
    def get_block_count(self) -> int:
        """Количество блоков"""
        return len(self.blocks)
    
    def get_total_formula_count(self) -> int:
        """Общее количество формул во всех блоках"""
        return sum(block.get_formula_count() for block in self.blocks)
    
    def get_formulas_flat(self) -> List[Formula]:
        """Плоский список всех формул"""
        formulas = []
        for block in self.blocks:
            formulas.extend(block.formulas)
        return formulas
    
    def get_cubes(self) -> set:
        """Получить все cube_id"""
        cubes = set()
        for block in self.blocks:
            if block.receiver:
                cubes.add(block.receiver.cube_id)
        return cubes
    
    def get_cube_to_formulas_map(self) -> Dict[str, List[Formula]]:
        """Карта куб → формулы"""
        cube_map = {}
        for block in self.blocks:
            if block.receiver:
                cube_id = block.receiver.cube_id
                if cube_id not in cube_map:
                    cube_map[cube_id] = []
                cube_map[cube_id].extend(block.formulas)
        return cube_map
    
    def __str__(self) -> str:
        return f"FSIGHTConfig(schema={self.schema}, algorithm={self.algorithm.name}, blocks={self.get_block_count()}, formulas={self.get_total_formula_count()})"
    
    def __repr__(self) -> str:
        return self.__str__()

"""
Представление периодических выражений формул FSIGHT
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PeriodExpr:
    """Периодическое выражение - формула для конкретного периода"""
    name: str               # Название периода (например, "Нр - Кр")
    text: str               # Текстовое представление формулы
    end_date: str           # Конечная дата периода
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PeriodExpr':
        return cls(
            name=data.get('name', ''),
            text=data.get('text', ''),
            end_date=data.get('end_date', '')
        )
    
    def __str__(self) -> str:
        return f"PeriodExpr(name='{self.name}', text='{self.text}', end_date='{self.end_date}')"
    
    def __repr__(self) -> str:
        return self.__str__()

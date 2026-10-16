"""
Представление точек данных в кубах FSIGHT

Точка данных - это значение в конкретном кубе с определенными значениями измерений.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum


class ValueType(Enum):
    """Тип значения точки"""
    NUMBER = "number"
    DATE = "date"
    STRING = "string"
    BOOLEAN = "boolean"


@dataclass
class MeasurementValue:
    """Значение измерения"""
    dim_id: str       # ID измерения (DICT_YEAR, DICT_PERIOD и т.д.)
    dim_name: str     # Название измерения
    key: int          # Ключ измерения
    elem_key: str     # Ключ элемента (например, "1", "2554")
    elem_name: str    # Название элемента (например, "2018", "P0")
    
    def __str__(self) -> str:
        return f"{self.dim_name}:{self.elem_name}"


@dataclass
class DataPoint:
    """Точка данных в кубе"""
    cube_id: str                      # ID куба (CUB_OSP_1)
    cube_name: str                    # Название куба
    measurements: Dict[str, Any]      # Ключ: dim_id, Значение: MeasurementValue
    
    # Значение в точке
    value: Optional[float] = None
    value_str: Optional[str] = None
    
    def get_key(self) -> str:
        """
        Получить ключ точки (для lookup)
        Формат: CUB_OSP_1!Измерение1|Значение1|Измерение2|Значение2
        """
        parts = [self.cube_id]
        for dim_id, meas in sorted(self.measurements.items()):
            parts.append(meas.elem_name)
        return "|".join(parts)
    
    def get_formatted_value(self) -> str:
        """Получить отформатированное значение"""
        if self.value is not None:
            return str(self.value)
        return self.value_str or ""
    
    def has_value(self) -> bool:
        """Проверить, есть ли значение"""
        return self.value is not None or self.value_str is not None
    
    def __str__(self) -> str:
        key = self.get_key()
        value = self.get_formatted_value()
        return f"DataPoint(key='{key}', value={value})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class CubeContext:
    """Контекст куба с его измерениями и значениями"""
    cube_id: str
    cube_name: str
    cube_key: int
    measurements: List[MeasurementValue]  # Все измерения куба
    data: Dict[str, DataPoint] = field(default_factory=dict)  # Точки данных
    
    @classmethod
    def from_cube_data(cls, cube_id: str, cube_name: str, cube_key: int, 
                       dims: List[Dict[str, Any]]) -> 'CubeContext':
        """Создать контекст из данных о кубе"""
        measurements = []
        for dim in dims:
            # Извлекаем элементы из selection
            elements = []
            selection = dim.get('selection', {})
            if selection.get('kind') == 'list':
                elements = selection.get('elements', [])
            elif selection.get('kind') == 'all':
                elements = []  # Все элементы
            
            measurements.append(MeasurementValue(
                dim_id=dim.get('id', ''),
                dim_name=dim.get('name', ''),
                key=dim.get('key', 0),
                elem_key=elements[0]['key'] if elements else '',
                elem_name=elements[0]['name'] if elements else ''
            ))
        
        return cls(
            cube_id=cube_id,
            cube_name=cube_name,
            cube_key=cube_key,
            measurements=measurements
        )
    
    def add_point(self, point: DataPoint):
        """Добавить точку данных"""
        key = point.get_key()
        self.data[key] = point
    
    def get_point(self, key: str) -> Optional[DataPoint]:
        """Получить точку по ключу"""
        return self.data.get(key)
    
    def get_points(self) -> List[DataPoint]:
        """Получить все точки"""
        return list(self.data.values())
    
    def get_measurement_by_id(self, dim_id: str) -> Optional[MeasurementValue]:
        """Получить измерение по ID"""
        for meas in self.measurements:
            if meas.dim_id == dim_id:
                return meas
        return None
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __str__(self) -> str:
        return f"CubeContext(id='{self.cube_id}', points={len(self.data)})"


class DataLookup:
    """Поиск значений в кубах"""
    
    def __init__(self):
        self.cubes: Dict[str, CubeContext] = {}
        self.test_data: Dict[str, float] = {}
    
    def add_cube(self, cube_context: CubeContext):
        """Добавить куб"""
        self.cubes[cube_context.cube_id] = cube_context
    
    def get_cube(self, cube_id: str) -> Optional[CubeContext]:
        """Получить куб"""
        return self.cubes.get(cube_id)
    
    def get_value(self, cube_id: str, measurements: Dict[str, str]) -> Optional[float]:
        """
        Получить значение по cube_id и измерениям
        
        Args:
            cube_id: ID куба
            measurements: Словарь {dim_id: elem_key}
            
        Returns:
            Значение или None
        """
        cube = self.get_cube(cube_id)
        if not cube:
            return None
        
        # Поиск точки
        for point in cube.get_points():
            # Проверка всех измерений
            match = True
            for dim_id, elem_key in measurements.items():
                if dim_id in point.measurements:
                    if point.measurements[dim_id].elem_key != elem_key:
                        match = False
                        break
            
            if match and point.has_value():
                return point.value
        
        return None
    
    def set_value(self, cube_id: str, measurements: Dict[str, str], value: float):
        """
        Установить значение для точки
        
        Args:
            cube_id: ID куба
            measurements: Словарь {dim_id: elem_key}
            value: Значение
        """
        cube = self.get_cube(cube_id)
        if not cube:
            raise ValueError(f"Куб {cube_id} не найден")
        
        # Создание ключа
        key_parts = [cube_id]
        for dim in cube.measurements:
            key_parts.append(measurements.get(dim.dim_id, dim.elem_key))
        key = "|".join(key_parts)
        
        # Создание точки
        point = DataPoint(
            cube_id=cube_id,
            cube_name=cube.cube_name,
            measurements={m.dim_id: m for m in cube.measurements},
            value=value
        )
        cube.add_point(point)
    
    def add_values_from_dict(self, cube_id: str, values: Dict[str, float]):
        """
        Добавить несколько значений сразу
        
        Args:
            cube_id: ID куба
            values: Словарь {key: value}, где key - строка измерений
        """
        cube = self.get_cube(cube_id)
        if not cube:
            raise ValueError(f"Куб {cube_id} не найден")
        
        for key_str, value in values.items():
            # Парсинг ключа
            parts = key_str.split('|')
            if parts[0] != cube_id:
                continue
            
            measurements = {
                cube.measurements[i].dim_id: parts[i+1] 
                for i in range(min(len(cube.measurements), len(parts)-1))
            }
            
            self.set_value(cube_id, measurements, value)
    
    def __len__(self) -> int:
        total = 0
        for cube in self.cubes.values():
            total += len(cube)
        return total


# Пример использования
if __name__ == '__main__':
    # Создание контекста куба
    cube_dims = [
        {'id': 'DICT_YEAR', 'name': 'Год', 'key': 2554},
        {'id': 'DICT_PERIOD', 'name': 'Период', 'key': 2552}
    ]
    
    context = CubeContext.from_cube_data(
        cube_id='CUB_OSP_1',
        cube_name='Куб OSP 1',
        cube_key=2952,
        dims=cube_dims
    )
    
    print(f"Создан контекст: {context}")
    print(f"Измерения: {len(context.measurements)}")
    
    # Создание точек данных
    lookup = DataLookup()
    lookup.add_cube(context)
    
    # Добавление значений
    lookup.add_values_from_dict('CUB_OSP_1', {
        'CUB_OSP_1|2017|P0': 100.0,
        'CUB_OSP_1|2018|P0': 150.0,
        'CUB_OSP_1|2017|P1': 120.0
    })
    
    print(f"\nВ кубе {len(lookup)} точек данных")
    
    for point in lookup.get_cube('CUB_OSP_1').get_points():
        print(f"  {point.get_key()} = {point.get_formatted_value()}")

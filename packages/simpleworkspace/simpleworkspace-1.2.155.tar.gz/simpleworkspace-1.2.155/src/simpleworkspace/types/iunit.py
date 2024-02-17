from abc import ABC
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar('T', bound=Enum)
#Temporary typehint workaround until python 3.11 is released on ubuntu, you can then remove this here and from generic and instead use typing.Self directly
Self = TypeVar('Self', bound=Enum)

class IUnit(ABC, Generic[T, Self]):
    _TypeEnum:T

    def __init__(self, amount:float, unit: T):
        if(not isinstance(unit, self._TypeEnum)):
            raise TypeError(f"Unit must be of type: {self._TypeEnum}")
        self.amount = amount
        self.unit = unit

    def To(self, desiredUnit:T) -> Self:
        '''converts current instance to desired unit'''
        return self._converter(self.amount, self.unit, desiredUnit)
    
    @classmethod
    def _converter(cls, amount:float, unit:T, desiredUnit:T) -> Self:
        '''Base converter is responsible for the conversion between units for the unit implementation'''

        #note: for performance reason, this is not using decimal module, this means that in extreme scenarios, 
        #      for example a large unit with a lot of decimals might lose some precision converting to an extremely small unit,
        #      for real life usecases this is pretty much pointless, therefore not worth the 2x performance overhead

        totalOfRelativeUnit = amount * unit.value # since the enums are always relative to a unit, anything multiplied by it will result in that unit
        convertedAmount = totalOfRelativeUnit / desiredUnit.value
        return cls(convertedAmount, desiredUnit)

 
    def Equals(self, other:Self, allowedDeltaDiff=None, decimalPrecision=None) -> bool:
        '''
        comparator for this type of unit implementation
        converts the objects to same unit, then checking if amount is same

        :param allowedDeltaDiff: Maximum allowed difference between the amounts.
        :param decimalPrecision: Number of decimal places to consider for comparison.
        :return: True if the amounts are equal within the specified precision or delta difference, False otherwise.
        '''

        if not isinstance(other, type(self)):
           raise TypeError(f"object to compare was not of type {type(self)}")
        

        first = None
        second = None
        if(self.unit == other.unit):
            first = self.amount
            second = other.amount
        elif(self.unit.value < other.unit.value):
            #programmatically special case, converting larger units to extremely small units can lead to floating point misses
            #we therefore always want to convert upwards to the larger unit to avoid dividing with extremely small numbers
            first = self.To(other.unit).amount 
            second = other.amount
        else:
            first = self.amount
            second = other.To(self.unit).amount

        if(decimalPrecision is not None):
            first = round(first, decimalPrecision)
            second = round(second, decimalPrecision)

        if(allowedDeltaDiff is None):
            return first == second

        deltaDiff = abs(first - second)
        if(deltaDiff > allowedDeltaDiff):
            return False
        return True

        
    def __eq__(self, other:Self) -> bool:
        if not isinstance(other, type(self)):
           return NotImplemented
        
        return self.Equals(other)

    
    def __str__(self) -> str:
        '''dictates how the unit is represented in string format'''
        return f'{round(self.amount, 2)} {self.unit.name}'
    
    #region archimetric overloading
    def __gt__(self, other: Self):
        # greater than operator
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.amount > other.To(self.unit).amount

    def __ge__(self, other: Self):
        # greater than or equal operator
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.amount >= other.To(self.unit).amount

    def __lt__(self, other:Self):
        # lower than or equal operator
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.amount < other.To(self.unit).amount

    def __le__(self, other:Self):
        # lower than operator

        if not isinstance(other, type(self)):
            return NotImplemented

        return self.amount <= other.To(self.unit).amount
    
    def __iadd__(self, other: Self|float) -> Self:
        '''inplace addition of another unit type or directly a value(interpretted as current unit)'''
        if isinstance(other, type(self)):
            self.amount += other.To(self.unit).amount
        else:
            self.amount += other
        return self
    def __imul__(self, other: Self|float) -> Self:
        '''inplace multiplication of another unit type or directly a value(interpretted as current unit)'''
        if isinstance(other, type(self)):
            self.amount *= other.To(self.unit).amount
        else:
            self.amount *= other
        return self
    
    def __itruediv__(self, other: Self|float) -> Self:
        '''inplace division of another unit type or directly a value(interpretted as current unit)'''
        if isinstance(other, type(self)):
            self.amount /= other.To(self.unit).amount
        else:
            self.amount /= other
        return self

    def __isub__(self, other: Self|float) -> Self:
        '''inplace subtraction of another unit type or directly a value(interpretted as current unit)'''
        if isinstance(other, type(self)):
            self.amount -= other.To(self.unit).amount
        else:
            self.amount -= other
        return self
    #endregion archimetric overloading
from enum import Enum as _Enum
from .iunit import IUnit as _IUnit

class WeightEnum(_Enum):
    '''relative to grams'''
    Nanogram = 0.000000001
    Microgram = 0.000001
    Milligram = 0.001
    Gram = 1
    Kilogram = 1000
    MetricTon = Kilogram * 1000
    Pound = 453.59237
    Ounce = Pound / 16

class LengthEnum(_Enum):
    '''relative to meters'''
    Nanometer = 0.000000001
    Micrometer = 0.000001
    Millimeter = 0.001
    Centimeter = 0.01
    Meter = 1
    Kilometer = 1000
    
    #specialties
    SCANDINAVIAN_Mile = Kilometer * 10
    
    #US
    Inch = 0.0254
    Foot = 0.3048
    Yard = 0.9144
    US_Statute_Mile = 1609.34 
    '''commonly used mile format for US'''
    US_Nautical_Mile = 1852
    '''used in marine and aviation contexts'''


class WeightUnit(_IUnit[WeightEnum, 'WeightUnit']):
    _TypeEnum = WeightEnum



class LengthUnit(_IUnit[LengthEnum, 'LengthUnit']):
    _TypeEnum = LengthEnum
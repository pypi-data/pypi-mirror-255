from enum import Enum as _Enum
from .iunit import IUnit as _IUnit


class ByteEnum(_Enum):
    '''relative to bytes'''
    Bit = 0.125 # 1/8 of a byte
    Byte = 1
    KiloByte = 1000
    MegaByte = KiloByte * 1000
    GigaByte = MegaByte * 1000
    TeraByte = GigaByte * 1000
    PetaByte = TeraByte * 1000
    ExaByte  = PetaByte * 1000


class ByteUnit(_IUnit[ByteEnum, 'ByteUnit']):
    _TypeEnum = ByteEnum
    def GetParts(self, minPart:ByteEnum=None, maxPart:ByteEnum=None) -> dict[ByteEnum, float]:
        """Splits the current amount of relative bytes to individual parts

        :param minPart: The smallest part that should be included in the resulting dict. \
            if there are smaller parts available than minPart, they will be added as decimals to minPart 
        :param maxPart:  The highest part that should be included in the resulting dict. \
            If there are bigger parts available than maxPart, they will be added as the maxPart unit instead.
            This implies that when maxPart is specified to say MegaByte, in the case \
            that there is 1 complete GigaByte, it will instead be added to MegaBytes as 1000
        :return: dictionary of all used enums as keys, and their corresponding amount as values

        Example Usage:

        >>> ByteUnit(1.5, ByteEnum.MegaByte).GetParts()
        {
            ByteEnum.Bit: 0.0,
            ByteEnum.Byte: 0.0,
            ByteEnum.KiloByte: 500.0,
            ByteEnum.MegaByte: 1.0,
            ByteEnum.GigaByte: 0.0,
            ByteEnum.TeraByte: 0.0,
            ByteEnum.PetaByte: 0.0,
            ByteEnum.ExaByte: 0.0,
        }
        >>> ByteUnit(1.5, ByteEnum.MegaByte).GetParts(maxPart=ByteEnum.KiloByte)
        {
            ByteEnum.Bit: 0.0,
            ByteEnum.Byte: 0.0,
            ByteEnum.KiloByte: 1500.0,
        }

        >>> ByteUnit(1002.1, ByteEnum.MegaByte).GetParts(minPart=ByteEnum.MegaByte, maxPart=ByteEnum.GigaByte)
        {
            ByteEnum.MegaByte: 2.1,
            ByteEnum.GigaByte: 1.0,
        }

        """
        parts = {}
        remaining = self.amount * self.unit.value

        # sort by size and reverse it to get biggest parts to smallest
        reversed_enum = sorted(ByteEnum, key=lambda x: x.value, reverse=True)
        for enumUnit in reversed_enum:
            if maxPart and (enumUnit.value > maxPart.value):
                continue
            if enumUnit.value <= remaining:
                part = remaining // enumUnit.value
                parts[enumUnit] = part
                remaining %= enumUnit.value
            else:
                parts[enumUnit] = 0.0
            
            if minPart and (minPart == enumUnit):
                break
        
        #gather the leftovers to the smallest part if any
        if(remaining > 0):
            #use last ByteUnit in loop since that will be the smallest part
            parts[enumUnit] = parts[enumUnit] + remaining / enumUnit.value
        return parts
    

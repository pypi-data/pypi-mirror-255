from enum import Enum as _Enum

class TimeEnum(_Enum):
    '''relative to seconds'''
    NanoSecond  = 0.000000001
    MicroSecond = 0.000001 
    MilliSecond = 0.001
    Second = 1
    Minute = 60
    Hour = Minute * 60
    Day = 24 * Hour
    Week = 7 * Day


class TimeSpan:
    def __init__(self, milliSeconds:float=0, seconds:float=0, minutes:float=0, hours:float=0, days:float=0, weeks:float=0):
        self._seconds = 0
        if(milliSeconds > 0):
            self._seconds += milliSeconds * TimeEnum.MilliSecond.value
        if(seconds > 0):
            self._seconds += seconds
        if(minutes > 0):
            self._seconds += minutes * TimeEnum.Minute.value
        if(hours > 0):
            self._seconds += hours * TimeEnum.Hour.value
        if(days > 0):
            self._seconds += days * TimeEnum.Day.value
        if(weeks > 0):
            self._seconds += weeks * TimeEnum.Week.value
        
        #max precision is up to 1 milli second, more does not make sense for a timespan, when inputting milliseconds with decimals
        #it will however round to neareast full millisecond eg. a timespan with 1.1 millisecond would become 1.0 millisecond
        #and a timespan with 1.9 millisecond would become 2.0 milliseconds
        self._seconds = round(self._seconds, 3)
        return
    
    def InMilliseconds(self) -> float:
        """Return the total time span in milliseconds."""
        return self._seconds / TimeEnum.MilliSecond.value
    
    def InSeconds(self) -> float:
        """Return the total time span in Seconds."""
        return self._seconds
    
    def InMinutes(self) -> float:
        """Return the total time span in minutes."""
        return self._seconds / TimeEnum.Minute.value
    
    def InHours(self) -> float:
        """Return the total time span in hours."""
        return self._seconds / TimeEnum.Hour.value
    
    def InDays(self) -> float:
        """Return the total time span in days."""
        return self._seconds / TimeEnum.Day.value
    
    def InWeeks(self) -> float:
        """Return the total time span in weeks."""
        return self._seconds / TimeEnum.Week.value
    
    def Add(self, other:'TimeSpan') -> 'TimeSpan':
        """Add another TimeSpan object to the current TimeSpan object"""
        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for TimeSpan.Add")
        self._seconds += other._seconds
        return self
    
    def Subtract(self, other:'TimeSpan') -> 'TimeSpan':
        """Subtract another TimeSpan object to the current TimeSpan object"""
        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for TimeSpan.Subtract")
        self._seconds -= other._seconds
        return self


    @property
    def Milliseconds(self):
        milliseconds_part = self._seconds % 1 #get decimal part
        return round(milliseconds_part / TimeEnum.MilliSecond.value)

    @property
    def Seconds(self):
        return int(self._seconds % 60)

    @property
    def Minutes(self):
        return int((self._seconds / TimeEnum.Minute.value) % 60)

    @property
    def Hours(self):
        return int((self._seconds / TimeEnum.Hour.value) % 24)

    @property
    def Days(self):
        return int(self._seconds / TimeEnum.Day.value)
    
    @property
    def Weeks(self):
        return int(self._seconds / TimeEnum.Week.value)
    
    def Partition(self, minUnit:TimeEnum=None, maxUnit:TimeEnum=None) -> dict[TimeEnum, float]:
        """Splits the current timespan to individual parts

        :param minUnit: The smallest part that should be included in the resulting dict. \
            if there are smaller parts available than minUnit, they will be added as decimals to minUnit 
        :param maxUnit:  The highest part that should be included in the resulting dict. \
            If there are bigger parts available than maxUnit, they will be added as the maxUnit unit instead.
            This implies that when maxUnit is specified to say hours, in the case \
            that there is 1 complete day, it will instead be added to hours as 24
        :return: dictionary of all used enums as keys, and their corresponding amount as values

        Example Usage:

        >>> TimeSpan(seconds=30, minutes=2).Partition()
        {
            TimeEnum.MilliSeconds: 0.0,
            TimeEnum.Seconds: 30.0,
            TimeEnum.Minute: 2.0,
            TimeEnum.Hour: 0.0,
            TimeEnum.Day: 0.0,
            TimeEnum.Week: 0.0,
        }
        >>> TimeSpan(days=1).Partition(maxUnit=TimeEnum.Hour)
        {
            TimeEnum.MilliSeconds: 0.0,
            TimeEnum.Seconds: 0.0,
            TimeEnum.Minute: 0.0,
            TimeEnum.Hour: 24.0,
        }
        >>> TimeSpan(seconds=1, hours=1, milliseconds=100).Partition(minUnit=TimeEnum.Second, maxUnit=TimeEnum.Minute)
        {
            TimeEnum.Seconds: 1.1,
            TimeEnum.Minute: 60.0,
        }

        """
        parts = {}
        remaining = self._seconds

        # list time units descending to get biggest parts to smallest
        descendingUnits = [
            TimeEnum.Week,
            TimeEnum.Day,
            TimeEnum.Hour,
            TimeEnum.Minute,
            TimeEnum.Second,
            TimeEnum.MilliSecond
        ]
        for enumUnit in descendingUnits:
            if maxUnit and (enumUnit.value > maxUnit.value):
                continue
            if enumUnit.value <= remaining:
                part = remaining // enumUnit.value
                parts[enumUnit] = part
                remaining %= enumUnit.value
            else:
                parts[enumUnit] = 0.0
            
            if minUnit and (minUnit == enumUnit):
                break
        
        #gather the leftovers to the smallest part if any
        if(remaining > 0):
            #use last TimeSpan in loop since that will be the smallest part
            parts[enumUnit] = parts[enumUnit] + remaining / enumUnit.value
        return parts

    
   #region archimetric overloading
    def __eq__(self, other):
        if isinstance(other, TimeSpan):
            return self._seconds == other._seconds
        return False
    
    def __lt__(self, other:'TimeSpan'):
        #lower than operator
        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for <")
        
        return self._seconds < other._seconds
    
    def __le__(self, other:'TimeSpan'):
        # lower than or equal operator

        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for <=")

        return self._seconds <= other._seconds
    
    def __gt__(self, other:'TimeSpan'):
        # greater than operator

        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for >")

        return self._seconds > other._seconds
    
    def __ge__(self, other:'TimeSpan'):
        # greater than or equal operator

        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for >=")

        return self._seconds >= other._seconds


    def __add__(self, other:'TimeSpan') -> 'TimeSpan':
        '''addition of two timespans, returns a new independent timespan object'''
        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for +")
        
        total_seconds = self._seconds + other._seconds
        return TimeSpan(seconds=total_seconds)

    def __iadd__(self, other: 'TimeSpan') -> 'TimeSpan':
        '''inplace addition of another timespan'''
        return self.Add(other)

    def __sub__(self, other:'TimeSpan') -> 'TimeSpan':
        '''subtraction of two timespans, returns a new independent timespan object'''
        if not isinstance(other, TimeSpan):
            raise TypeError("Unsupported operand type(s) for +")
        
        total_seconds = self._seconds - other._seconds
        return TimeSpan(seconds=total_seconds)

    def __isub__(self, other: 'TimeSpan') -> 'TimeSpan':
        '''inplace subtraction of another timespan'''
        return self.Subtract(other)
    #endregion archimetric overloading



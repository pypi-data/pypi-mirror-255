import time as _time
from typing import Callable as _Callable
from simpleworkspace.types.time import TimeSpan as _TimeSpan

class StopWatch:
    def __init__(self) -> None:
        self.timeHistory = []
        self.__timeElapsed = 0
        self.__isRunning = False
        self._GetCurrentTime = _time.perf_counter

    def Start(self):
        if(self.__isRunning):
            return
        self.__isRunning = True
        self.timeHistory.append({
            "timestamp": self._GetCurrentTime(),
            "isStartEvent": True
        })
        self.__UpdateTimeElapsed()
        return
    
    def Stop(self):
        if not(self.__isRunning):
            return
        self.__isRunning = False
        self.timeHistory.append({
            "timestamp": self._GetCurrentTime(),
            "isStartEvent": False
        })
        return
    
    def Reset(self):
        '''Stops and resets the timer'''
        self.__init__()
        return

    def __UpdateTimeElapsed(self):
        endTime = self._GetCurrentTime() #take end time directly to avoid spending time while calculating
        self.__timeElapsed = 0
        startTime = None
        for timeEvent in self.timeHistory:
            if(timeEvent["isStartEvent"]):
                startTime = timeEvent["timestamp"]
                continue
            self.__timeElapsed += timeEvent["timestamp"] - startTime
            startTime = None
        if(startTime is not None):
            self.__timeElapsed += endTime - startTime

    def _PrecisionConverter(self, value:float|int, decimalPrecision:int):
        """
        Converts a value to the specified decimal precision.
        
        :param value: The value to be converted.
        :param decimalPrecision: The decimal precision.
            
        :Return: The converted value.
        """
        if(decimalPrecision < 1):
            decimalPrecision = None #None as decimalPrecision strips all decimals and returns int, but precision of even 0 returns a float 1.0
        return round(value, decimalPrecision) 

    def GetElapsedSeconds(self, decimalPrecision:int = None) -> float: 
        """
        Returns the elapsed time in seconds.
        
        :param decimalPrecision: The decimal precision of the returned time (default=None, which returns the maximum precision).
            
        :return: The elapsed time in seconds.
        """
        self.__UpdateTimeElapsed()
        timeElapsed = self.__timeElapsed
        if(decimalPrecision is not None):
            timeElapsed = self._PrecisionConverter(timeElapsed, decimalPrecision)
        return timeElapsed

    def GetElapsedMilliseconds(self, decimalPrecision:int = None):
        """
        Returns the elapsed time in milliseconds.
        
        :param decimalPrecision: The decimal precision of the returned time (default=None, which returns the maximum precision with no rounding).
            
        :return: The elapsed time in milliseconds.
        """
        
        timeElapsed = self.GetElapsedSeconds() * 1000
        if(decimalPrecision is not None):
            timeElapsed = self._PrecisionConverter(timeElapsed, decimalPrecision)
        return timeElapsed
    
    def __enter__(self):
        self.Start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Stop()
        return
    
    def __str__(self) -> str:
        return str(self.GetElapsedMilliseconds(3)) + " MS"
        

class Timer:
    ''' A live timer running on separate thread to perform events at each tick interval or after certain period has passed'''
    def __init__(self, tickInterval = _TimeSpan(seconds=1)) -> None:
        """
        :param tickInterval: Specifies how often the timer ticks, and therefore also how responsive it is
        """
        import threading

        if(type(tickInterval) is not _TimeSpan):
            raise TypeError("tick interval must be of type TimeSpan")

        self.tickInterval = tickInterval
        self._elapsed = 0
        self._stopwatch = StopWatch()
        self._eventListeners_OnTick = []
        self._eventListeners_OnElapsed = []
        self._thread_tick:threading.Thread = None
        self._thread_tick_stopEvent = threading.Event()
        self._thread_tick_isRunning = lambda: self._thread_tick is not None and self._thread_tick.is_alive()
    
    @property
    def Elapsed(self):
        '''Gets elapsed time since timer has been running'''
        return self._elapsed
    
    @Elapsed.setter
    def Elapsed(self, newValue):
        self._elapsed = newValue
        for listener in self._eventListeners_OnTick:
            listener()

        i = 0
        while i < len(self._eventListeners_OnElapsed):
            listener = self._eventListeners_OnElapsed[i]
            if(self.Elapsed >= listener["targetElapsed"]):
                listener["callback"]()
                del self._eventListeners_OnElapsed[i]
            else: #only increment index when not removing an element
                i += 1
                
        

    def AddEventListener_OnTick(self, callback: _Callable):
        '''Calls a callback at each tick of the timer'''
        self._eventListeners_OnTick.append(callback)
    
    def AddEventListener_OnElapsed(self, elapsed:_TimeSpan, callback: _Callable):
        '''Calls a callback once after a certain period of time has elapsed'''
        self._eventListeners_OnElapsed.append({
            "targetElapsed": elapsed.InSeconds(),
            "callback": callback
        })

    def Stop(self):
        '''awaits the live thread and pauses the stopwatch'''
        self._stopwatch.Stop()
        if(not self._thread_tick_isRunning()):
            return
        self._thread_tick_stopEvent.set()
        self._thread_tick.join()

    def Start(self):
        '''Starts the timer and its live thread'''
        import threading

        self._stopwatch.Start()
        if(self._thread_tick_isRunning()):
            return

        def _Tick(tickInterval: _TimeSpan):
            """:param tickInterval: how often to perform tick operation specified in seconds"""

            # prints once right away, then at end of while loop after delay each time, since the delay can be aborted,
            # we want to make sure we get one last refresh
            while not self._thread_tick_stopEvent.is_set():
                self.Elapsed = self._stopwatch.GetElapsedSeconds()
                self._thread_tick_stopEvent.wait(tickInterval.InSeconds())
            self._thread_tick_stopEvent.clear()
            return
    
        self._thread_tick = threading.Thread(target=_Tick, args=[self.tickInterval])
        self._thread_tick.daemon = True
        self._thread_tick.start()
        return
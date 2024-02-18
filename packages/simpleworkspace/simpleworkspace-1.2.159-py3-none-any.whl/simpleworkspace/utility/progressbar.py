from time import time
import sys
from typing import Callable
from simpleworkspace.types.time import TimeEnum, TimeSpan
import threading


class ProgressBar:
    '''thread safe progressbar'''

    def __init__(self, iterable=None, total=None):
        self.setting_style_fill = "█"
        '''the character to fill the progressbar with'''
        self.setting_style_barLength = 20
        '''total width in characters of the progressbar'''
        self.setting_style_infinityFormat = "{incremented} {unit} [Elapsed={elapsedTime}, Speed={speed:.1f}/s]"
        '''the style used for when the progressbar does not have a known total, since alot of statistics can not be calculated in this scenario'''
        self.setting_style_format = "|{bar}| {percentage:.1f}% [Elapsed={elapsedTime}|ETA={remainingTime}|Speed={speed:.1f}/s|{unit}={incremented}/{total}]"
        '''the style used for when the progressbar has a known total'''
        self.setting_style_unit = "pcs"
        '''states what one increment is, such as 1 piece or 1 byte etc'''
        self.setting_printOnIncrement = True
        '''print progressbar on every increment call'''

        if total is None and iterable is not None:
            if hasattr(iterable, "__len__"):
                total = len(iterable)

        self.total = total
        self._iterable = iterable
        if self._iterable is not None:
            self._iterator = iter(iterable)
        self.stats_incremented = 0
        '''the total incremented amount'''
        self._stats_startTime = time()  # Track start time
        self._stats_previousIncrementCount = 0
        self._stats_previousIncrementTime = self._stats_startTime  # Track previous time for increment

        self._CallbackSettings_OnIncrementSteps = None
        self._CallbackSettings_OnReachedTarget = None

        self._lock = threading.Lock()
        self._thread_PrintAsync = None
        self._thread_PrintAsync_stopEvent = threading.Event()
        self._thread_PrintAsync_IsRunning = lambda: self._thread_PrintAsync is not None and self._thread_PrintAsync.is_alive()


    def IsFinished(self):
        if self.total is None:
            return False  # without a total, its not possible to say its finished
        if self.stats_incremented >= self.total:
            return True
        return False

    def Increment(self, increment=1):
        '''Increases the progress bar by the specified increment value'''
        
        with self._lock:
            self.stats_incremented += increment
            if self.setting_printOnIncrement:
                self.Print()

            if self._CallbackSettings_OnIncrementSteps:
                for setting in self._CallbackSettings_OnIncrementSteps:
                    setting["effective_increments"] += increment
                    if setting["effective_increments"] >= setting["increments"]:
                        setting["callback"]()
                        setting["effective_increments"] = 0
            
            if(self._CallbackSettings_OnReachedTarget):
                i = 0
                while i < len(self._CallbackSettings_OnReachedTarget):
                    setting = self._CallbackSettings_OnReachedTarget[i]
                    if(self.stats_incremented >= setting['increments']):
                        setting["callback"]()
                        del self._CallbackSettings_OnReachedTarget[i]
                    else: #only increment index when not removing an element
                        i += 1
        return

    def Print(self):
        '''Prints the progress bar to the console'''

        sys.stdout.write("\r\x1b[2K")  # backtrack the console line with \r, and clear the old text with rest of the sequence
        sys.stdout.write(self.ToString())
        sys.stdout.flush()
        return
    
    def PrintAsync(self, refreshDelay=1):
        '''
        Prints the progress bar live in a new thread with the refresh delay specified in settings

        disables autoprint on increment if its on, the live progress thread will take care
        of printing it with better statistics since increments are gathered over potentially a longer duration

        :param refreshDelay: how often to refresh bar stats and visuals, delay is specified in seconds
        '''

        if(self._thread_PrintAsync_IsRunning()):
            return

        def _PrintAsync(refreshDelay: float):
            # prints once right away, then at end of while loop after delay each time, since the delay can be aborted,
            # we want to make sure we get one last refresh
            self.Print()
            while not self._thread_PrintAsync_stopEvent.is_set():
                if self.IsFinished():
                    break
                self._thread_PrintAsync_stopEvent.wait(refreshDelay)
                self.Print()
            self._thread_PrintAsync_stopEvent.clear()
            self.Console_CleanUp()
            return
    
        self.setting_printOnIncrement = False

        self._thread_PrintAsync = threading.Thread(target=_PrintAsync, args=[refreshDelay])
        self._thread_PrintAsync.daemon = True
        self._thread_PrintAsync.start()
        return

    def PrintAsync_Stop(self):
        '''stops the live print thread, and awaits until thread closed'''
        
        if(not self._thread_PrintAsync_IsRunning()):
            return
        self._thread_PrintAsync_stopEvent.set()
        self._thread_PrintAsync.join()

    def PrintAsync_Wait(self):
        if(not self._thread_PrintAsync_IsRunning()):
            return
        self._thread_PrintAsync.join()

    def ToString(self):
        '''gets the progressbar information as a string'''
        current_time = time()
        elapsedTime = current_time - self._stats_startTime
        elapsedTime_str = self._FormatTime(elapsedTime)
        elapsedTime_SinceLastIncrement = current_time - self._stats_previousIncrementTime
        incrementsSinceLastPrint = self.stats_incremented - self._stats_previousIncrementCount
        incrementsPerSecond = 0 if elapsedTime_SinceLastIncrement == 0 else (incrementsSinceLastPrint) / elapsedTime_SinceLastIncrement
        self._stats_previousIncrementTime = current_time
        self._stats_previousIncrementCount = self.stats_incremented

        if self.total is None:
            return self.setting_style_infinityFormat.format(incremented=self.stats_incremented, elapsedTime=elapsedTime_str, speed=incrementsPerSecond, unit=self.setting_style_unit)

        # Calculate remaining time
        remainingTime = 0 if incrementsPerSecond == 0 else (self.total - self.stats_incremented) / incrementsPerSecond
        remainingTime_str = self._FormatTime(remainingTime)

        # progressbar style
        filled_length = min(int(self.setting_style_barLength * self.stats_incremented / self.total), self.setting_style_barLength)  # use min incase bar length is over 100%
        bar = self.setting_style_fill * filled_length + "-" * (self.setting_style_barLength - filled_length)
        percentage = self.stats_incremented * 100 / self.total

        return self.setting_style_format.format(bar=bar, percentage=percentage, elapsedTime=elapsedTime_str, remainingTime=remainingTime_str, speed=incrementsPerSecond, incremented=self.stats_incremented, total=self.total, unit=self.setting_style_unit)

    def Console_CleanUp(self):
        '''
        Cleans up console by flushing out progressbar and adding newline to make it prepared for regular use
        
        - is not needed when iterable supplied or printasync, since these have an definite stop point, eg end of iterable or stop of printasync thread. 
        '''
        sys.stdout.write('\n')
        sys.stdout.flush()

    def AddEventListener_OnIncrementSteps(self, increments: int, callback: Callable):
        '''
        Set a callback to be executed after every x increments.
        :param increments: The number of increments after which the callback should be executed.
        :param callback: The user-specified function to be called after 'increments' number of increments
        '''
        if self._CallbackSettings_OnIncrementSteps is None:
            self._CallbackSettings_OnIncrementSteps = []
        self._CallbackSettings_OnIncrementSteps.append({"increments": increments, "callback": callback, "effective_increments": 0})
    
    def AddEventListener_OnReachedTarget(self, targetIncrements: int, callback: Callable):
        '''
        Set a callback to be executed one time after specified increments are surpassed.
        :param targetIncrements: The number of increments after which the callback should be executed.
        :param callback: The user-specified function to be called once the reached increments surpasses the specified total
        '''
        if self._CallbackSettings_OnReachedTarget is None:
            self._CallbackSettings_OnReachedTarget = []
        self._CallbackSettings_OnReachedTarget.append({"increments": targetIncrements, "callback": callback})

    def _FormatTime(self, seconds: float):
        '''
        Formats the given time in seconds to the format HH:MM:SS.
        :param seconds: The time in seconds to format.
        '''
        timespan = TimeSpan(seconds=seconds)
        timeParts = timespan.Partition(minUnit=TimeEnum.Second, maxUnit=TimeEnum.Hour)
        for i in timeParts.keys():
            timeParts[i] = round(timeParts[i])  # remove all decimals
        return "{0:02d}:{1:02d}:{2:02d}".format(timeParts[TimeEnum.Hour], timeParts[TimeEnum.Minute], timeParts[TimeEnum.Second])  # 00:00:00 format

    def __len__(self):
        return self.total

    def __iter__(self):
        return self

    def __next__(self):
        '''Returns the next value from the iterator and increments the progress bar'''

        try:
            value = next(self._iterator)
            self.Increment()
            return value
        except StopIteration:
            self.Console_CleanUp()
            raise StopIteration

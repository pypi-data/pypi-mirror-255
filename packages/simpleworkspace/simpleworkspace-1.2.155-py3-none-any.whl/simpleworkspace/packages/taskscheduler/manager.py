from logging import Logger
from datetime import datetime
from simpleworkspace.utility.linq import LINQ
from simpleworkspace.utility.time import StopWatch
from simpleworkspace.settingsproviders import SettingsManager_JSON
from simpleworkspace.types.time import TimeSpan
import os
from zlib import crc32
from simpleworkspace.utility import module
from simpleworkspace.io import directory
from concurrent.futures import ThreadPoolExecutor
import traceback
from threading import Lock, Event
from typing import Callable
from datetime import datetime
from .model import ITask

class TaskSchedulerManager:
    def __init__(self, settingsPath: str, logger: Logger) -> None:
        self.logger = logger
        self._settingsPath = settingsPath
        self._settingsManager = SettingsManager_JSON(self._settingsPath)
        self._settingsManager.LoadSettings()
        self._lock_settingsManager = Lock()
        self._tasks = {} #type: dict[str, ITask]
        '''all registered tasks'''
        self._FLAG_SAVESETTINGS = False
        self._mainloop_stopEvent = Event()
        self._config_maxThreads = 6
        '''max threads to use for running tasks'''
        self._threading_activeTasks = set()
        self._lock_threading_activeTasks = Lock()

        self.settings_ScanInterval = TimeSpan(seconds=60)
        ''' Specifies how often to scan tasks for OnSchedule event. Lower this if you need higher resolution for more precise date triggers'''

    class _TaskResult:
        def __init__(self) -> None:
            self.stopwatch = StopWatch()
            self.output = None #type:str
            self.error = None #type:str

        @property
        def ElapsedMS(self):
            return self.stopwatch.GetElapsedMilliseconds(decimalPrecision=2)

    def _RunTaskEvent(self, task: ITask, eventFunc: Callable):
        eventName = eventFunc.__name__
        taskResult = self._TaskResult()
        taskResult.stopwatch.Start()

        taskTitle = task._task_id if not task.task_description else f'{task._task_id}({task.task_description})'
        try:
            output = eventFunc()
            taskResult.output = f"Event {eventName}[{taskResult.ElapsedMS} MS]: {taskTitle}"
            if(output):
                taskResult.output += f", Output: {output}"
        except Exception as e:
            taskResult.error = f"Event {eventName} FAILED[{taskResult.ElapsedMS} MS]: {taskTitle}, Error: {traceback.format_exc()}"
        return taskResult

    def _SaveSettingsIfNeeded(self):
        '''instead of saving after each small modification, change when modifications are made'''
        if not (self._FLAG_SAVESETTINGS): 
            return

        with self._lock_settingsManager:
            self._settingsManager.SaveSettings()
            self._FLAG_SAVESETTINGS = False
            
    def LoadTasks(self, tasks: list[ITask]):
        '''Load list of ITasks into memory'''
        for task in tasks:
            if not isinstance(task, ITask):
                raise TypeError(f"Task must be of type ITask, got {type(task)}")
            self._tasks[task._task_id] = task
        return self

    def LoadTasksFromFile(self, path:str):
        '''Scans a file for all ITask implementing classes and loads them into memory'''
        if(not os.path.isfile(path)):
            raise FileNotFoundError(path)
        
        taskInstances = []
        
        dynamicModuleName = f"{os.path.basename(path)}_{crc32(path.encode())}"
        dynamicModule = module.ImportModuleDynamically(dynamicModuleName, path)
        dynamicModuleInfo = module.ModuleInfo(dynamicModule)
        classes = dynamicModuleInfo.GetDeclaredClasses(ITask, includeChildsOnly=True)
        for className,obj in classes.items():
            taskInstances.append(obj())

        self.LoadTasks(taskInstances)  

        return self

    def LoadTasksFromDirectory(self, path:str, recursive=True):
        '''Scans a directory for all ITask implementing classes and loads them into memory'''

        if(not os.path.isdir(path)):
            raise NotADirectoryError(path)
        
        maxDepth = None if recursive == True else 1
        taskInstances = []
        pyFiles = directory.Scan(path, 
                             includeDirs=False, 
                             filter=r'/\.py$/i',
                             maxDepth=maxDepth)
        for filepath in pyFiles:
            self.LoadTasksFromFile(filepath)

        return self


    def _InitializeTasks(self):
        if("TaskSchedules" not in self._settingsManager.Settings):
            self._settingsManager.Settings["TaskSchedules"] = {}
            self._FLAG_SAVESETTINGS = True

        taskSettings = self._settingsManager.Settings["TaskSchedules"]

        #clear invalid/old settings
        for key in list(taskSettings.keys()):
            if(key not in self._tasks): #this includes ignored tasks aswell, since we dont want to reset it's schedule when its temporarily ignored
                del taskSettings[key]
                self._FLAG_SAVESETTINGS = True

        for task in self._tasks.values():
            #skip tasks without schedules, eg no interval or custom nextschedule handler
            if(not task._HasEvent_Schedule):
                continue

            scheduleName = ""
            if(task.task_interval is not None):
                scheduleName += str(task.task_interval.InSeconds())
            if(task.NextSchedule.__func__ is not ITask.NextSchedule):
                scheduleName += f"FN"

            if(task._task_id not in taskSettings) or (taskSettings[task._task_id]["scheduleName"] != scheduleName):
                taskSettings[task._task_id] = {
                    "scheduleName": scheduleName,
                    "lastRunDate": None
                }
                self._FLAG_SAVESETTINGS = True

            if(taskSettings[task._task_id]["lastRunDate"] is not None):
                task._cache_lastRunDate = datetime.fromisoformat(taskSettings[task._task_id]["lastRunDate"])

        self._SaveSettingsIfNeeded()            
        return
    
    def Run(self):
        #region ThreadHandlers
        def RunTaskEvent_OnStartUp(task: ITask):
            return self._RunTaskEvent(task, task.On_StartUp)
        
        def RunTaskEvent_OnSchedule(task: ITask):
            results = self._RunTaskEvent(task, task.On_Schedule)
            task._cache_lastRunDate = datetime.now()
            with self._lock_settingsManager:
                self._settingsManager.Settings["TaskSchedules"][task._task_id]["lastRunDate"] = task._cache_lastRunDate.isoformat()
                self._FLAG_SAVESETTINGS = True
            return results

        def OnTaskFinish(taskResult: TaskSchedulerManager._TaskResult):
            if(taskResult.error):
                self.logger.error(taskResult.error)
            else:
                self.logger.info(taskResult.output)
            return
        
        def ToggleTaskState(taskId:str, active:bool):
            with self._lock_threading_activeTasks:
                if(active):
                    self._threading_activeTasks.add(taskId)
                else:
                    self._threading_activeTasks.remove(taskId)

        #endregion ThreadHandlers

        self._InitializeTasks()
        self.logger.info(f"Event Start")

        activeTaskList = LINQ(self._tasks.values()) \
            .Where(lambda task: task.task_ignore == False) \
            .ToList()

        pool = ThreadPoolExecutor(max_workers=self._config_maxThreads)
        #skip none overriden ones
        tasksWithStartUp = LINQ(activeTaskList).Where(lambda task: task._HasEvent_StartUp)
        
        #ensures all startup tasks are finished before continuing to onSchedule
        for taskResult in pool.map(RunTaskEvent_OnStartUp, tasksWithStartUp):
            OnTaskFinish(taskResult)

        tasksWithSchedules = LINQ(activeTaskList) \
            .Where(lambda task: task._HasEvent_Schedule) \
            .ToList()

        while not self._mainloop_stopEvent.is_set():
            for task in tasksWithSchedules:
                if(task._task_id in self._threading_activeTasks):
                    continue #already running skip
                shouldRun = task.NextSchedule(task._cache_lastRunDate)
                if not (shouldRun):
                    continue
                ToggleTaskState(task._task_id, active=True)
                promise = pool.submit(RunTaskEvent_OnSchedule, task)
                promise.add_done_callback(lambda x: OnTaskFinish(x.result()))
                promise.add_done_callback(lambda x, taskId=task._task_id: ToggleTaskState(taskId, active=False)) #add taskId arg in lambda to use current variable in loop

            self._SaveSettingsIfNeeded() #save once per full iteration if needed
            self._mainloop_stopEvent.wait(self.settings_ScanInterval.InSeconds())

        self._SaveSettingsIfNeeded() #save once per full iteration if needed
        pool.shutdown()



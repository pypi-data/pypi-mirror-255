import logging as _logging
from simpleworkspace.types.byte import ByteEnum as _ByteEnum
import sys as _sys
import os as _os
import time as _time

class _BaseLogger:
    class Formatter(_logging.Formatter):
        def __init__(self, forceUTC=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if(forceUTC):
                self._timezoneStr = '+0000'
                self.converter = _time.gmtime
            else:
                self._timezoneStr = _time.strftime('%z') #uses '+HHMM'

        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                # support %z and %f in datefmt (struct_time doesn't carry ms or tz)
                datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
                datefmt = datefmt.replace('%z', self._timezoneStr)
                s = _time.strftime(datefmt, ct)
            else:
                s = _time.strftime(self.default_time_format, ct)
                if self.default_msec_format:
                    s = self.default_msec_format % (s, record.msecs)
            return s
        
        @classmethod
        def Factory(cls, useUTCTime=True, includeTime=True, includeLevel=True, includeTrace=True):
            '''Styling: "<Time> <Level> <Trace(moduleName, lineNo)>: <Message>"'''

            fmt = []
            if(includeTime):
                fmt.append('%(asctime)s')
            if(includeLevel):
                fmt.append('%(levelname)s')
            if(includeTrace):
                fmt.append('<%(module)s,%(lineno)s>')
            if(len(fmt) > 0):
                fmt[-1] = fmt[-1] + ':' #add colon to last part before message if needed
            fmt.append('%(message)s')
            fmt = ' '.join(fmt)

            return cls(forceUTC=useUTCTime, fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S.%f%z")

    
    @staticmethod
    def RegisterAsUnhandledExceptionHandler(logger):
        def UncaughtExeceptionHandler(exc_type, exc_value, exc_traceback):
            if not issubclass(exc_type, KeyboardInterrupt): #avoid registering console aborts such as ctrl+c etc
                logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            _logging.shutdown()
            _sys.__excepthook__(exc_type, exc_value, exc_traceback)

        _sys.excepthook = UncaughtExeceptionHandler
    
class RotatingFileLogger:
    @classmethod
    def GetLogger(cls, filepath, minimumLogLevel=_logging.DEBUG, maxBytes=_ByteEnum.MegaByte.value * 100, maxRotations=10, useUTCTime=True, registerGlobalUnhandledExceptions=False):
        from logging.handlers import RotatingFileHandler
        
        def rotator(source, dest):
            import gzip 
            with open(source, "rb") as sf:
                gzip_fp = gzip.open(dest, "wb")
                gzip_fp.writelines(sf)
                gzip_fp.close()
            _os.remove(source)

        logger = _logging.getLogger(f"__ROTATINGFILELOGGER_{hash((filepath,minimumLogLevel,maxBytes,maxRotations,useUTCTime))}")
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        FileLogger._CreateParentFolders(filepath)

        logger.setLevel(minimumLogLevel)
        handler = RotatingFileHandler(filepath, maxBytes=maxBytes, backupCount=maxRotations, encoding='utf-8')
        handler.rotator = rotator
        handler.namer = lambda name: name + ".gz"
        handler.setFormatter(_BaseLogger.Formatter.Factory(useUTCTime=useUTCTime, includeTime=True, includeLevel=True, includeTrace=True))
        logger.addHandler(handler)

        return logger

class FileLogger:
    @classmethod
    def GetLogger(cls, filepath, minimumLogLevel=_logging.DEBUG, useUTCTime=True, registerGlobalUnhandledExceptions=False):
        logger = _logging.getLogger("__FILELOGGER_" + str(hash(f"{filepath}{minimumLogLevel}{useUTCTime}")))
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        cls._CreateParentFolders(filepath)
        logger.setLevel(minimumLogLevel)
        handler = _logging.FileHandler(filepath, encoding='utf-8')
        handler.setFormatter(_BaseLogger.Formatter.Factory(useUTCTime=useUTCTime, includeTime=True, includeLevel=True, includeTrace=True))
        logger.addHandler(handler)
        return logger
    
    @staticmethod
    def _CreateParentFolders(filepath:str):
        filepath = _os.path.realpath(filepath)
        directoryPath = _os.path.dirname(filepath)
        if(directoryPath in ("", "/")):
            return
        _os.makedirs(directoryPath, exist_ok=True)

class StreamLogger:
    @classmethod
    def GetLogger(cls, 
                  minimumLogLevel=_logging.DEBUG, useUTCTime=False, 
                  registerGlobalUnhandledExceptions=False,  stream=_sys.stdout,
                  fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=False):
        stdoutLogger = _logging.getLogger("__STDOUTLOGGER__" + str(hash(f"{minimumLogLevel}{useUTCTime}{fmt_includeTime}{fmt_includeLevel}{fmt_includeTrace}{stream.__hash__()}")))
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(stdoutLogger)
        if(stdoutLogger.hasHandlers()):
            return stdoutLogger
        stdoutLogger.setLevel(minimumLogLevel)
        stdoutLogger.addHandler(cls.CreateHandler(useUTCTime=useUTCTime, stream=stream, fmt_includeTime=fmt_includeTime, fmt_includeLevel=fmt_includeLevel, fmt_includeTrace=fmt_includeTrace))
        return stdoutLogger
    
    @staticmethod
    def CreateHandler(useUTCTime=False, stream=_sys.stdout, fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=False):
        handler = _logging.StreamHandler(stream)
        handler.setFormatter(_BaseLogger.Formatter.Factory(useUTCTime=useUTCTime, includeTime=fmt_includeTime, includeLevel=fmt_includeLevel, includeTrace=fmt_includeTrace))
        return handler

class DummyLogger:
    @classmethod
    def GetLogger(cls):
        dummyLogger = _logging.getLogger("@@BLACKHOLE@@")
        if(dummyLogger.hasHandlers()):
            return dummyLogger
        dummyLogger.addHandler(_logging.NullHandler())
        dummyLogger.propagate = False
        return dummyLogger

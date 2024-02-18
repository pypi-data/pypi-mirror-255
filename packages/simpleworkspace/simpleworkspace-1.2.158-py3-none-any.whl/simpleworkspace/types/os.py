from enum import Enum as _Enum
class OperatingSystemEnum(_Enum):
    Windows = 1
    MacOS = 2
    Linux = 3
    Unkown = 4

    @classmethod
    def GetCurrentOS(cls):
        """ Get the enum value of the current operating system. """
        
        import sys
        
        if sys.platform.startswith('win'):
            return cls.Windows
        elif sys.platform.startswith('linux'):
            return cls.Linux
        elif sys.platform.startswith('darwin'):
            return cls.MacOS
        else:
            return cls.Unkown
        

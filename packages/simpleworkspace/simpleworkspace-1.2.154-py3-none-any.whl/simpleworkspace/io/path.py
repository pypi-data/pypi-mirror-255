import os as _os
import string as _string

class PathInfo:
    from functools import cached_property as _cached_property

    def __init__(self, path:str, normalizePath = True) -> None:
        """
        :param normalizePath: all backslashes are replaced with forward ones for compability when enabled
        """
        self._normalizePath = normalizePath
        self.Path = self._NormalizePathIfNeeded(path)
        '''the input path, example case: a/b/test.exe -> a/b/test.exe'''

    def CreateDirectory(self):
        '''
        Create all non existing directiores in specified path, ignores if directory already exists
        :raises Exception: if path exists and is not a directory
        '''
        from simpleworkspace.io import directory

        if not (self.Exists):
            directory.Create(self.Path)
            return
        if not (self.IsDirectory):
            raise Exception(f'Path "{self.AbsolutePath}" already exists and is NOT a directory')
        return #path is already directory

    def CreateFile(self, data: bytes | str = None):
        '''
        Creates or overwrites file if exists
        :raises Exception: if path exists and is not a file
        '''
        from simpleworkspace.io import file

        if (not self.Exists) or (self.IsFile):
            file.Create(self.Path, data)
            return
        
        raise Exception(f'Path "{self.AbsolutePath}" already exists and is NOT a file')

    @property
    def IsDirectory(self) -> bool:
        return _os.path.isdir(self.Path)
    @property
    def IsFile(self) -> bool:
        return _os.path.isfile(self.Path)
    
    @property
    def IsSymlink(self) -> bool:
        return _os.path.islink(self.Path)
    
    @property
    def Exists(self) -> bool:
        return _os.path.exists(self.Path)
    
    def Join(self, *otherPaths:str):
        return self.__class__(_os.path.join(self.Path, *otherPaths), self._normalizePath)

    @property
    def Stats(self):
        return _os.stat(self.Path) #follows symlink by default

    @_cached_property
    def AbsolutePath(self) -> str:
        '''converts the input path to an absolute path, example case: a/b/test.exe -> c:/a/b/test.exe'''
        return self._NormalizePathIfNeeded(_os.path.realpath(self.Path))

    @property
    def Tail(self) -> str:
        '''Retrieves everything before filename, example case: a/b/test.exe -> a/b'''

        tail, head = self._HeadTail
        return tail

    @property
    def Head(self) -> str:
        '''Retrieves everything after last slash which would be the filename or directory, example case: a/b/test.exe -> test.exe'''

        tail,head = self._HeadTail
        return head
    
    @property
    def Filename(self) -> str:
        '''retrieves filename, example case: a/b/test.exe -> test.exe'''

        return self.Head
    
    @property
    def FilenameWithoutExtension(self):
        '''retrieves filename without extension, example case: a/b/test.exe -> test'''

        filename = self._FilenameSplit[0]
        return filename
    
    @property
    def Extension(self):
        '''
        Retrieves fileextension without the dot, example case: a/b/test.exe -> exe\n
        Returns empty string if there is no extension
        '''

        if(len(self._FilenameSplit) == 2):
            return self._FilenameSplit[1]
        return ""
    
    @property
    def Parent(self) -> 'PathInfo':
        return PathInfo(self.Tail)

    def RelativeTo(self, startPath:'str|PathInfo'):
        '''
        Return a relative version of a path with starting point of startPath
        
        Example:

        >>> PathInfo("/root/assets/img.png").RelativeTo('/root')
        'assets/img.png'
        '''
        if isinstance(startPath, type(self)):
            startPath = startPath.Path
        return self._NormalizePathIfNeeded(_os.path.relpath(self.Path, startPath))

    @_cached_property
    def _HeadTail(self) -> tuple[str,str]:
        return _os.path.split(self.Path)
    
    @_cached_property
    def _FilenameSplit(self) -> str:
        return self.Head.rsplit(".", 1)
    
    @property
    def __str__(self) -> str:
        return self.Path
    
    def _NormalizePathIfNeeded(self, path:str):
        return path.replace("\\", "/") if self._normalizePath else path
    
    def __truediv__(self, otherPath:str):
        return self.Join(otherPath)
    
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.Path == other.Path #could be swapped for potentially abspath to make different path syntax match aswell
    
def FindEmptySpot(filepath: str):
    pathInfo = PathInfo(filepath)
    TmpPath = filepath
    i = 1
    while _os.path.exists(TmpPath) == True:
        TmpPath = _os.path.join(pathInfo.Tail, f"{pathInfo.FilenameWithoutExtension}_{i}.{pathInfo.Extension}")
        i += 1
    return TmpPath

def GetAppdataPath(appName=None, companyName=None):
    """
    Retrieves crossplatform Appdata folder.\n
    * no arguments        -> %appdata%/\n
    * appName only        -> %appdata%/appname\n
    * appname and company -> %appdata%/appname/companyName\n
    """
    from simpleworkspace.types.os import OperatingSystemEnum
    

    currentOS = OperatingSystemEnum.GetCurrentOS()
    if currentOS == OperatingSystemEnum.Windows:
        pathBuilder = _os.getenv('APPDATA')
    elif currentOS == OperatingSystemEnum.MacOS:
        pathBuilder = _os.path.expanduser('~/Library/Application Support/')
    else:
        pathBuilder = _os.getenv('XDG_DATA_HOME', _os.path.expanduser("~/.local/share"))

    if(companyName is not None):
        pathBuilder = _os.path.join(pathBuilder, companyName)
    if(appName is not None):
        pathBuilder = _os.path.join(pathBuilder, appName)
    return pathBuilder
    
def SantizePath(path:str, allowedCharset = _string.ascii_letters + _string.digits + " .-_/\\"):
    from simpleworkspace.utility import strings
    return strings.Sanitize(path, allowedCharset=allowedCharset)

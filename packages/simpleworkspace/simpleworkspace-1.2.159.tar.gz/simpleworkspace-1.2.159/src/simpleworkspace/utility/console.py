import os as _os
from simpleworkspace.types.os import OperatingSystemEnum as _OperatingSystemEnum
from simpleworkspace.utility import strings as _strings

def LevelPrint(level:int, msg="", flush=False, end='\n'):
    print(_strings.IndentText(msg, level, indentStyle='    '), flush=flush, end=end)


def LevelInput(level:int, msg="", flush=False, end='\n'):
    return input(_strings.IndentText(msg, level, indentStyle='    '), flush=flush, end=end)


def AnyKeyDialog(msg=""):
    if msg != "":
        msg += " - "
    msg += "Press enter to continue..."
    input(msg)

def Clear():
    _os.system("cls" if _os.name == "nt" else "clear")
    return

def Prompt_YesOrNo(question:str) -> bool:
    '''
    prompts user indefinitely until one of the choices are picked

    output style: "<question> [Y/N]:"
    @return: boolean yes=True, no=False
    '''
    
    while(True):
        answer = input(question + " [Y/N]:").upper()
        if(answer == "Y"):
            return True
        elif(answer == "N"):
            return False



def Print_SelectFileDialog(message="Enter File Paths",printlevel=0) -> list[str]|None:
    import shlex
    LevelPrint(printlevel, f"-{message}")
    filepathString = LevelInput(printlevel, "-")
    filepaths = shlex.split(filepathString)
    if(len(filepaths) == 0):
        return None
    return filepaths


class ConsoleSettingsManagerExtension():
    from simpleworkspace.settingsproviders import SettingsManager_Base as _SettingsManager_Base
    __Command_Delete = "#delete"

    def __init__(self, settingsManager: _SettingsManager_Base) -> None:
        self.SettingsManager = settingsManager
        

    def __Console_ChangeSettings(self):
        while True:
            Clear()
            LevelPrint(0, "[Change Settings]")
            LevelPrint(1, "0. Save Settings and go back.(Type cancel to discard changes)")
            LevelPrint(1, "1. Add a new setting")
            LevelPrint(2, "[Current Settings]")
            dictlist = []
            dictlist_start = 2
            dictlist_count = 2
            for key in self.SettingsManager.Settings:
                LevelPrint(3, str(dictlist_count) + ". " + key + " : " + str(self.SettingsManager.Settings[key]))
                dictlist.append(key)
                dictlist_count += 1
            LevelPrint(1)
            choice = input("-Choice: ")
            if choice == "cancel":
                self.SettingsManager.LoadSettings()
                AnyKeyDialog("Discarded changes!")
                break
            if choice == "0":
                self.SettingsManager.SaveSettings()
                LevelPrint(1)
                AnyKeyDialog("Saved Settings!")
                break
            elif choice == "1":
                LevelPrint(1, "Setting Name:")
                keyChoice = LevelInput(1, "-")
                LevelPrint(1, "Setting Value")
                valueChoice = LevelInput(1, "-")
                self.SettingsManager.Settings[keyChoice] = valueChoice
            else:
                IntChoice = None
                try:
                    IntChoice = int(choice)
                except Exception as e:
                    pass
                if IntChoice is None or (IntChoice >= dictlist_start and IntChoice < dictlist_count):
                    continue
                else:
                    key = dictlist[IntChoice - dictlist_start]
                    LevelPrint(2, '(Leave empty to cancel, or type "' + self.__Command_Delete + '" to remove setting)')
                    LevelPrint(2, ">> " + str(self.SettingsManager.Settings[key]))
                    choice = LevelInput(2, "Enter new value: ")
                    if choice == "":
                        continue
                    elif choice == self.__Command_Delete:
                        del self.SettingsManager.Settings[key]
                    else:
                        self.SettingsManager.Settings[key] = choice
        return

    def Console_PrintSettingsMenu(self):
        from simpleworkspace.io.path import PathInfo
        while(True):
            Clear()
            LevelPrint(0, "[Settings Menu]")
            LevelPrint(1, "1.Change settings")
            LevelPrint(1, "2.Reset settings")
            LevelPrint(1, "3.Open Settings Directory")
            LevelPrint(1, "0.Go back")
            LevelPrint(1)
            choice = input("-")
            if choice == "1":
                self.__Console_ChangeSettings()
            elif choice == "2":
                LevelPrint(1)
                confirmed = Prompt_YesOrNo("-Confirm Reset!")
                if confirmed:
                    self.SettingsManager.ClearSettings()
                    self.SettingsManager.SaveSettings()
                    LevelPrint(1)
                    AnyKeyDialog("*Settings resetted!")
            elif choice == "3":
                pathInfo = PathInfo(self.SettingsManager._settingsPath)
                _os.startfile(pathInfo.Tail)
            else:
                break
        return
 
class CommandBuilder:            
    def __init__(self):
        self._os = _OperatingSystemEnum.GetCurrentOS()
        self._eolSequence = "\r\n" if self._os == _OperatingSystemEnum.Windows else "\n"
        self._commentSequence = "@REM" if self._os == _OperatingSystemEnum.Windows else "#"
        self._shellType = "cmd.exe" if self._os == _OperatingSystemEnum.Windows else "/bin/sh"
        self._queuedCommands:list[str] = []

        self._QueueDefaults()

    def _QueueDefaults(self):
        if(self._os == _OperatingSystemEnum.Windows):
            self.Queue('@echo off')
        else:
            self.Queue('#!/bin/sh')
    
    def Clear(self):
        self.__init__()

    def Queue(self, command:str, isComment = False, escapeNewlines=False):
        """Queues a shell command

        :param isComment: when true, comments out the command
        :param escapeNewlines: escapes newlines by replacing them with a space ' '
        """
        if(escapeNewlines):
            command = command.replace('\r\n', ' ')
            command = command.replace('\n', ' ')
        if(isComment):
            command = f'{self._commentSequence} {command}'
            command = command.replace('\n', f'\n{self._commentSequence} ') #if there are newlines, comment those out aswell
        self._queuedCommands.append(command)

    def Execute(self):
        import tempfile
        import subprocess

        try:
            # Create a temporary file
            fileExtension = 'bat' if self._os == _OperatingSystemEnum.Windows else "sh"
            fp = tempfile.NamedTemporaryFile(prefix='__CommandBuilder__', suffix=f'.{fileExtension}', delete=False)
            for line in self.Reader():
                fp.write(line.encode())
            fp.close()
                
            runCommand = [self._shellType, fp.name]
            if(self._os == _OperatingSystemEnum.Windows):
                runCommand = [self._shellType, "/c", fp.name] #when invoking with cmd.exe, it requires the /c flag
            result = subprocess.run(
                runCommand,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE 
            )

            if(result.returncode != 0): #something went bad
                raise ChildProcessError(f'Script execution got bad return code({result.returncode}), STDERR: {result.stderr}')
            return result
        finally:
            fp.close()
            _os.remove(fp.name)


    def Reader(self):
        ''' Iterator to read the generatable file line by line '''
        for line in self._queuedCommands:
            yield line + self._eolSequence + self._eolSequence

    def __str__(self):
        return ''.join(self.Reader())
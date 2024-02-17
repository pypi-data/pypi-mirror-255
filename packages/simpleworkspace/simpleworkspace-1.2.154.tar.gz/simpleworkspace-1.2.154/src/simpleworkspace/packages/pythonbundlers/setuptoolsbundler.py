import sys as _sys
import os as _os
import simpleworkspace.loader as _sw
from simpleworkspace.utility.time import StopWatch as _StopWatch
from .dependecy import toml as _toml
from simpleworkspace.logproviders import StreamLogger

class SetupToolsBundler:
    def __init__(self):
        from simpleworkspace.utility.module import ModuleInfo

        mainModule = ModuleInfo.Factory_MainModule()
        self.entryPath = mainModule.pathInfo.Parent.AbsolutePath
        self.pyproject = _toml.load(f"{self.entryPath}/pyproject.toml")
        self.packageName = self.pyproject['project']['name']
        _sys.path.insert(0, self.entryPath + "/src") #ensure imports to the package is done through the dev version
        self._stopwatch = _StopWatch()
        self._Register_CLI()
        self.logger = StreamLogger.GetLogger(stream=_sys.stdout, fmt_includeTime=False, fmt_includeLevel=False, fmt_includeTrace=False)
        
    def _Register_CLI(self):
        from argparse import ArgumentParser
        parser = ArgumentParser(add_help=False)
        parser.add_argument('--build')
        args, rest = parser.parse_known_args()
        self.cli_Build:str = args.build

    def Command(self, args:list[str], title=None):
        import subprocess
        if(title is None):
            title = f'{args}'
        self.logger.info(f"> Executing command {title}...")
        with _StopWatch() as sw1:
            result = subprocess.run(args)
            if(result.returncode != 0): #something went bad
                raise RuntimeError(f"command failed... stdout: {result.stdout}; stderr: {result.stderr};")
        self.logger.info(f' - Command finished in {sw1.GetElapsedSeconds(2)} seconds...')

    def Pipe_Init(self):
        self._stopwatch.Start()
        initMessage = f'> Bundling {self.packageName}'
        if(self.cli_Build):
            initMessage += ', Build=' + self.cli_Build
        self.logger.info(initMessage)

    def Pipe_CleanUp(self):
        if not (_os.path.isfile(f'{self.entryPath}/pyproject.toml')):
            raise LookupError("Could not find a pyproject.toml file in entry directory, aborting cleanup as safety precaution")
        self.logger.info("> Performing CleanUp...")
        for pathToRemove in [
            f'{self.entryPath}/dist/',
            f'{self.entryPath}/build/',
            f'{self.entryPath}/src/{self.packageName}.egg-info/'
        ]:
            if(_os.path.isdir(pathToRemove)):
                _sw.io.directory.RemoveTree(pathToRemove)
                self.logger.info(f'    - Removed {pathToRemove}')
        return


    def Pipe_RunTests(self, testpath='tests/'):
        import unittest 
        self.logger.info("> Running unittests...")
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(_os.path.join(self.entryPath, testpath))
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        if(result.failures or result.errors): #something went bad
            raise Exception("Unittests failed!")

    def Pipe_IncrementPackageVersion(self):
        def BumpMinorVersion(versionString):
            versionInfo = versionString.split(".")
            versionInfo[2] = str(int(versionInfo[2]) + 1)
            newVersion = ".".join(versionInfo)
            return newVersion
        
        ### increment module version ###
        currentVersion = self.pyproject["project"]["version"]
        newVersion = BumpMinorVersion(currentVersion)
        self.pyproject["project"]["version"] = newVersion
        _sw.io.file.Create(f"{self.entryPath}/pyproject.toml", _toml.dumps(self.pyproject))
        self.logger.info(f"> Incremented package version from {currentVersion} -> {newVersion}...")

    def Pipe_Build(self):
        ### build package ###
        self.Command([_sys.executable, '-m', 'build', self.entryPath])

    def Pipe_Install(self, developmentMode=False):
        ### install on computer as editable/dev mode ###
        if(developmentMode):
            self.Command([_sys.executable, "-m", "pip", "install", "--editable", self.entryPath])
        else:
            self.Command([_sys.executable, "-m", "pip", "install", self.entryPath])

    def Pipe_Publish(self, username:str, token:str):
        ### upload to pypi ###
        self.Command(
            [_sys.executable, "-m",
                "twine", "upload",
                "-u", username, 
                "-p", token,
                f"{self.entryPath}/dist/*"
            ], 
            title='Upload To PyPi')

    def Pipe_Finish(self):
        self.logger.info(f"> Installer finished! Elapsed: {self._stopwatch.GetElapsedSeconds(decimalPrecision=1)} seconds")



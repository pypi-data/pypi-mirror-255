
from typing import TYPE_CHECKING
class __LazyImporter__:
    def __init__(self, package, moduleName):
        self._package = package
        self._moduleName = moduleName
        self._moduleImport = None

    def __getattr__(self, attr):
        import importlib

        if self._moduleImport is None:
            self._moduleImport = importlib.import_module(self._moduleName, self._package)
        
        return getattr(self._moduleImport, attr)
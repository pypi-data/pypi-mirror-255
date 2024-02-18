from simpleworkspace.__lazyimporter__ import __LazyImporter__, TYPE_CHECKING
if(TYPE_CHECKING):
    from . import byte as _byte
    from . import time as _time
    from . import os as _os
    from . import measurement as _measurement


byte: '_byte' = __LazyImporter__(__package__, '.byte')
time: '_time' = __LazyImporter__(__package__, '.time')
os: '_os' = __LazyImporter__(__package__, '.os')
measurement: '_measurement' = __LazyImporter__(__package__, '.measurement')

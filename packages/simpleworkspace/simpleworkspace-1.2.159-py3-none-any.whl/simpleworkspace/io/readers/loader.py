from simpleworkspace.__lazyimporter__ import __LazyImporter__, TYPE_CHECKING
if(TYPE_CHECKING):
    from . import csvreader as _csvreader
    from . import logreader as _logreader

csvreader: '_csvreader' = __LazyImporter__(__package__, '.csvreader')
logreader: '_logreader' = __LazyImporter__(__package__, '.logreader')

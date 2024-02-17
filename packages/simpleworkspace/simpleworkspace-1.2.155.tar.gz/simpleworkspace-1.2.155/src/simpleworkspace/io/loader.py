from simpleworkspace.__lazyimporter__ import __LazyImporter__, TYPE_CHECKING
if(TYPE_CHECKING):
    from . import directory as _directory
    from . import file as _file
    from . import path as _path
    from . import archive as _archive
    from .readers import loader as _readers

directory: '_directory' = __LazyImporter__(__package__, '.directory')
file: '_file' = __LazyImporter__(__package__, '.file')
path: '_path' = __LazyImporter__(__package__, '.path')
archive: '_archive' = __LazyImporter__(__package__, '.archive')
readers: '_readers' = __LazyImporter__(__package__, '.readers.loader')

from simpleworkspace.__lazyimporter__ import __LazyImporter__, TYPE_CHECKING
if(TYPE_CHECKING):
    from . import dialogs as _dialogs

dialogs: '_dialogs' = __LazyImporter__(__package__, '.dialogs')

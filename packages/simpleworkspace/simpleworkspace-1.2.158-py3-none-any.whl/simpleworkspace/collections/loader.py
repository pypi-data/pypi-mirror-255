from simpleworkspace.__lazyimporter__ import __LazyImporter__, TYPE_CHECKING
if(TYPE_CHECKING):
    from . import observables as _observables
observables: '_observables' = __LazyImporter__(__package__, '.observables')
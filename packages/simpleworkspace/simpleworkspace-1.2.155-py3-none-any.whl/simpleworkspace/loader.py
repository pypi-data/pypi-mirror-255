#directory ./packages are not loaded by autoloaders, modules under there are usually speciality cases and should be imported directly since they are not commonly used

from simpleworkspace.__lazyimporter__ import __LazyImporter__, TYPE_CHECKING
if(TYPE_CHECKING):
    from .io import loader as _io
    from .types import loader as _types
    from .utility import loader as _utility
    from .db import loader as _db
    from .collections import loader as _collections
    from .gui import loader as _gui
    from . import logproviders as _logproviders
    from . import settingsproviders as _settingsproviders
    from . import app as _app

io: '_io' = __LazyImporter__(__package__, '.io.loader')
types: '_types' = __LazyImporter__(__package__, '.types.loader')
utility: '_utility' = __LazyImporter__(__package__, '.utility.loader')
db: '_db' = __LazyImporter__(__package__, '.db.loader')
collections: '_collections' = __LazyImporter__(__package__, '.collections.loader')
gui: '_gui' = __LazyImporter__(__package__, '.gui.loader')
logproviders: '_logproviders' = __LazyImporter__(__package__, '.logproviders')
settingsproviders: '_settingsproviders' = __LazyImporter__(__package__, '.settingsproviders')
app: '_app' = __LazyImporter__(__package__, '.app')

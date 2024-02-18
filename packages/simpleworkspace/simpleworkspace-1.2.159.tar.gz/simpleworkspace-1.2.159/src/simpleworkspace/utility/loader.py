from simpleworkspace.__lazyimporter__ import __LazyImporter__, TYPE_CHECKING
if(TYPE_CHECKING):
    from . import console as _console
    from . import module as _module
    from . import regex as _regex
    from . import time as _time
    from . import strings as _strings
    from . import bytes as _bytes
    from . import linq as _linq
    from . import progressbar as _progressbar
    from . import parallel as _parallel

console: '_console' = __LazyImporter__(__package__, '.console')
module: '_module' = __LazyImporter__(__package__, '.module')
regex: '_regex' = __LazyImporter__(__package__, '.regex')
time: '_time' = __LazyImporter__(__package__, '.time')
strings: '_strings' = __LazyImporter__(__package__, '.strings')
bytes: '_bytes' = __LazyImporter__(__package__, '.bytes')
linq: '_linq' = __LazyImporter__(__package__, '.linq')
progressbar: '_progressbar' = __LazyImporter__(__package__, '.progressbar')
parallel: '_parallel' = __LazyImporter__(__package__, '.parallel')
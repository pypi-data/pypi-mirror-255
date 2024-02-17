import functools as _functools
import sys as _sys

def Time(_func=None, *, repeat=1, stream=_sys.stdout):
    def decorator_profile(func):
        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            from simpleworkspace.utility.time import StopWatch
            nonlocal stream

            funcInfo = [f'{func.__module__}.{func.__name__}']
            if(repeat > 1):
                funcInfo.append(f'Rep={repeat}')

            t1 = StopWatch()
            t1.Start()
            if repeat > 1:
                for _ in range(repeat - 1):
                    func(*args, **kwargs)
            result = func(*args, **kwargs)
            t1.Stop()

            stream.write(f'<{", ".join(funcInfo)}> Time -> {t1.GetElapsedMilliseconds(2)} MS\n')
            stream.flush()
            return result
        return wrapper
    return decorator_profile if _func is None else decorator_profile(_func)
    
def Memory(_func=None, *, repeat=1, stream=_sys.stdout):
    def decorator_profile(func):
        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            import tracemalloc
            from simpleworkspace.types.byte import ByteEnum, ByteUnit

            nonlocal stream

            funcInfo = [f'{func.__module__}.{func.__name__}']
            if(repeat > 1):
                funcInfo.append(f'Rep={repeat}')

            tracemalloc.start()
            current1, _ = tracemalloc.get_traced_memory()
            if repeat > 1:
                for _ in range(repeat - 1):
                    func(*args, **kwargs)
            result = func(*args, **kwargs)
            current2, funcPeak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            funcDiff = '{:+}'.format(ByteUnit(current2 - current1, ByteEnum.Byte).To(ByteEnum.KiloByte).amount)
            funcPeak = round(ByteUnit(funcPeak, ByteEnum.Byte).To(ByteEnum.KiloByte).amount, 2)

            stream.write(f'<{", ".join(funcInfo)}> Memory -> Diff:{funcDiff}KB, Peak:{funcPeak}KB\n')
            stream.flush()
            return result
        return wrapper
    return decorator_profile if _func is None else decorator_profile(_func)

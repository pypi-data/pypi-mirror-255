def profile(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        from line_profiler import LineProfiler

        prof = LineProfiler()
        try:
            return prof(func)(*args, **kwargs)
        finally:
            prof.print_stats()

    return wrapper


@profile
def tester():
    retval = []
    for x in range(100):
        retval.extend([1234, 1234])
    return retval


tester()

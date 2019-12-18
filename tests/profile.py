# encoding: utf-8
""" Small helper. """

import cProfile
import pstats


def measure(func):
    """ The decorator. """
    def profiling(*args, **kwargs):
        """ The profiler. """
        prof = cProfile.Profile()
        prof.enable()
        ret = prof.runcall(func, *args, **kwargs)
        prof.disable()
        ps = pstats.Stats(prof).sort_stats('cumulative')
        print(func.func_name)
        ps.print_stats(20)
        return ret

    profiling.func_name = func.func_name
    return profiling

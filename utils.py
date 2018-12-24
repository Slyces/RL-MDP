verbose = 0
def vprint(*args, v=1, **kwargs):
    """ prints its content if verbose >= v """
    if verbose >= v: print(*args, **kwargs)

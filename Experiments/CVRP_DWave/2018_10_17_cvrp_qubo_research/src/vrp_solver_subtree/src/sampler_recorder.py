"""A recorder for D-Wave sampler allowing one to retrieve timings when using QBSolv."""
from collections import namedtuple
from contextlib import contextmanager
from functools import wraps


def _make_recorder(func, target, key, store_arguments=True):
    """Wrap given callable in wrapper that records returned timings and used arguments.

    :param func: callable to wrap. In theory this could be anything that returns
     object `result` such tht `result.info['timing']` is well defined. In practice
     its meant for sample_qubo and sample_ising methods of D-Wave solvers.
    :type func: callable.
    :param target: a target list to which calls will be appended.
    :type target: list
    :param key: key that will identify this particular callable in the target.
     See below for explanation.
    :type key: str
    :param store_arguments: whether to store arguments used when calling functions.
     Setting to False reduces storage requirements and is therefore recommended for
     problems.
    :type store_arguments: bool
    :returns: a function with the same interface as `func` which additionally records all.
     its calls into `target` list. More precisely for every call of `func`. a dict with
     following entries will be appended to `target`:
     - 'method`: `key`, a field indicating which callable placed entry in `target`
     - `timing`: timing structure returned by sampler.
     - `args`, `kwargs`: arguments and keyword arguments used. Those entries are only present
       if `store_arguments` is set to True.
    :rtype: callable.
    """
    @wraps(func)
    def _wrapped(*args, **kwargs):
        record = {}
        if store_arguments:
            record['args'] = args
            record['kwargs'] = kwargs
        result = func(*args, **kwargs)
        record['timing'] = result.info['timing']
        record['method'] = key
        target.append(record)
        return result
    return _wrapped


@contextmanager
def record_sampler_invocations(sampler, store_arguments=True):
    """Turn on temporary recording of sampler invocations.

    This context manager yields a list of records that can be used
    in (or after) exiting the `with` statement.

    See recording_eample.py for a sample usage.
    """
    target = []
    sample_qubo_wrapper = _make_recorder(sampler.sample_qubo, target, 'qubo', store_arguments)
    sample_ising_wrapper = _make_recorder(sampler.sample_ising, target, 'ising', store_arguments)
    original_sample_qubo = sampler.sample_qubo
    original_sample_ising = sampler.sample_ising

    try:
        sampler.sample_qubo = sample_qubo_wrapper
        sampler.sample_ising = sample_ising_wrapper
        yield target
    finally:
        sampler.sample_qubo = original_sample_qubo
        sampler.sample_ising = original_sample_ising

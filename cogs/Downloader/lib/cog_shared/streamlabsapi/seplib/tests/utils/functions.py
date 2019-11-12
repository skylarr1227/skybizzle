import asyncio
from types import FunctionType

from typing import Coroutine, Tuple, Dict


def simple_return_function(return_value: object):
    def fake_function(*args, **kwargs):
        return return_value

    return fake_function


def simple_coroutine(name: str) -> Coroutine:
    """
    Generates a simple async function in the local scope that does nothing (pass) and returns its coroutine.

    The coroutine has its future explicitly ensured, which is a hacky workaround for tests
    which need to pass around corotuines as parameters, and will avoid the pesky
    "async function was never awaited" warnings.

    :param name: Name of the async function to be created.
    :return: Simple async coroutine that just passes, generated in the local scope.
    """
    exec("""async def {name}():\n  pass""".format(name=name))
    coroutine = locals()[name]()
    asyncio.ensure_future(coroutine)
    return coroutine


def coroutine_return(return_value: object) -> FunctionType:
    """
    Generates a simple async function in the local scope which, when called and awaited, will return the object passed
    :param return_value: object which will be returned verbatim when the function is called and awaited
    :return: Returns a coroutine function
    """

    async def coroutine(*coargs, **cokwargs):
        return return_value

    return coroutine


def coroutine_return_args() -> FunctionType:
    """
    Generates an async function which, when called and awaited, will return a dict with the args and kwargs
    passed to the async function.

    This can be used to validate that the patched method properly passes args along.

    :param args: args to pass to the async function
    :param kwargs: kwargs to pass to the async function
    :return: Dict with keys "args" and "kwargs" containing the passed args/kwargs
    """

    async def coroutine(*coargs, **cokwargs):
        return {"args": coargs, "kwargs": cokwargs}

    return coroutine


def coroutine_return_modified_args() -> Tuple[Dict, FunctionType]:
    return_dict = {}

    async def coroutine(*coargs, **cokwargs):
        return_dict.update({"args": coargs, "kwargs": cokwargs})
        return return_dict

    return return_dict, coroutine


def coroutine_exception(exception: BaseException) -> FunctionType:
    """
    Generates a simple coroutine in the local scope which, when called and awaited, will raise the specified exception.
    :param exception: Exception which will be raised when the function is called and awaited
    :return: Returns
    """

    async def coroutine(*coargs, **cokwargs):
        raise exception

    return coroutine

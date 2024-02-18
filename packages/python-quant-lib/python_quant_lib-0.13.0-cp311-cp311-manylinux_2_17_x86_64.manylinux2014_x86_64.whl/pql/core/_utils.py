from typing import Callable
from pql.core.context import get_eval_ctx


def eval_request(func: Callable) -> Callable:
    """
    Automatically passes the context to eval requests if not automatically
    specified
    """

    def wrapper(self, *args, **kwargs):
        ctx = kwargs.pop("ctx", None) or get_eval_ctx()
        return func(self, *args, ctx=ctx, **kwargs)

    return wrapper

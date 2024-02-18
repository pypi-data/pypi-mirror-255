"""
#
# Wait utilities
#
# Copyright(c) 2021-, Carium, Inc. All rights reserved.
#
"""

from typing import Callable, Optional

from tenacity import retry, stop_after_delay, wait_fixed
from tenacity.stop import stop_base
from tenacity.wait import wait_base


class Waiter:

    DEFAULT_RERAISE = True
    DEFAULT_STOP = stop_after_delay(60)
    DEFAULT_WAIT = wait_fixed(1)

    def __init__(
        self,
        reraise: bool = DEFAULT_RERAISE,
        stop: Optional[stop_base] = None,
        wait: Optional[wait_base] = None,
    ):
        self.t_reraise = reraise
        self.t_stop = stop or self.DEFAULT_STOP
        self.t_wait = wait or self.DEFAULT_WAIT

    def reduce(
        self,
        *functions: Callable,
        reraise: Optional[bool] = None,
        wait: Optional[wait_base] = None,
        stop: Optional[stop_base] = None,
    ) -> list:
        kwargs = {
            "reraise": reraise if reraise is not None else self.t_reraise,
            "stop": stop or self.t_stop,
            "wait": wait or self.t_wait,
        }

        @retry(**kwargs)
        def _retry_fn():
            results = [functions[0]()]
            for func in functions[1:]:
                results.append(func(results[-1]))
            assert results[-1]
            return results

        return _retry_fn()

    def wait(self, function: Callable, **kwargs):
        """Shortcut to `multi_step` with single callable"""
        return self.reduce(*[function], **kwargs)[0]

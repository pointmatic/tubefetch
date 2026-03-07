# Copyright (c) 2026 Pointmatic
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Gentlify throttle configuration for retry and rate limiting."""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any, Callable, TypeVar, cast

from gentlify import RetryConfig, Throttle

from tubefetch.core.errors import FetchException
from tubefetch.core.options import FetchOptions

T = TypeVar("T")


def create_throttle(options: FetchOptions) -> Throttle:
    """Create a configured Throttle instance based on FetchOptions.

    Args:
        options: FetchOptions with retry and rate limit configuration.

    Returns:
        Configured Throttle instance with retry and concurrency settings.
    """
    # Configure retry based on options.retries
    retry_config = None
    if options.retries > 0:
        retry_config = RetryConfig(
            max_attempts=options.retries,
            backoff="exponential_jitter",
            base_delay=1.0,
            max_delay=60.0,
            retryable=_is_retryable_exception,
        )

    # Create throttle with configured retry
    # Note: max_concurrency is set to 1 for single-video processing
    # For batch processing, this will be handled at the pipeline level
    throttle = Throttle(
        max_concurrency=1,
        retry=retry_config,
    )

    return throttle


def _is_retryable_exception(exc: BaseException) -> bool:
    """Determine if an exception should be retried.

    Uses the FetchException.retryable attribute if available,
    otherwise falls back to checking for common transient errors.

    Args:
        exc: Exception to check.

    Returns:
        True if the exception should be retried, False otherwise.
    """
    # Check if it's a FetchException with retryable attribute
    if isinstance(exc, FetchException):
        return exc.retryable

    # Fallback: common transient errors
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return True

    return False


async def async_execute_with_retry(
    func: Callable[..., T],
    throttle: Throttle,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute a synchronous function with gentlify retry logic.

    Args:
        func: Synchronous function to execute.
        throttle: Configured Throttle instance.
        *args: Positional arguments to pass to func.
        **kwargs: Keyword arguments to pass to func.

    Returns:
        Result of func execution.

    Raises:
        Exception: If all retry attempts are exhausted.
    """

    async def _async_wrapper(slot: Any) -> T:
        # Execute the synchronous function in the event loop's executor
        loop = asyncio.get_event_loop()
        # Use partial to handle both args and kwargs
        func_with_args = partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, func_with_args)

    result = await throttle.execute(_async_wrapper)
    return cast(T, result)


def execute_with_retry(
    func: Callable[..., T],
    throttle: Throttle,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute a synchronous function with gentlify retry logic (sync wrapper).

    This is a synchronous wrapper around async_execute_with_retry for use
    in synchronous contexts.

    Args:
        func: Synchronous function to execute.
        throttle: Configured Throttle instance.
        *args: Positional arguments to pass to func.
        **kwargs: Keyword arguments to pass to func.

    Returns:
        Result of func execution.

    Raises:
        Exception: If all retry attempts are exhausted.
    """
    return asyncio.run(async_execute_with_retry(func, throttle, *args, **kwargs))

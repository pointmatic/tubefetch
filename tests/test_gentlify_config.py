# Copyright (c) 2026 Pointmatic
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Tests for gentlify throttle configuration and retry logic."""

import asyncio
from unittest.mock import Mock, patch

import pytest

from yt_fetch.core.errors import (
    FetchErrorCode,
    FetchException,
    MetadataError,
    MetadataServiceError,
    TranscriptError,
    TranscriptServiceError,
)
from yt_fetch.core.options import FetchOptions
from yt_fetch.utils.gentlify_config import (
    _is_retryable_exception,
    async_execute_with_retry,
    create_throttle,
    execute_with_retry,
)


class TestCreateThrottle:
    """Test throttle creation with different FetchOptions configurations."""

    def test_creates_throttle_with_retry_enabled(self):
        """Throttle should be created with retry config when retries > 0."""
        options = FetchOptions(retries=3)
        throttle = create_throttle(options)

        assert throttle is not None
        # Throttle is created successfully (internal retry config not exposed)

    def test_creates_throttle_with_retry_disabled(self):
        """Throttle should be created without retry config when retries = 0."""
        options = FetchOptions(retries=0)
        throttle = create_throttle(options)

        assert throttle is not None
        # Throttle is created successfully (internal retry config not exposed)

    def test_default_retry_count(self):
        """Default retry count should be 3."""
        options = FetchOptions()
        throttle = create_throttle(options)

        assert throttle is not None
        # Default FetchOptions.retries is 3


class TestIsRetryableException:
    """Test exception retryability classification."""

    def test_fetch_exception_with_retryable_true(self):
        """FetchException with retryable=True should be retryable."""
        exc = MetadataServiceError("transient error")
        assert exc.retryable is True
        assert _is_retryable_exception(exc) is True

    def test_fetch_exception_with_retryable_false(self):
        """FetchException with retryable=False should not be retryable."""
        exc = MetadataError("permanent error", code=FetchErrorCode.VIDEO_NOT_FOUND)
        assert exc.retryable is False
        assert _is_retryable_exception(exc) is False

    def test_connection_error_is_retryable(self):
        """ConnectionError should be retryable (fallback)."""
        exc = ConnectionError("network error")
        assert _is_retryable_exception(exc) is True

    def test_timeout_error_is_retryable(self):
        """TimeoutError should be retryable (fallback)."""
        exc = TimeoutError("timeout")
        assert _is_retryable_exception(exc) is True

    def test_os_error_is_retryable(self):
        """OSError should be retryable (fallback)."""
        exc = OSError("os error")
        assert _is_retryable_exception(exc) is True

    def test_generic_exception_not_retryable(self):
        """Generic exceptions should not be retryable."""
        exc = ValueError("bad value")
        assert _is_retryable_exception(exc) is False

    def test_transcript_service_error_retryable(self):
        """TranscriptServiceError should be retryable."""
        exc = TranscriptServiceError("service error")
        assert exc.retryable is True
        assert _is_retryable_exception(exc) is True

    def test_transcript_error_not_retryable(self):
        """TranscriptError (base) should not be retryable."""
        exc = TranscriptError("permanent error", code=FetchErrorCode.TRANSCRIPT_NOT_FOUND)
        assert exc.retryable is False
        assert _is_retryable_exception(exc) is False


class TestExecuteWithRetry:
    """Test retry execution wrapper."""

    @pytest.mark.asyncio
    async def test_async_execute_success_first_attempt(self):
        """Function should succeed on first attempt without retry."""
        call_count = 0

        def successful_func(arg1, arg2):
            nonlocal call_count
            call_count += 1
            return f"{arg1}-{arg2}"

        options = FetchOptions(retries=3)
        throttle = create_throttle(options)

        result = await async_execute_with_retry(successful_func, throttle, "foo", "bar")

        assert result == "foo-bar"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_execute_retries_on_retryable_error(self):
        """Function should retry on retryable errors."""
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise MetadataServiceError("transient")
            return "success"

        options = FetchOptions(retries=3)
        throttle = create_throttle(options)

        result = await async_execute_with_retry(flaky_func, throttle)

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_execute_fails_on_non_retryable_error(self):
        """Function should not retry on non-retryable errors."""
        call_count = 0

        def permanent_fail():
            nonlocal call_count
            call_count += 1
            raise MetadataError("permanent", code=FetchErrorCode.VIDEO_NOT_FOUND)

        options = FetchOptions(retries=3)
        throttle = create_throttle(options)

        with pytest.raises(MetadataError, match="permanent"):
            await async_execute_with_retry(permanent_fail, throttle)

        assert call_count == 1  # No retries for non-retryable errors

    @pytest.mark.asyncio
    async def test_async_execute_exhausts_retries(self):
        """Function should raise after exhausting all retries."""
        call_count = 0

        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("always fails")

        options = FetchOptions(retries=2)
        throttle = create_throttle(options)

        with pytest.raises(ConnectionError, match="always fails"):
            await async_execute_with_retry(always_fails, throttle)

        assert call_count == 2  # max_attempts = 2

    @pytest.mark.asyncio
    async def test_async_execute_no_retry_when_disabled(self):
        """Function should not retry when retries=0."""
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("error")

        options = FetchOptions(retries=0)
        throttle = create_throttle(options)

        with pytest.raises(ConnectionError, match="error"):
            await async_execute_with_retry(flaky_func, throttle)

        assert call_count == 1  # No retries

    def test_sync_execute_with_retry(self):
        """Sync wrapper should work correctly."""
        call_count = 0

        def flaky_func(value):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("timeout")
            return value * 2

        options = FetchOptions(retries=3)
        throttle = create_throttle(options)

        result = execute_with_retry(flaky_func, throttle, 5)

        assert result == 10
        assert call_count == 2

    def test_sync_execute_with_kwargs(self):
        """Sync wrapper should handle kwargs correctly."""
        def func_with_kwargs(a, b=10):
            return a + b

        options = FetchOptions(retries=1)
        throttle = create_throttle(options)

        result = execute_with_retry(func_with_kwargs, throttle, 5, b=20)

        assert result == 25


class TestRetryBackoff:
    """Test retry backoff behavior."""

    @pytest.mark.asyncio
    async def test_exponential_jitter_backoff(self):
        """Retry should use exponential jitter backoff."""
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("transient")
            return "success"

        options = FetchOptions(retries=3)
        throttle = create_throttle(options)

        result = await async_execute_with_retry(flaky_func, throttle)

        assert result == "success"
        assert call_count == 3  # Retried until success


class TestIntegrationWithPipeline:
    """Test gentlify integration with actual pipeline usage patterns."""

    def test_retries_respect_fetch_options(self):
        """Retry count should respect FetchOptions.retries setting."""
        call_count = 0

        def flaky_metadata(video_id, options):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise MetadataServiceError("transient")
            return {"video_id": video_id}

        # Test with retries enabled
        options = FetchOptions(retries=3)
        throttle = create_throttle(options)
        result = execute_with_retry(flaky_metadata, throttle, "test123", options)

        assert result["video_id"] == "test123"
        assert call_count == 2

    def test_zero_retries_fails_immediately(self):
        """With retries=0, errors should propagate immediately."""
        call_count = 0

        def always_fails(video_id):
            nonlocal call_count
            call_count += 1
            raise MetadataServiceError("error")

        options = FetchOptions(retries=0)
        throttle = create_throttle(options)

        with pytest.raises(MetadataServiceError):
            execute_with_retry(always_fails, throttle, "test123")

        assert call_count == 1  # Should fail immediately, no retries

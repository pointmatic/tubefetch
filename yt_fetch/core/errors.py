# Copyright (c) 2025 Pointmatic
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Structured error handling for yt-fetch operations."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class FetchErrorCode(StrEnum):
    """Machine-readable error classification for yt-fetch operations."""

    # --- Content unavailable (permanent or semi-permanent) ---
    VIDEO_NOT_FOUND = "video_not_found"
    VIDEO_PRIVATE = "video_private"
    VIDEO_DELETED = "video_deleted"
    VIDEO_AGE_RESTRICTED = "video_age_restricted"
    VIDEO_GEO_BLOCKED = "video_geo_blocked"
    TRANSCRIPTS_DISABLED = "transcripts_disabled"
    TRANSCRIPT_NOT_FOUND = "transcript_not_found"

    # --- Transient / infrastructure ---
    RATE_LIMITED = "rate_limited"
    SERVICE_ERROR = "service_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"

    # --- Client-side ---
    INVALID_VIDEO_ID = "invalid_video_id"
    MISSING_DEPENDENCY = "missing_dependency"
    CONFIGURATION_ERROR = "configuration_error"

    # --- Catch-all ---
    UNKNOWN = "unknown"


class FetchPhase(StrEnum):
    """Pipeline phase where an error occurred."""

    METADATA = "metadata"
    TRANSCRIPT = "transcript"
    MEDIA = "media"


class FetchError(BaseModel):
    """A structured error from a yt-fetch operation."""

    code: FetchErrorCode
    message: str
    phase: FetchPhase
    retryable: bool
    video_id: str
    details: dict[str, Any] | None = None


class FetchException(Exception):
    """Base exception for all yt-fetch errors."""

    def __init__(self, message: str, code: FetchErrorCode, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


# --- Transcript exceptions ---


class TranscriptError(FetchException):
    """Transcript fetch failed."""


class TranscriptNotFound(TranscriptError):
    """No transcript available for the requested languages."""

    def __init__(self, message: str):
        super().__init__(message, code=FetchErrorCode.TRANSCRIPT_NOT_FOUND, retryable=False)


class TranscriptsDisabledError(TranscriptError):
    """Transcripts are disabled for this video."""

    def __init__(self, message: str):
        super().__init__(message, code=FetchErrorCode.TRANSCRIPTS_DISABLED, retryable=False)


class TranscriptServiceError(TranscriptError):
    """Transient service error during transcript fetch."""

    def __init__(self, message: str, code: FetchErrorCode = FetchErrorCode.SERVICE_ERROR):
        super().__init__(message, code=code, retryable=True)


# --- Metadata exceptions ---


class MetadataError(FetchException):
    """Metadata fetch failed."""


class VideoNotFoundError(MetadataError):
    """Video does not exist or is inaccessible."""

    def __init__(self, message: str, code: FetchErrorCode = FetchErrorCode.VIDEO_NOT_FOUND):
        super().__init__(message, code=code, retryable=False)


class MetadataServiceError(MetadataError):
    """Transient service error during metadata fetch."""

    def __init__(self, message: str, code: FetchErrorCode = FetchErrorCode.SERVICE_ERROR):
        super().__init__(message, code=code, retryable=True)


# --- Media exceptions ---


class MediaError(FetchException):
    """Media download failed."""


class MediaServiceError(MediaError):
    """Transient service error during media download."""

    def __init__(self, message: str, code: FetchErrorCode = FetchErrorCode.SERVICE_ERROR):
        super().__init__(message, code=code, retryable=True)


# --- Error classification helper ---


def _classify_exception(exc: Exception) -> FetchErrorCode:
    """Best-effort classification of an exception into a FetchErrorCode.

    Priority: exception type → HTTP status → exception message string.
    """
    # --- 1. Classify by exception type (most reliable) ---
    # Import here to avoid circular dependencies and optional dependency issues
    try:
        from youtube_transcript_api import (
            NoTranscriptAvailable,
            NoTranscriptFound,
            TranscriptsDisabled,
            VideoUnavailable,
        )

        if isinstance(exc, TranscriptsDisabled):
            return FetchErrorCode.TRANSCRIPTS_DISABLED
        if isinstance(exc, (NoTranscriptFound, NoTranscriptAvailable)):
            return FetchErrorCode.TRANSCRIPT_NOT_FOUND
        if isinstance(exc, VideoUnavailable):
            return FetchErrorCode.VIDEO_NOT_FOUND
    except ImportError:
        pass

    # Check TimeoutError before OSError since TimeoutError is a subclass of OSError
    if isinstance(exc, TimeoutError):
        return FetchErrorCode.TIMEOUT
    if isinstance(exc, (ConnectionError, OSError)):
        return FetchErrorCode.NETWORK_ERROR

    # --- 2. Classify by HTTP status code (if available) ---
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status == 429:
        return FetchErrorCode.RATE_LIMITED
    if isinstance(status, int) and 500 <= status < 600:
        return FetchErrorCode.SERVICE_ERROR

    # --- 3. Fallback: classify by message string (fragile) ---
    exc_str = str(exc).lower()
    if "timeout" in exc_str:
        return FetchErrorCode.TIMEOUT
    if "connection" in exc_str or "dns" in exc_str:
        return FetchErrorCode.NETWORK_ERROR
    if "private" in exc_str:
        return FetchErrorCode.VIDEO_PRIVATE
    if "not found" in exc_str or "not exist" in exc_str or "unavailable" in exc_str:
        return FetchErrorCode.VIDEO_NOT_FOUND
    if "age" in exc_str and "restrict" in exc_str:
        return FetchErrorCode.VIDEO_AGE_RESTRICTED
    if "disabled" in exc_str:
        return FetchErrorCode.TRANSCRIPTS_DISABLED

    return FetchErrorCode.UNKNOWN

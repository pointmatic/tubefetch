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

"""Tests for structured error handling."""

import pytest

from tubefetch.core.errors import (
    FetchError,
    FetchErrorCode,
    FetchException,
    FetchPhase,
    MediaError,
    MediaServiceError,
    MetadataError,
    MetadataServiceError,
    TranscriptError,
    TranscriptNotFound,
    TranscriptsDisabledError,
    TranscriptServiceError,
    VideoNotFoundError,
    _classify_exception,
)


class TestFetchErrorCode:
    """Test FetchErrorCode enum values and serialization."""

    def test_error_code_values(self):
        """Test all error code enum values are defined."""
        assert FetchErrorCode.VIDEO_NOT_FOUND == "video_not_found"
        assert FetchErrorCode.VIDEO_PRIVATE == "video_private"
        assert FetchErrorCode.VIDEO_DELETED == "video_deleted"
        assert FetchErrorCode.VIDEO_AGE_RESTRICTED == "video_age_restricted"
        assert FetchErrorCode.VIDEO_GEO_BLOCKED == "video_geo_blocked"
        assert FetchErrorCode.TRANSCRIPTS_DISABLED == "transcripts_disabled"
        assert FetchErrorCode.TRANSCRIPT_NOT_FOUND == "transcript_not_found"
        assert FetchErrorCode.RATE_LIMITED == "rate_limited"
        assert FetchErrorCode.SERVICE_ERROR == "service_error"
        assert FetchErrorCode.NETWORK_ERROR == "network_error"
        assert FetchErrorCode.TIMEOUT == "timeout"
        assert FetchErrorCode.INVALID_VIDEO_ID == "invalid_video_id"
        assert FetchErrorCode.MISSING_DEPENDENCY == "missing_dependency"
        assert FetchErrorCode.CONFIGURATION_ERROR == "configuration_error"
        assert FetchErrorCode.UNKNOWN == "unknown"

    def test_error_code_serialization(self):
        """Test error codes serialize to strings."""
        code = FetchErrorCode.VIDEO_NOT_FOUND
        assert str(code) == "video_not_found"
        assert code.value == "video_not_found"


class TestFetchPhase:
    """Test FetchPhase enum values."""

    def test_phase_values(self):
        """Test all phase enum values are defined."""
        assert FetchPhase.METADATA == "metadata"
        assert FetchPhase.TRANSCRIPT == "transcript"
        assert FetchPhase.MEDIA == "media"


class TestFetchError:
    """Test FetchError model creation and JSON round-trip."""

    def test_fetch_error_creation(self):
        """Test creating a FetchError instance."""
        error = FetchError(
            code=FetchErrorCode.VIDEO_NOT_FOUND,
            message="Video does not exist",
            phase=FetchPhase.METADATA,
            retryable=False,
            video_id="test123",
        )
        assert error.code == FetchErrorCode.VIDEO_NOT_FOUND
        assert error.message == "Video does not exist"
        assert error.phase == FetchPhase.METADATA
        assert error.retryable is False
        assert error.video_id == "test123"
        assert error.details is None

    def test_fetch_error_with_details(self):
        """Test FetchError with optional details."""
        error = FetchError(
            code=FetchErrorCode.RATE_LIMITED,
            message="Rate limit exceeded",
            phase=FetchPhase.TRANSCRIPT,
            retryable=True,
            video_id="test456",
            details={"http_status": 429, "retry_after": 30},
        )
        assert error.details == {"http_status": 429, "retry_after": 30}

    def test_fetch_error_json_round_trip(self):
        """Test FetchError serialization and deserialization."""
        error = FetchError(
            code=FetchErrorCode.TRANSCRIPT_NOT_FOUND,
            message="No transcript available",
            phase=FetchPhase.TRANSCRIPT,
            retryable=False,
            video_id="test789",
            details={"available_languages": ["es", "fr"]},
        )

        # Serialize to JSON
        json_data = error.model_dump()
        assert json_data["code"] == "transcript_not_found"
        assert json_data["message"] == "No transcript available"
        assert json_data["phase"] == "transcript"
        assert json_data["retryable"] is False
        assert json_data["video_id"] == "test789"
        assert json_data["details"] == {"available_languages": ["es", "fr"]}

        # Deserialize from JSON
        restored = FetchError(**json_data)
        assert restored.code == error.code
        assert restored.message == error.message
        assert restored.phase == error.phase
        assert restored.retryable == error.retryable
        assert restored.video_id == error.video_id
        assert restored.details == error.details


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_fetch_exception_base(self):
        """Test FetchException base class."""
        exc = FetchException("Test error", code=FetchErrorCode.UNKNOWN, retryable=False)
        assert str(exc) == "Test error"
        assert exc.code == FetchErrorCode.UNKNOWN
        assert exc.retryable is False

    def test_transcript_not_found_is_transcript_error(self):
        """Test TranscriptNotFound is a TranscriptError."""
        exc = TranscriptNotFound("No transcript")
        assert isinstance(exc, TranscriptError)
        assert isinstance(exc, FetchException)
        assert exc.code == FetchErrorCode.TRANSCRIPT_NOT_FOUND
        assert exc.retryable is False

    def test_transcripts_disabled_is_transcript_error(self):
        """Test TranscriptsDisabledError is a TranscriptError."""
        exc = TranscriptsDisabledError("Transcripts disabled")
        assert isinstance(exc, TranscriptError)
        assert isinstance(exc, FetchException)
        assert exc.code == FetchErrorCode.TRANSCRIPTS_DISABLED
        assert exc.retryable is False

    def test_transcript_service_error_is_transcript_error(self):
        """Test TranscriptServiceError is a TranscriptError."""
        exc = TranscriptServiceError("Service error")
        assert isinstance(exc, TranscriptError)
        assert isinstance(exc, FetchException)
        assert exc.code == FetchErrorCode.SERVICE_ERROR
        assert exc.retryable is True

    def test_video_not_found_is_metadata_error(self):
        """Test VideoNotFoundError is a MetadataError."""
        exc = VideoNotFoundError("Video not found")
        assert isinstance(exc, MetadataError)
        assert isinstance(exc, FetchException)
        assert exc.code == FetchErrorCode.VIDEO_NOT_FOUND
        assert exc.retryable is False

    def test_metadata_service_error_is_metadata_error(self):
        """Test MetadataServiceError is a MetadataError."""
        exc = MetadataServiceError("Service error")
        assert isinstance(exc, MetadataError)
        assert isinstance(exc, FetchException)
        assert exc.code == FetchErrorCode.SERVICE_ERROR
        assert exc.retryable is True

    def test_media_service_error_is_media_error(self):
        """Test MediaServiceError is a MediaError."""
        exc = MediaServiceError("Service error")
        assert isinstance(exc, MediaError)
        assert isinstance(exc, FetchException)
        assert exc.code == FetchErrorCode.SERVICE_ERROR
        assert exc.retryable is True


class TestExceptionDefaults:
    """Test each exception subclass carries correct default code and retryable."""

    def test_transcript_not_found_defaults(self):
        """Test TranscriptNotFound default code and retryable."""
        exc = TranscriptNotFound("Test message")
        assert exc.code == FetchErrorCode.TRANSCRIPT_NOT_FOUND
        assert exc.retryable is False

    def test_transcripts_disabled_defaults(self):
        """Test TranscriptsDisabledError default code and retryable."""
        exc = TranscriptsDisabledError("Test message")
        assert exc.code == FetchErrorCode.TRANSCRIPTS_DISABLED
        assert exc.retryable is False

    def test_transcript_service_error_defaults(self):
        """Test TranscriptServiceError default code and retryable."""
        exc = TranscriptServiceError("Test message")
        assert exc.code == FetchErrorCode.SERVICE_ERROR
        assert exc.retryable is True

    def test_transcript_service_error_custom_code(self):
        """Test TranscriptServiceError with custom code."""
        exc = TranscriptServiceError("Test message", code=FetchErrorCode.NETWORK_ERROR)
        assert exc.code == FetchErrorCode.NETWORK_ERROR
        assert exc.retryable is True

    def test_video_not_found_defaults(self):
        """Test VideoNotFoundError default code and retryable."""
        exc = VideoNotFoundError("Test message")
        assert exc.code == FetchErrorCode.VIDEO_NOT_FOUND
        assert exc.retryable is False

    def test_video_not_found_custom_code(self):
        """Test VideoNotFoundError with custom code."""
        exc = VideoNotFoundError("Test message", code=FetchErrorCode.VIDEO_PRIVATE)
        assert exc.code == FetchErrorCode.VIDEO_PRIVATE
        assert exc.retryable is False

    def test_metadata_service_error_defaults(self):
        """Test MetadataServiceError default code and retryable."""
        exc = MetadataServiceError("Test message")
        assert exc.code == FetchErrorCode.SERVICE_ERROR
        assert exc.retryable is True

    def test_media_service_error_defaults(self):
        """Test MediaServiceError default code and retryable."""
        exc = MediaServiceError("Test message")
        assert exc.code == FetchErrorCode.SERVICE_ERROR
        assert exc.retryable is True


class TestClassifyException:
    """Test _classify_exception helper function."""

    def test_classify_connection_error(self):
        """Test ConnectionError → NETWORK_ERROR."""
        exc = ConnectionError("Connection failed")
        assert _classify_exception(exc) == FetchErrorCode.NETWORK_ERROR

    def test_classify_timeout_error(self):
        """Test TimeoutError → TIMEOUT."""
        exc = TimeoutError("Request timed out")
        assert _classify_exception(exc) == FetchErrorCode.TIMEOUT

    def test_classify_os_error(self):
        """Test OSError → NETWORK_ERROR."""
        exc = OSError("Network unreachable")
        assert _classify_exception(exc) == FetchErrorCode.NETWORK_ERROR

    def test_classify_http_429(self):
        """Test HTTP 429 → RATE_LIMITED."""

        class MockHTTPError(Exception):
            status_code = 429

        exc = MockHTTPError("Too many requests")
        assert _classify_exception(exc) == FetchErrorCode.RATE_LIMITED

    def test_classify_http_500(self):
        """Test HTTP 500 → SERVICE_ERROR."""

        class MockHTTPError(Exception):
            status_code = 500

        exc = MockHTTPError("Internal server error")
        assert _classify_exception(exc) == FetchErrorCode.SERVICE_ERROR

    def test_classify_http_503(self):
        """Test HTTP 503 → SERVICE_ERROR."""

        class MockHTTPError(Exception):
            code = 503

        exc = MockHTTPError("Service unavailable")
        assert _classify_exception(exc) == FetchErrorCode.SERVICE_ERROR

    def test_classify_message_timeout(self):
        """Test message string 'timeout' → TIMEOUT."""
        exc = Exception("Request timeout occurred")
        assert _classify_exception(exc) == FetchErrorCode.TIMEOUT

    def test_classify_message_connection(self):
        """Test message string 'connection' → NETWORK_ERROR."""
        exc = Exception("Connection refused")
        assert _classify_exception(exc) == FetchErrorCode.NETWORK_ERROR

    def test_classify_message_dns(self):
        """Test message string 'dns' → NETWORK_ERROR."""
        exc = Exception("DNS resolution failed")
        assert _classify_exception(exc) == FetchErrorCode.NETWORK_ERROR

    def test_classify_message_private(self):
        """Test message string 'private' → VIDEO_PRIVATE."""
        exc = Exception("This video is private")
        assert _classify_exception(exc) == FetchErrorCode.VIDEO_PRIVATE

    def test_classify_message_not_found(self):
        """Test message string 'not found' → VIDEO_NOT_FOUND."""
        exc = Exception("Video not found")
        assert _classify_exception(exc) == FetchErrorCode.VIDEO_NOT_FOUND

    def test_classify_message_unavailable(self):
        """Test message string 'unavailable' → VIDEO_NOT_FOUND."""
        exc = Exception("Video unavailable")
        assert _classify_exception(exc) == FetchErrorCode.VIDEO_NOT_FOUND

    def test_classify_message_age_restricted(self):
        """Test message string 'age restricted' → VIDEO_AGE_RESTRICTED."""
        exc = Exception("This video is age restricted")
        assert _classify_exception(exc) == FetchErrorCode.VIDEO_AGE_RESTRICTED

    def test_classify_message_disabled(self):
        """Test message string 'disabled' → TRANSCRIPTS_DISABLED."""
        exc = Exception("Transcripts are disabled for this video")
        assert _classify_exception(exc) == FetchErrorCode.TRANSCRIPTS_DISABLED

    def test_classify_unknown_exception(self):
        """Test unknown exception → UNKNOWN."""
        exc = Exception("Some random error")
        assert _classify_exception(exc) == FetchErrorCode.UNKNOWN

    def test_classify_youtube_transcript_api_exceptions(self):
        """Test classification of youtube-transcript-api exceptions."""
        try:
            from youtube_transcript_api import (
                NoTranscriptAvailable,
                NoTranscriptFound,
                TranscriptsDisabled,
                VideoUnavailable,
            )

            # Test TranscriptsDisabled
            exc = TranscriptsDisabled("test_video_id")
            assert _classify_exception(exc) == FetchErrorCode.TRANSCRIPTS_DISABLED

            # Test NoTranscriptFound
            exc = NoTranscriptFound("test_video_id", ["en"], {"transcript_list": []})
            assert _classify_exception(exc) == FetchErrorCode.TRANSCRIPT_NOT_FOUND

            # Test NoTranscriptAvailable
            exc = NoTranscriptAvailable("test_video_id")
            assert _classify_exception(exc) == FetchErrorCode.TRANSCRIPT_NOT_FOUND

            # Test VideoUnavailable
            exc = VideoUnavailable("test_video_id")
            assert _classify_exception(exc) == FetchErrorCode.VIDEO_NOT_FOUND

        except ImportError:
            pytest.skip("youtube-transcript-api not installed")

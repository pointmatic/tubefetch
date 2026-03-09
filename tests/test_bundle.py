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

"""Tests for video bundle output."""

import json
from datetime import datetime, timezone

from tubefetch.core.models import FetchResult, Metadata, Transcript, TranscriptSegment, VideoBundle
from tubefetch.core.writer import write_bundle
from tubefetch.utils.hashing import hash_bundle


def _make_metadata() -> Metadata:
    """Create test metadata."""
    return Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        channel_title="Test Channel",
        channel_id="UC123",
        upload_date="2024-01-01",
        duration_seconds=120.0,
        description="Test description",
        tags=["test", "video"],
        view_count=1000,
        like_count=50,
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )


def _make_transcript() -> Transcript:
    """Create test transcript."""
    return Transcript(
        video_id="test123",
        language="en",
        is_generated=False,
        segments=[
            TranscriptSegment(start=0.0, duration=2.0, text="Hello world"),
            TranscriptSegment(start=2.0, duration=2.0, text="This is a test"),
        ],
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
        available_languages=["en"],
        token_count=10,
    )


def test_write_bundle_creates_file(tmp_path):
    """write_bundle creates video_bundle.json file."""
    metadata = _make_metadata()
    transcript = _make_transcript()

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)

    assert bundle_path.exists()
    assert bundle_path.name == "video_bundle.json"
    assert bundle_path.parent.name == "test123"


def test_bundle_contains_correct_fields(tmp_path):
    """Bundle contains video_id, metadata, transcript, errors."""
    metadata = _make_metadata()
    transcript = _make_transcript()

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert data["video_id"] == "test123"
    assert data["metadata"] is not None
    assert data["metadata"]["title"] == "Test Video"
    assert data["transcript"] is not None
    assert len(data["transcript"]["segments"]) == 2
    assert data["errors"] == []


def test_bundle_content_hash_matches_hash_bundle(tmp_path):
    """Bundle content_hash matches hash_bundle() output."""
    metadata = _make_metadata()
    transcript = _make_transcript()

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    expected_hash = hash_bundle(metadata, transcript)
    assert data["content_hash"] == expected_hash


def test_bundle_token_count_matches_transcript(tmp_path):
    """Bundle token_count matches transcript token_count."""
    metadata = _make_metadata()
    transcript = _make_transcript()
    transcript.token_count = 42

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert data["token_count"] == 42


def test_bundle_token_count_none_when_transcript_none(tmp_path):
    """Bundle token_count is None when transcript is None."""
    metadata = _make_metadata()

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=None,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert data["token_count"] is None


def test_bundle_token_count_none_when_transcript_token_count_none(tmp_path):
    """Bundle token_count is None when transcript.token_count is None."""
    metadata = _make_metadata()
    transcript = _make_transcript()
    transcript.token_count = None

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert data["token_count"] is None


def test_bundle_handles_missing_metadata(tmp_path):
    """Bundle handles case where metadata is None."""
    transcript = _make_transcript()

    result = FetchResult(
        video_id="test123",
        success=False,
        metadata=None,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert data["video_id"] == "test123"
    assert data["metadata"] is None
    assert data["transcript"] is not None


def test_bundle_handles_missing_transcript(tmp_path):
    """Bundle handles case where transcript is None."""
    metadata = _make_metadata()

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=None,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert data["video_id"] == "test123"
    assert data["metadata"] is not None
    assert data["transcript"] is None


def test_bundle_includes_errors(tmp_path):
    """Bundle includes errors from FetchResult."""
    from tubefetch.core.errors import FetchError, FetchErrorCode, FetchPhase

    metadata = _make_metadata()

    error = FetchError(
        code=FetchErrorCode.TRANSCRIPT_NOT_FOUND,
        message="No transcript available",
        phase=FetchPhase.TRANSCRIPT,
        retryable=False,
        video_id="test123",
    )

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=None,
        errors=[error],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert len(data["errors"]) == 1
    assert data["errors"][0]["code"] == "transcript_not_found"
    assert data["errors"][0]["message"] == "No transcript available"


def test_bundle_json_round_trip(tmp_path):
    """Bundle can be written and read back correctly."""
    metadata = _make_metadata()
    transcript = _make_transcript()

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)

    # Read back and parse as VideoBundle
    data = json.loads(bundle_path.read_text())
    bundle = VideoBundle(**data)

    assert bundle.video_id == "test123"
    assert bundle.metadata is not None
    assert bundle.metadata.title == "Test Video"
    assert bundle.transcript is not None
    assert len(bundle.transcript.segments) == 2
    assert bundle.content_hash is not None
    assert bundle.token_count == 10


def test_bundle_has_fetched_at_timestamp(tmp_path):
    """Bundle includes fetched_at timestamp."""
    metadata = _make_metadata()
    transcript = _make_transcript()

    result = FetchResult(
        video_id="test123",
        success=True,
        metadata=metadata,
        transcript=transcript,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)
    data = json.loads(bundle_path.read_text())

    assert "fetched_at" in data
    assert data["fetched_at"] is not None
    # Should be a valid ISO timestamp
    datetime.fromisoformat(data["fetched_at"].replace("Z", "+00:00"))


def test_bundle_creates_video_directory(tmp_path):
    """write_bundle creates video directory if it doesn't exist."""
    metadata = _make_metadata()

    result = FetchResult(
        video_id="new_video",
        success=True,
        metadata=metadata,
        transcript=None,
        errors=[],
    )

    bundle_path = write_bundle(result, tmp_path)

    assert bundle_path.parent.exists()
    assert bundle_path.parent.name == "new_video"

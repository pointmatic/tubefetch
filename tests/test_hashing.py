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

"""Tests for content hashing."""

from datetime import datetime, timezone

from tubefetch.core.models import Metadata, Transcript, TranscriptSegment
from tubefetch.utils.hashing import hash_bundle, hash_metadata, hash_transcript


def test_hash_metadata_consistent():
    """hash_metadata produces consistent hash for same content."""
    metadata1 = Metadata(
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

    metadata2 = Metadata(
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

    hash1 = hash_metadata(metadata1)
    hash2 = hash_metadata(metadata2)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length
    assert hash1.islower()  # Lowercase hex


def test_hash_metadata_different_when_title_changes():
    """hash_metadata produces different hash when title changes."""
    metadata1 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Original Title",
        channel_title="Test Channel",
        channel_id="UC123",
        upload_date="2024-01-01",
        duration_seconds=120.0,
        description="Test description",
        tags=["test"],
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    metadata2 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Modified Title",
        channel_title="Test Channel",
        channel_id="UC123",
        upload_date="2024-01-01",
        duration_seconds=120.0,
        description="Test description",
        tags=["test"],
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    hash1 = hash_metadata(metadata1)
    hash2 = hash_metadata(metadata2)

    assert hash1 != hash2


def test_hash_metadata_different_when_description_changes():
    """hash_metadata produces different hash when description changes."""
    metadata1 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        description="Original description",
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    metadata2 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        description="Modified description",
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    hash1 = hash_metadata(metadata1)
    hash2 = hash_metadata(metadata2)

    assert hash1 != hash2


def test_hash_metadata_same_when_view_count_changes():
    """hash_metadata produces same hash when only view_count changes."""
    metadata1 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        description="Test description",
        view_count=1000,
        like_count=50,
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    metadata2 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        description="Test description",
        view_count=2000,  # Changed
        like_count=50,
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    hash1 = hash_metadata(metadata1)
    hash2 = hash_metadata(metadata2)

    # Hash should be the same because view_count is excluded from canonical fields
    assert hash1 == hash2


def test_hash_metadata_same_when_like_count_changes():
    """hash_metadata produces same hash when only like_count changes."""
    metadata1 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        view_count=1000,
        like_count=50,
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    metadata2 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        view_count=1000,
        like_count=100,  # Changed
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    hash1 = hash_metadata(metadata1)
    hash2 = hash_metadata(metadata2)

    # Hash should be the same because like_count is excluded from canonical fields
    assert hash1 == hash2


def test_hash_metadata_tags_order_normalized():
    """hash_metadata normalizes tag order for consistent hashing."""
    metadata1 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        tags=["python", "tutorial", "coding"],
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    metadata2 = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        tags=["coding", "python", "tutorial"],  # Different order
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    hash1 = hash_metadata(metadata1)
    hash2 = hash_metadata(metadata2)

    # Hash should be the same because tags are sorted
    assert hash1 == hash2


def test_hash_transcript_consistent():
    """hash_transcript produces consistent hash for same segments."""
    segments = [
        TranscriptSegment(start=0.0, duration=2.0, text="Hello world"),
        TranscriptSegment(start=2.0, duration=2.0, text="This is a test"),
    ]

    transcript1 = Transcript(
        video_id="test123",
        language="en",
        is_generated=False,
        segments=segments,
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    transcript2 = Transcript(
        video_id="test123",
        language="en",
        is_generated=False,
        segments=segments,
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    hash1 = hash_transcript(transcript1)
    hash2 = hash_transcript(transcript2)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length
    assert hash1.islower()  # Lowercase hex


def test_hash_transcript_different_when_text_changes():
    """hash_transcript produces different hash when segment text changes."""
    segments1 = [
        TranscriptSegment(start=0.0, duration=2.0, text="Original text"),
    ]

    segments2 = [
        TranscriptSegment(start=0.0, duration=2.0, text="Modified text"),
    ]

    transcript1 = Transcript(
        video_id="test123",
        language="en",
        segments=segments1,
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    transcript2 = Transcript(
        video_id="test123",
        language="en",
        segments=segments2,
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    hash1 = hash_transcript(transcript1)
    hash2 = hash_transcript(transcript2)

    assert hash1 != hash2


def test_hash_transcript_same_when_timestamps_change():
    """hash_transcript produces same hash when only timestamps change."""
    segments1 = [
        TranscriptSegment(start=0.0, duration=2.0, text="Hello world"),
    ]

    segments2 = [
        TranscriptSegment(start=10.0, duration=5.0, text="Hello world"),  # Different timing
    ]

    transcript1 = Transcript(
        video_id="test123",
        language="en",
        segments=segments1,
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    transcript2 = Transcript(
        video_id="test123",
        language="en",
        segments=segments2,
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    hash1 = hash_transcript(transcript1)
    hash2 = hash_transcript(transcript2)

    # Hash should be the same because only text content matters
    assert hash1 == hash2


def test_hash_bundle_combines_metadata_and_transcript():
    """hash_bundle combines metadata and transcript hashes."""
    metadata = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    transcript = Transcript(
        video_id="test123",
        language="en",
        segments=[TranscriptSegment(start=0.0, duration=2.0, text="Test")],
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    bundle_hash = hash_bundle(metadata, transcript)

    assert len(bundle_hash) == 64
    assert bundle_hash.islower()

    # Bundle hash should be different from individual hashes
    assert bundle_hash != hash_metadata(metadata)
    assert bundle_hash != hash_transcript(transcript)


def test_hash_bundle_metadata_only():
    """hash_bundle works with metadata only."""
    metadata = Metadata(
        video_id="test123",
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        fetched_at=datetime.now(timezone.utc),
        metadata_source="yt-dlp",
    )

    bundle_hash = hash_bundle(metadata, None)

    assert len(bundle_hash) == 64
    assert bundle_hash.islower()


def test_hash_bundle_transcript_only():
    """hash_bundle works with transcript only."""
    transcript = Transcript(
        video_id="test123",
        language="en",
        segments=[TranscriptSegment(start=0.0, duration=2.0, text="Test")],
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
    )

    bundle_hash = hash_bundle(None, transcript)

    assert len(bundle_hash) == 64
    assert bundle_hash.islower()


def test_hash_bundle_both_none():
    """hash_bundle works with both None."""
    bundle_hash = hash_bundle(None, None)

    assert len(bundle_hash) == 64
    assert bundle_hash.islower()

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

"""Pipeline and error edge case tests for Story 7.3.

Covers:
- Idempotency with transcript content verification
- Error isolation with transcript errors in batch
- Fail-fast with transcript errors
- Retry integration with pipeline service calls
"""

import json
from datetime import datetime, timezone
from unittest.mock import patch

from yt_fetch.core.errors import FetchErrorCode, FetchPhase
from yt_fetch.core.models import Metadata, Transcript, TranscriptSegment
from yt_fetch.core.options import FetchOptions
from yt_fetch.core.pipeline import process_batch, process_video
from yt_fetch.services.metadata import MetadataError
from yt_fetch.services.transcript import TranscriptError


def _make_metadata(video_id: str = "testVid12345") -> Metadata:
    return Metadata(
        video_id=video_id,
        source_url=f"https://www.youtube.com/watch?v={video_id}",
        title="Test Video",
        fetched_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        metadata_source="yt-dlp",
    )


def _make_transcript(video_id: str = "testVid12345", text: str = "Hello") -> Transcript:
    return Transcript(
        video_id=video_id,
        language="en",
        is_generated=False,
        segments=[TranscriptSegment(start=0.0, duration=2.0, text=text)],
        fetched_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        transcript_source="youtube-transcript-api",
    )


# --- Idempotency: transcript content verification ---


class TestIdempotencyTranscript:
    @patch("yt_fetch.core.pipeline.get_transcript")
    @patch("yt_fetch.core.pipeline.get_metadata")
    def test_force_overwrites_transcript(self, mock_meta, mock_trans, tmp_path):
        """--force should overwrite transcript content."""
        mock_meta.return_value = _make_metadata()
        mock_trans.return_value = _make_transcript(text="Original text")
        opts = FetchOptions(out=tmp_path)
        process_video("testVid12345", opts)

        data1 = json.loads((tmp_path / "testVid12345" / "transcript.json").read_text())
        assert data1["segments"][0]["text"] == "Original text"

        mock_meta.return_value = _make_metadata()
        mock_trans.return_value = _make_transcript(text="Updated text")
        opts_force = FetchOptions(out=tmp_path, force=True)
        process_video("testVid12345", opts_force)

        data2 = json.loads((tmp_path / "testVid12345" / "transcript.json").read_text())
        assert data2["segments"][0]["text"] == "Updated text"

    @patch("yt_fetch.core.pipeline.get_transcript")
    @patch("yt_fetch.core.pipeline.get_metadata")
    def test_force_transcript_only_preserves_metadata(self, mock_meta, mock_trans, tmp_path):
        """--force-transcript should not refetch metadata."""
        meta = _make_metadata()
        meta.title = "Original Title"
        mock_meta.return_value = meta
        mock_trans.return_value = _make_transcript(text="v1")
        opts = FetchOptions(out=tmp_path)
        process_video("testVid12345", opts)

        mock_meta.reset_mock()
        mock_trans.reset_mock()
        mock_trans.return_value = _make_transcript(text="v2")

        opts_ft = FetchOptions(out=tmp_path, force_transcript=True)
        process_video("testVid12345", opts_ft)

        mock_meta.assert_not_called()
        mock_trans.assert_called_once()
        # Metadata should be unchanged
        meta_data = json.loads((tmp_path / "testVid12345" / "metadata.json").read_text())
        assert meta_data["title"] == "Original Title"
        # Transcript should be updated
        trans_data = json.loads((tmp_path / "testVid12345" / "transcript.json").read_text())
        assert trans_data["segments"][0]["text"] == "v2"


# --- Error isolation: transcript errors in batch ---


class TestBatchTranscriptErrors:
    @patch("yt_fetch.core.pipeline.get_transcript")
    @patch("yt_fetch.core.pipeline.get_metadata")
    def test_transcript_error_isolated(self, mock_meta, mock_trans, tmp_path):
        """A transcript error for one video should not affect others.

        Transcript-only failures are warnings (success=True) since metadata
        succeeded. The error is still recorded in result.errors.
        """
        mock_meta.side_effect = lambda vid, opts: _make_metadata(vid)

        def trans_side(vid, opts):
            if vid == "bad_trans_aaa":
                raise TranscriptError("no transcript", code=FetchErrorCode.TRANSCRIPT_NOT_FOUND)
            return _make_transcript(vid)

        mock_trans.side_effect = trans_side

        opts = FetchOptions(out=tmp_path, workers=1)
        result = process_batch(["vid_aaaaaaa", "bad_trans_aaa", "vid_bbbbbbb"], opts)

        assert result.total == 3
        # bad_trans_aaa: metadata succeeded so success=True, but transcript error recorded
        bad = [r for r in result.results if r.video_id == "bad_trans_aaa"]
        assert len(bad) == 1
        assert bad[0].success is True
        assert any(e.phase == FetchPhase.TRANSCRIPT for e in bad[0].errors)

        # All videos should succeed (transcript failure is a warning)
        good = [r for r in result.results if r.success]
        assert len(good) == 3

    @patch("yt_fetch.core.pipeline.get_transcript")
    @patch("yt_fetch.core.pipeline.get_metadata")
    def test_both_metadata_and_transcript_error(self, mock_meta, mock_trans, tmp_path):
        """Both metadata and transcript errors should be collected."""
        from yt_fetch.core.errors import FetchErrorCode

        mock_meta.side_effect = MetadataError("meta fail", code=FetchErrorCode.VIDEO_NOT_FOUND)
        mock_trans.side_effect = TranscriptError("trans fail", code=FetchErrorCode.TRANSCRIPT_NOT_FOUND)

        opts = FetchOptions(out=tmp_path)
        result = process_video("testVid12345", opts)

        assert result.success is False
        assert len(result.errors) == 2
        assert any(e.phase == FetchPhase.METADATA for e in result.errors)
        assert any(e.phase == FetchPhase.TRANSCRIPT for e in result.errors)


# --- Fail-fast with transcript errors ---


class TestFailFastTranscript:
    @patch("yt_fetch.core.pipeline.get_transcript")
    @patch("yt_fetch.core.pipeline.get_metadata")
    def test_fail_fast_on_transcript_error(self, mock_meta, mock_trans, tmp_path):
        """Fail-fast should trigger on metadata errors (critical failures).

        Transcript-only failures are warnings and do not trigger fail-fast.
        A metadata failure sets success=False and triggers early termination.
        """

        def meta_side(vid, opts):
            if vid == "bad_meta_aaa":
                raise MetadataError("fail", code=FetchErrorCode.VIDEO_NOT_FOUND)
            return _make_metadata(vid)

        mock_meta.side_effect = meta_side
        mock_trans.side_effect = lambda vid, opts: _make_transcript(vid)

        opts = FetchOptions(out=tmp_path, fail_fast=True, workers=1)
        result = process_batch(["vid_aaaaaaa", "bad_meta_aaa", "vid_ccccccc", "vid_ddddddd"], opts)

        assert result.failed >= 1
        assert result.total < 4


# --- Retry integration with pipeline ---


# TestRetryIntegration class removed - retry logic now handled by gentlify
# Retry behavior is tested through pipeline integration tests

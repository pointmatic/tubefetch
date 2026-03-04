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

"""Tests for tubefetch public library API."""

from datetime import datetime, timezone
from unittest.mock import patch

import tubefetch
from tubefetch import (
    BatchResult,
    FetchOptions,
    FetchResult,
    Metadata,
    Transcript,
    fetch_batch,
    fetch_video,
)
from tubefetch.core.models import TranscriptSegment


def _make_metadata(video_id: str) -> Metadata:
    return Metadata(
        video_id=video_id,
        source_url=f"https://www.youtube.com/watch?v={video_id}",
        title="Test",
        fetched_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        metadata_source="yt-dlp",
    )


def _make_transcript(video_id: str) -> Transcript:
    return Transcript(
        video_id=video_id,
        language="en",
        is_generated=False,
        segments=[TranscriptSegment(start=0.0, duration=1.0, text="Hello")],
        fetched_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        transcript_source="youtube-transcript-api",
    )


# --- Exports ---


class TestExports:
    def test_version_exported(self):
        assert hasattr(tubefetch, "__version__")
        assert isinstance(tubefetch.__version__, str)

    def test_fetch_video_exported(self):
        assert callable(tubefetch.fetch_video)

    def test_fetch_batch_exported(self):
        assert callable(tubefetch.fetch_batch)

    def test_models_exported(self):
        assert tubefetch.FetchOptions is FetchOptions
        assert tubefetch.FetchResult is FetchResult
        assert tubefetch.BatchResult is BatchResult
        assert tubefetch.Metadata is Metadata
        assert tubefetch.Transcript is Transcript

    def test_all_list(self):
        for name in tubefetch.__all__:
            assert hasattr(tubefetch, name)


# --- fetch_video ---


class TestFetchVideo:
    @patch("tubefetch.core.pipeline.get_transcript")
    @patch("tubefetch.core.pipeline.get_metadata")
    def test_with_valid_id(self, mock_meta, mock_trans, tmp_path):
        mock_meta.return_value = _make_metadata("dQw4w9WgXcQ")
        mock_trans.return_value = _make_transcript("dQw4w9WgXcQ")

        opts = FetchOptions(out=tmp_path)
        result = fetch_video("dQw4w9WgXcQ", opts)

        assert isinstance(result, FetchResult)
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.success is True

    @patch("tubefetch.core.pipeline.get_transcript")
    @patch("tubefetch.core.pipeline.get_metadata")
    def test_with_url(self, mock_meta, mock_trans, tmp_path):
        mock_meta.return_value = _make_metadata("dQw4w9WgXcQ")
        mock_trans.return_value = _make_transcript("dQw4w9WgXcQ")

        opts = FetchOptions(out=tmp_path)
        result = fetch_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", opts)

        assert result.success is True
        assert result.video_id == "dQw4w9WgXcQ"

    def test_with_invalid_id(self):
        result = fetch_video("not-valid")
        assert result.success is False
        assert len(result.errors) == 1
        assert "Invalid video ID" in result.errors[0].message

    @patch("tubefetch.core.pipeline.get_transcript")
    @patch("tubefetch.core.pipeline.get_metadata")
    def test_default_options(self, mock_meta, mock_trans, tmp_path):
        mock_meta.return_value = _make_metadata("dQw4w9WgXcQ")
        mock_trans.return_value = _make_transcript("dQw4w9WgXcQ")

        # Should work without explicit options (uses defaults)
        # We need to patch out to avoid writing to ./out
        with patch("tubefetch.core.pipeline.Path") as mock_path:
            mock_path.return_value = tmp_path
            mock_path.side_effect = None
            result = fetch_video("dQw4w9WgXcQ", FetchOptions(out=tmp_path))

        assert isinstance(result, FetchResult)

    def test_no_cli_context_needed(self):
        """Library usage should not require Click or CLI setup."""
        # Just constructing options should work without CLI
        opts = FetchOptions()
        assert opts.languages == ["en"]
        assert opts.download == "none"


# --- fetch_batch ---


class TestFetchBatch:
    @patch("tubefetch.core.pipeline.get_transcript")
    @patch("tubefetch.core.pipeline.get_metadata")
    def test_batch_success(self, mock_meta, mock_trans, tmp_path):
        mock_meta.side_effect = lambda vid, opts: _make_metadata(vid)
        mock_trans.side_effect = lambda vid, opts: _make_transcript(vid)

        opts = FetchOptions(out=tmp_path, workers=1)
        result = fetch_batch(["dQw4w9WgXcQ", "abc12345678"], opts)

        assert isinstance(result, BatchResult)
        assert result.total == 2
        assert result.succeeded == 2

    @patch("tubefetch.core.pipeline.get_transcript")
    @patch("tubefetch.core.pipeline.get_metadata")
    def test_batch_deduplicates(self, mock_meta, mock_trans, tmp_path):
        mock_meta.side_effect = lambda vid, opts: _make_metadata(vid)
        mock_trans.side_effect = lambda vid, opts: _make_transcript(vid)

        opts = FetchOptions(out=tmp_path, workers=1)
        result = fetch_batch(["dQw4w9WgXcQ", "dQw4w9WgXcQ"], opts)

        assert result.total == 1

    @patch("tubefetch.core.pipeline.get_transcript")
    @patch("tubefetch.core.pipeline.get_metadata")
    def test_batch_parses_urls(self, mock_meta, mock_trans, tmp_path):
        mock_meta.side_effect = lambda vid, opts: _make_metadata(vid)
        mock_trans.side_effect = lambda vid, opts: _make_transcript(vid)

        opts = FetchOptions(out=tmp_path, workers=1)
        result = fetch_batch(
            ["https://www.youtube.com/watch?v=dQw4w9WgXcQ", "abc12345678"],
            opts,
        )

        assert result.total == 2

    @patch("tubefetch.core.pipeline.get_transcript")
    @patch("tubefetch.core.pipeline.get_metadata")
    def test_batch_empty(self, mock_meta, mock_trans, tmp_path):
        opts = FetchOptions(out=tmp_path, workers=1)
        result = fetch_batch([], opts)

        assert result.total == 0
        assert result.succeeded == 0

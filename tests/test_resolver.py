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

"""Tests for playlist and channel resolution."""

import json
from unittest.mock import MagicMock, patch

import pytest

from tubefetch.core.errors import MetadataError
from tubefetch.services.resolver import (
    resolve_channel,
    resolve_input,
    resolve_playlist,
    write_resolved_ids,
)


def _mock_playlist_info(video_ids: list[str]) -> dict:
    """Create mock yt-dlp info dict for a playlist."""
    return {
        "entries": [{"id": vid, "url": f"https://www.youtube.com/watch?v={vid}"} for vid in video_ids],
        "title": "Test Playlist",
    }


def test_resolve_playlist_returns_video_ids(monkeypatch):
    """resolve_playlist returns ordered list of video IDs."""
    video_ids = ["vid1", "vid2", "vid3"]
    mock_info = _mock_playlist_info(video_ids)

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_playlist("https://www.youtube.com/playlist?list=PLtest", max_videos=None)

    assert result == video_ids


def test_resolve_playlist_respects_max_videos(monkeypatch):
    """resolve_playlist limits results to max_videos."""
    video_ids = ["vid1", "vid2", "vid3", "vid4", "vid5"]
    mock_info = _mock_playlist_info(video_ids)

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_playlist("https://www.youtube.com/playlist?list=PLtest", max_videos=3)

    # Should only return first 3
    assert len(result) == 3
    assert result == ["vid1", "vid2", "vid3"]


def test_resolve_playlist_handles_empty_playlist(monkeypatch):
    """resolve_playlist handles empty playlist."""
    mock_info = {"entries": [], "title": "Empty Playlist"}

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_playlist("https://www.youtube.com/playlist?list=PLtest", max_videos=None)

    assert result == []


def test_resolve_playlist_raises_on_error(monkeypatch):
    """resolve_playlist raises MetadataError on yt-dlp error."""
    import yt_dlp

    mock_ydl = MagicMock()
    mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Playlist not found")

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        with pytest.raises(MetadataError, match="Failed to resolve playlist URL"):
            resolve_playlist("https://www.youtube.com/playlist?list=PLtest", max_videos=None)


def test_resolve_channel_returns_video_ids(monkeypatch):
    """resolve_channel returns list of video IDs from channel."""
    video_ids = ["chan_vid1", "chan_vid2", "chan_vid3"]
    mock_info = _mock_playlist_info(video_ids)

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_channel("https://www.youtube.com/@testchannel", max_videos=None)

    assert result == video_ids


def test_resolve_channel_respects_max_videos(monkeypatch):
    """resolve_channel limits results to max_videos."""
    video_ids = ["chan_vid1", "chan_vid2", "chan_vid3", "chan_vid4"]
    mock_info = _mock_playlist_info(video_ids)

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_channel("https://www.youtube.com/@testchannel", max_videos=2)

    assert len(result) == 2
    assert result == ["chan_vid1", "chan_vid2"]


def test_resolve_input_detects_playlist_url(monkeypatch):
    """resolve_input auto-detects playlist URL."""
    video_ids = ["vid1", "vid2"]
    mock_info = _mock_playlist_info(video_ids)

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_input("https://www.youtube.com/playlist?list=PLtest", max_videos=None)

    assert result == video_ids


def test_resolve_input_detects_channel_url(monkeypatch):
    """resolve_input auto-detects channel URL."""
    video_ids = ["chan_vid1", "chan_vid2"]
    mock_info = _mock_playlist_info(video_ids)

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_input("https://www.youtube.com/@testchannel", max_videos=None)

    assert result == video_ids


def test_resolve_input_detects_video_id():
    """resolve_input treats single video ID/URL as single-item list."""
    result = resolve_input("dQw4w9WgXcQ", max_videos=None)
    assert result == ["dQw4w9WgXcQ"]


def test_resolve_input_detects_video_url():
    """resolve_input parses video URL and returns single-item list."""
    result = resolve_input("https://www.youtube.com/watch?v=dQw4w9WgXcQ", max_videos=None)
    assert result == ["dQw4w9WgXcQ"]


def test_resolve_input_raises_on_invalid_input():
    """resolve_input raises MetadataError for invalid input."""
    with pytest.raises(MetadataError, match="Invalid video ID or URL"):
        resolve_input("not-a-valid-id-or-url", max_videos=None)


def test_write_resolved_ids_creates_json_file(tmp_path):
    """write_resolved_ids creates JSON file with video IDs."""
    video_ids = ["vid1", "vid2", "vid3"]
    source_url = "https://www.youtube.com/playlist?list=PLtest"

    result_path = write_resolved_ids(video_ids, tmp_path, source_url)

    assert result_path.exists()
    assert result_path.name == "resolved_ids.json"

    data = json.loads(result_path.read_text())
    assert data["source_url"] == source_url
    assert data["video_ids"] == video_ids
    assert data["count"] == 3


def test_write_resolved_ids_creates_output_dir(tmp_path):
    """write_resolved_ids creates output directory if it doesn't exist."""
    out_dir = tmp_path / "nested" / "output"
    video_ids = ["vid1"]
    source_url = "https://www.youtube.com/playlist?list=PLtest"

    result_path = write_resolved_ids(video_ids, out_dir, source_url)

    assert out_dir.exists()
    assert result_path.exists()


def test_resolve_playlist_handles_none_entries(monkeypatch):
    """resolve_playlist skips None entries."""
    mock_info = {
        "entries": [
            {"id": "vid1"},
            None,  # Skip this
            {"id": "vid2"},
            None,  # Skip this
            {"id": "vid3"},
        ],
    }

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_playlist("https://www.youtube.com/playlist?list=PLtest", max_videos=None)

    assert result == ["vid1", "vid2", "vid3"]


def test_resolve_playlist_extracts_id_from_url_field(monkeypatch):
    """resolve_playlist extracts video ID from url field if id is missing."""
    mock_info = {
        "entries": [
            {"url": "https://www.youtube.com/watch?v=vid1"},
            {"url": "vid2"},  # Already just ID
        ],
    }

    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = mock_info

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = resolve_playlist("https://www.youtube.com/playlist?list=PLtest", max_videos=None)

    assert result == ["vid1", "vid2"]

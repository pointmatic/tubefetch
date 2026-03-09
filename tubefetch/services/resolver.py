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

"""Playlist and channel URL resolution to video IDs."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, cast

import yt_dlp

from tubefetch.core.errors import FetchErrorCode, MetadataError, _classify_exception

__all__ = ["resolve_playlist", "resolve_channel", "resolve_input"]

logger = logging.getLogger("tubefetch")


def resolve_playlist(url: str, max_videos: int | None = None) -> list[str]:
    """Resolve a playlist URL to an ordered list of video IDs.

    Args:
        url: YouTube playlist URL.
        max_videos: Maximum number of video IDs to return (None = all).

    Returns:
        List of video IDs in playlist order.

    Raises:
        MetadataError: If playlist resolution fails.
    """
    return _resolve_url(url, "playlist", max_videos)


def resolve_channel(url: str, max_videos: int | None = None) -> list[str]:
    """Resolve a channel URL to a list of video IDs (uploads).

    Args:
        url: YouTube channel URL (e.g., /@handle, /channel/..., /c/...).
        max_videos: Maximum number of video IDs to return (None = all).

    Returns:
        List of video IDs from channel uploads.

    Raises:
        MetadataError: If channel resolution fails.
    """
    return _resolve_url(url, "channel", max_videos)


def resolve_input(input_str: str, max_videos: int | None = None) -> list[str]:
    """Auto-detect input type and resolve to video IDs.

    Detects whether input is a video ID/URL, playlist URL, or channel URL,
    and returns the appropriate list of video IDs.

    Args:
        input_str: Video ID, video URL, playlist URL, or channel URL.
        max_videos: Maximum number of video IDs to return (None = all).

    Returns:
        List of video IDs (single item for video, multiple for playlist/channel).

    Raises:
        MetadataError: If resolution fails.
    """
    # Try to detect the input type
    lower = input_str.lower()

    # Check if it's a playlist URL
    if "list=" in lower or "/playlist" in lower:
        return resolve_playlist(input_str, max_videos)

    # Check if it's a channel URL
    if any(pattern in lower for pattern in ["/@", "/channel/", "/c/", "/user/"]):
        return resolve_channel(input_str, max_videos)

    # Otherwise, treat as a single video ID/URL
    from tubefetch.services.id_parser import parse_video_id

    video_id = parse_video_id(input_str)
    if video_id is None:
        raise MetadataError(f"Invalid video ID or URL: {input_str}", code=FetchErrorCode.INVALID_VIDEO_ID)

    return [video_id]


def _resolve_url(url: str, url_type: str, max_videos: int | None = None) -> list[str]:
    """Internal helper to resolve playlist or channel URLs to video IDs.

    Args:
        url: YouTube URL to resolve.
        url_type: Type of URL ("playlist" or "channel") for logging.
        max_videos: Maximum number of video IDs to return.

    Returns:
        List of video IDs.

    Raises:
        MetadataError: If resolution fails.
    """
    ydl_opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,  # Only extract IDs, don't download metadata
        "skip_download": True,
        "no_color": True,
    }

    if max_videos is not None:
        ydl_opts["playlistend"] = max_videos

    try:
        with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as exc:
        code = _classify_exception(exc)
        raise MetadataError(f"Failed to resolve {url_type} URL {url}: {exc}", code=code) from exc
    except Exception as exc:
        code = _classify_exception(exc)
        raise MetadataError(f"Failed to resolve {url_type} URL {url}: {exc}", code=code) from exc

    if info is None:
        raise MetadataError(f"No data returned for {url_type} URL: {url}")

    # Extract video IDs from entries
    entries = info.get("entries", [])
    video_ids = []

    for entry in entries:
        if entry is None:
            continue

        # Extract video ID from entry
        video_id = entry.get("id") or entry.get("url")
        if video_id:
            # Clean up video ID (remove URL prefix if present)
            if "/" in video_id:
                video_id = video_id.split("/")[-1]
            if "=" in video_id:
                video_id = video_id.split("=")[-1]

            video_ids.append(video_id)

        # Stop if we've reached max_videos
        if max_videos is not None and len(video_ids) >= max_videos:
            break

    logger.info("Resolved %s URL to %d video IDs", url_type, len(video_ids))
    return video_ids


def write_resolved_ids(video_ids: list[str], out_dir: Path, source_url: str) -> Path:
    """Write resolved video IDs to JSON file for reproducibility.

    Args:
        video_ids: List of resolved video IDs.
        out_dir: Output directory.
        source_url: Source URL that was resolved.

    Returns:
        Path to written resolved_ids.json file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "resolved_ids.json"

    data = {
        "source_url": source_url,
        "video_ids": video_ids,
        "count": len(video_ids),
    }

    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("Wrote %d resolved IDs to %s", len(video_ids), dest)
    return dest

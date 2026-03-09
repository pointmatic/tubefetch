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

"""Transcript fetching via youtube-transcript-api."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from youtube_transcript_api import TranscriptsDisabled, YouTubeTranscriptApi

from tubefetch.core.errors import (
    FetchErrorCode,
    TranscriptError,
    TranscriptNotFound,
    TranscriptsDisabledError,
    TranscriptServiceError,
    _classify_exception,
)
from tubefetch.core.models import Transcript, TranscriptSegment
from tubefetch.core.options import FetchOptions
from tubefetch.utils.hashing import hash_transcript

__all__ = ["get_transcript", "list_available_transcripts", "TranscriptError"]

logger = logging.getLogger("tubefetch")

# Retryable error codes for transient failures
RETRYABLE_CODES = (
    FetchErrorCode.NETWORK_ERROR,
    FetchErrorCode.TIMEOUT,
    FetchErrorCode.SERVICE_ERROR,
    FetchErrorCode.RATE_LIMITED,
)


def get_transcript(video_id: str, options: FetchOptions) -> Transcript:
    """Fetch a transcript for a video using the configured language preferences.

    Language selection algorithm:
    1. Try preferred languages in order.
    2. Prefer manual over generated (when allow_generated is False).
    3. Fall back to any available language (when allow_any_language is True).
    4. Raise TranscriptNotFound when nothing is available.
    """
    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)
    except TranscriptsDisabled as exc:
        raise TranscriptsDisabledError(f"Transcripts are disabled for {video_id}") from exc
    except Exception as exc:
        code = _classify_exception(exc)
        if code in RETRYABLE_CODES:
            raise TranscriptServiceError(f"Failed to list transcripts for {video_id}: {exc}", code=code) from exc
        raise TranscriptError(f"Failed to list transcripts for {video_id}: {exc}", code=code) from exc

    available = list(transcript_list)
    available_languages = [t.language_code for t in available]

    selected = _select_transcript(
        available,
        languages=options.languages,
        allow_generated=options.allow_generated,
        allow_any_language=options.allow_any_language,
    )

    if selected is None:
        raise TranscriptNotFound(
            f"TRANSCRIPT_NOT_FOUND: No transcript for {video_id} "
            f"in languages {options.languages}. "
            f"Available: {available_languages}"
        )

    try:
        fetched = selected.fetch()
    except Exception as exc:
        code = _classify_exception(exc)
        if code in RETRYABLE_CODES:
            raise TranscriptServiceError(f"Failed to fetch transcript for {video_id}: {exc}", code=code) from exc
        raise TranscriptError(f"Failed to fetch transcript for {video_id}: {exc}", code=code) from exc

    segments = [
        TranscriptSegment(
            start=snippet.start,
            duration=snippet.duration,
            text=snippet.text,
        )
        for snippet in fetched
    ]

    transcript = Transcript(
        video_id=video_id,
        language=fetched.language_code,
        is_generated=fetched.is_generated,
        segments=segments,
        fetched_at=datetime.now(timezone.utc),
        transcript_source="youtube-transcript-api",
        available_languages=available_languages,
    )

    # Compute content hash
    transcript.content_hash = hash_transcript(transcript)
    return transcript


def list_available_transcripts(video_id: str) -> list[dict[str, Any]]:
    """List available transcripts for a video.

    Returns a list of dicts with keys: language_code, language, is_generated.
    """
    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)
    except TranscriptsDisabled as exc:
        raise TranscriptsDisabledError(f"Transcripts are disabled for {video_id}") from exc
    except Exception as exc:
        code = _classify_exception(exc)
        if code in RETRYABLE_CODES:
            raise TranscriptServiceError(f"Failed to list transcripts for {video_id}: {exc}", code=code) from exc
        raise TranscriptError(f"Failed to list transcripts for {video_id}: {exc}", code=code) from exc

    return [
        {
            "language_code": t.language_code,
            "language": t.language,
            "is_generated": t.is_generated,
        }
        for t in transcript_list
    ]


def _select_transcript(
    available: list[Any],
    *,
    languages: list[str],
    allow_generated: bool,
    allow_any_language: bool,
) -> Any | None:
    """Select the best transcript from available options.

    Priority:
    1. Manual transcript in a preferred language (in order).
    2. Generated transcript in a preferred language (if allow_generated).
    3. Any manual transcript (if allow_any_language).
    4. Any generated transcript (if allow_any_language and allow_generated).
    5. None.
    """
    by_lang: dict[str, list[Any]] = {}
    for t in available:
        by_lang.setdefault(t.language_code, []).append(t)

    for lang in languages:
        candidates = by_lang.get(lang, [])
        manual = [t for t in candidates if not t.is_generated]
        generated = [t for t in candidates if t.is_generated]

        if manual:
            return manual[0]
        if allow_generated and generated:
            return generated[0]

    if allow_any_language:
        all_manual = [t for t in available if not t.is_generated]
        all_generated = [t for t in available if t.is_generated]

        if all_manual:
            return all_manual[0]
        if allow_generated and all_generated:
            return all_generated[0]

    return None

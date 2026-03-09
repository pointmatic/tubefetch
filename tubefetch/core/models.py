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

"""Pydantic data models for yt-fetch."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from tubefetch.core.errors import FetchError


class Metadata(BaseModel):
    video_id: str
    source_url: str
    title: str | None = None
    channel_title: str | None = None
    channel_id: str | None = None
    upload_date: str | None = None
    duration_seconds: float | None = None
    description: str | None = None
    tags: list[str] = []
    view_count: int | None = None
    like_count: int | None = None
    fetched_at: datetime
    metadata_source: str
    content_hash: str | None = None
    raw: dict[str, Any] | None = None


class TranscriptSegment(BaseModel):
    start: float
    duration: float
    text: str


class Transcript(BaseModel):
    video_id: str
    language: str
    is_generated: bool | None = None
    segments: list[TranscriptSegment]
    fetched_at: datetime
    transcript_source: str
    available_languages: list[str] = []
    content_hash: str | None = None
    errors: list[str] = []


class FetchResult(BaseModel):
    video_id: str
    success: bool
    metadata_path: Path | None = None
    transcript_path: Path | None = None
    media_paths: list[Path] = []
    metadata: Metadata | None = None
    transcript: Transcript | None = None
    errors: list[FetchError] = []


class BatchResult(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: list[FetchResult]

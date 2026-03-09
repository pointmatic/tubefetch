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

"""SHA-256 content hashing for change detection."""

from __future__ import annotations

import hashlib
import json

from tubefetch.core.models import Metadata, Transcript


def hash_metadata(metadata: Metadata) -> str:
    """Compute SHA-256 hash of canonical metadata fields.

    Canonical fields are those that represent the actual content, excluding
    volatile fields like view_count, like_count, fetched_at, and raw.

    Args:
        metadata: Metadata model.

    Returns:
        Hex-encoded lowercase SHA-256 hash string.
    """
    # Canonical fields: stable content that represents the video
    canonical = {
        "video_id": metadata.video_id,
        "title": metadata.title,
        "description": metadata.description,
        "tags": sorted(metadata.tags) if metadata.tags else [],
        "upload_date": metadata.upload_date,
        "duration_seconds": metadata.duration_seconds,
        "channel_id": metadata.channel_id,
        "channel_title": metadata.channel_title,
    }

    # Serialize to JSON with sorted keys for deterministic output
    canonical_json = json.dumps(canonical, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def hash_transcript(transcript: Transcript) -> str:
    """Compute SHA-256 hash of concatenated transcript segment text.

    Args:
        transcript: Transcript model with segments.

    Returns:
        Hex-encoded lowercase SHA-256 hash string.
    """
    # Concatenate all segment text
    text = " ".join(seg.text for seg in transcript.segments)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_bundle(metadata: Metadata | None, transcript: Transcript | None) -> str:
    """Compute SHA-256 hash of combined metadata and transcript content.

    Args:
        metadata: Metadata model (or None).
        transcript: Transcript model (or None).

    Returns:
        Hex-encoded lowercase SHA-256 hash string.
    """
    # Combine hashes of metadata and transcript
    parts = []
    if metadata is not None:
        parts.append(hash_metadata(metadata))
    if transcript is not None:
        parts.append(hash_transcript(transcript))

    # Hash the combined hashes
    combined = "|".join(parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

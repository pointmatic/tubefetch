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

"""LLM-ready transcript text formatting with intelligent paragraph chunking."""

from __future__ import annotations

from tubefetch.core.models import TranscriptSegment


def format_transcript_txt(
    segments: list[TranscriptSegment],
    is_generated: bool | None = None,
    gap_threshold: float = 2.0,
    timestamps: bool = False,
    raw: bool = False,
) -> str:
    """Format transcript segments into LLM-ready plain text.

    Args:
        segments: List of transcript segments with start, duration, and text.
        is_generated: Whether the transcript is auto-generated. If True, prepends a notice.
        gap_threshold: Silence gap (seconds) threshold for paragraph breaks. Default 2.0.
        timestamps: If True, prepend [MM:SS] markers at paragraph boundaries.
        raw: If True, bare concatenation with spaces (no paragraph formatting).

    Returns:
        Formatted transcript text.

    Modes:
        - Default: Paragraph chunking with gap_threshold
        - Timestamped: Paragraph chunking with [MM:SS] markers
        - Raw: Bare concatenation (backward-compatible)

    Note:
        raw=True overrides timestamps.
    """
    if not segments:
        return ""

    # Auto-generated notice (prepended to all modes)
    notice = ""
    if is_generated:
        notice = "[Auto-generated transcript]\n\n"

    # Raw mode: bare concatenation with spaces
    if raw:
        text = " ".join(seg.text for seg in segments)
        return notice + text

    # Default or timestamped mode: paragraph chunking
    paragraphs: list[str] = []
    current_paragraph: list[str] = []
    current_paragraph_start: float | None = None
    prev_end: float | None = None

    for seg in segments:
        seg_start = seg.start
        seg_text = seg.text

        # Determine if we should start a new paragraph
        if prev_end is not None:
            gap = seg_start - prev_end
            if gap > gap_threshold:
                # Flush current paragraph
                if current_paragraph:
                    para_text = " ".join(current_paragraph)
                    if timestamps and paragraphs:
                        # Add timestamp marker for new paragraph (not the first one)
                        # Use the start time of the first segment in this paragraph
                        minutes = int(current_paragraph_start // 60)
                        seconds = int(current_paragraph_start % 60)
                        para_text = f"[{minutes:02d}:{seconds:02d}] {para_text}"
                    paragraphs.append(para_text)
                    current_paragraph = []
                    current_paragraph_start = None

        # Track the start of the current paragraph
        if current_paragraph_start is None:
            current_paragraph_start = seg_start

        current_paragraph.append(seg_text)
        prev_end = seg_start + seg.duration

    # Flush final paragraph
    if current_paragraph:
        para_text = " ".join(current_paragraph)
        if timestamps and paragraphs:
            # Add timestamp for final paragraph if not the first
            minutes = int(current_paragraph_start // 60)
            seconds = int(current_paragraph_start % 60)
            para_text = f"[{minutes:02d}:{seconds:02d}] {para_text}"
        paragraphs.append(para_text)

    # Join paragraphs with double newlines
    text = "\n\n".join(paragraphs)
    return notice + text

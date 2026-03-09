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

"""Tests for LLM-ready transcript text formatting."""

from tubefetch.core.models import TranscriptSegment
from tubefetch.utils.txt_formatter import format_transcript_txt


def test_empty_segments():
    """Empty segment list returns empty string."""
    result = format_transcript_txt([])
    assert result == ""


def test_raw_mode_bare_concatenation():
    """Raw mode produces bare concatenation with spaces."""
    segments = [
        TranscriptSegment(start=0.0, duration=2.0, text="Hello"),
        TranscriptSegment(start=2.0, duration=2.0, text="world"),
        TranscriptSegment(start=4.0, duration=2.0, text="test"),
    ]
    result = format_transcript_txt(segments, raw=True)
    assert result == "Hello world test"


def test_raw_mode_ignores_timestamps():
    """Raw mode ignores timestamps flag."""
    segments = [
        TranscriptSegment(start=0.0, duration=2.0, text="Hello"),
        TranscriptSegment(start=2.0, duration=2.0, text="world"),
    ]
    result = format_transcript_txt(segments, raw=True, timestamps=True)
    assert result == "Hello world"
    assert "[00:00]" not in result


def test_default_mode_small_gaps_same_paragraph():
    """Segments with gaps < threshold stay in same paragraph."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.5, text="First"),
        TranscriptSegment(start=1.5, duration=1.5, text="second"),  # gap = 0.0
        TranscriptSegment(start=3.5, duration=1.5, text="third"),   # gap = 0.5
    ]
    result = format_transcript_txt(segments, gap_threshold=2.0)
    assert result == "First second third"
    assert "\n\n" not in result


def test_default_mode_large_gaps_new_paragraph():
    """Segments with gaps > threshold create paragraph breaks."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="First paragraph."),
        TranscriptSegment(start=4.0, duration=1.0, text="Second paragraph."),  # gap = 3.0 > 2.0
        TranscriptSegment(start=8.0, duration=1.0, text="Third paragraph."),   # gap = 3.0 > 2.0
    ]
    result = format_transcript_txt(segments, gap_threshold=2.0)
    assert result == "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."


def test_custom_gap_threshold():
    """Custom gap threshold affects paragraph breaks."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="First"),
        TranscriptSegment(start=2.5, duration=1.0, text="Second"),  # gap = 1.5
    ]
    
    # With threshold 2.0, gap 1.5 < 2.0 -> same paragraph
    result = format_transcript_txt(segments, gap_threshold=2.0)
    assert result == "First Second"
    
    # With threshold 1.0, gap 1.5 > 1.0 -> new paragraph
    result = format_transcript_txt(segments, gap_threshold=1.0)
    assert result == "First\n\nSecond"


def test_timestamped_mode_adds_markers():
    """Timestamped mode adds [MM:SS] markers at paragraph boundaries."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="First paragraph."),
        TranscriptSegment(start=65.0, duration=1.0, text="Second paragraph."),  # 1:05, gap > 2.0
        TranscriptSegment(start=130.0, duration=1.0, text="Third paragraph."),  # 2:10, gap > 2.0
    ]
    result = format_transcript_txt(segments, gap_threshold=2.0, timestamps=True)
    
    # First paragraph has no timestamp
    assert result.startswith("First paragraph.")
    # Second paragraph has [01:05] marker
    assert "[01:05] Second paragraph." in result
    # Third paragraph has [02:10] marker
    assert "[02:10] Third paragraph." in result


def test_timestamped_mode_no_marker_for_first_paragraph():
    """First paragraph doesn't get a timestamp marker."""
    segments = [
        TranscriptSegment(start=10.0, duration=1.0, text="Only paragraph."),
    ]
    result = format_transcript_txt(segments, timestamps=True)
    assert result == "Only paragraph."
    assert "[00:10]" not in result


def test_auto_generated_notice_true():
    """Auto-generated notice is prepended when is_generated=True."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="Test"),
    ]
    result = format_transcript_txt(segments, is_generated=True)
    assert result.startswith("[Auto-generated transcript]\n\n")
    assert "Test" in result


def test_auto_generated_notice_false():
    """No notice when is_generated=False."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="Test"),
    ]
    result = format_transcript_txt(segments, is_generated=False)
    assert not result.startswith("[Auto-generated transcript]")
    assert result == "Test"


def test_auto_generated_notice_none():
    """No notice when is_generated=None."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="Test"),
    ]
    result = format_transcript_txt(segments, is_generated=None)
    assert not result.startswith("[Auto-generated transcript]")
    assert result == "Test"


def test_auto_generated_notice_with_raw_mode():
    """Auto-generated notice works with raw mode."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="Hello"),
        TranscriptSegment(start=1.0, duration=1.0, text="world"),
    ]
    result = format_transcript_txt(segments, is_generated=True, raw=True)
    assert result == "[Auto-generated transcript]\n\nHello world"


def test_auto_generated_notice_with_timestamped_mode():
    """Auto-generated notice works with timestamped mode."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="First"),
        TranscriptSegment(start=5.0, duration=1.0, text="Second"),  # gap > 2.0
    ]
    result = format_transcript_txt(segments, is_generated=True, timestamps=True)
    assert result.startswith("[Auto-generated transcript]\n\n")
    assert "First" in result
    assert "[00:05] Second" in result


def test_complex_paragraph_chunking():
    """Complex scenario with multiple paragraphs and varying gaps."""
    segments = [
        # Paragraph 1
        TranscriptSegment(start=0.0, duration=2.0, text="Welcome to this video."),
        TranscriptSegment(start=2.5, duration=2.0, text="Today we'll discuss AI."),  # gap 0.5
        
        # Paragraph 2 (gap 3.0 > 2.0)
        TranscriptSegment(start=7.5, duration=2.0, text="First, let's define terms."),
        TranscriptSegment(start=10.0, duration=2.0, text="AI stands for artificial intelligence."),  # gap 0.5
        
        # Paragraph 3 (gap 5.0 > 2.0)
        TranscriptSegment(start=17.0, duration=2.0, text="Thanks for watching."),
    ]
    
    result = format_transcript_txt(segments, gap_threshold=2.0)
    
    paragraphs = result.split("\n\n")
    assert len(paragraphs) == 3
    assert paragraphs[0] == "Welcome to this video. Today we'll discuss AI."
    assert paragraphs[1] == "First, let's define terms. AI stands for artificial intelligence."
    assert paragraphs[2] == "Thanks for watching."


def test_timestamp_formatting():
    """Verify timestamp formatting is correct."""
    segments = [
        TranscriptSegment(start=0.0, duration=1.0, text="Zero seconds"),
        TranscriptSegment(start=65.0, duration=1.0, text="One minute five"),     # 1:05
        TranscriptSegment(start=3661.0, duration=1.0, text="One hour one min"),  # 61:01
    ]
    
    result = format_transcript_txt(segments, timestamps=True, gap_threshold=1.0)
    
    # First has no timestamp
    assert result.startswith("Zero seconds")
    # Second has [01:05]
    assert "[01:05] One minute five" in result
    # Third has [61:01] (minutes can exceed 59)
    assert "[61:01] One hour one min" in result

# LLM-Ready Text Formatting

TubeFetch produces optimized plain text transcripts designed for LLM consumption with intelligent paragraph chunking, optional timestamps, and configurable formatting.

## Overview

The `transcript.txt` output is specifically formatted for AI/LLM pipelines:

- **Intelligent paragraph chunking** based on silence gaps
- **Optional timestamp markers** for temporal context
- **Configurable gap threshold** for different content types
- **Auto-generated notice** for machine-generated transcripts

## Formatting Modes

### Default Mode: Paragraph Chunking

```bash
tubefetch VIDEO_ID
```

Automatically groups transcript segments into paragraphs based on silence gaps (default: 2.0 seconds).

**Example output:**
```
Hello and welcome to this tutorial. Today we're going to learn about Python programming. Let's get started with the basics.

Python is a high-level programming language. It's known for its simplicity and readability. Many beginners start with Python.

Now let's write our first program. Open your text editor and type the following code.
```

### Timestamped Mode

```bash
tubefetch VIDEO_ID --txt-timestamps
```

Adds `[MM:SS]` markers at paragraph boundaries for temporal context.

**Example output:**
```
Hello and welcome to this tutorial. Today we're going to learn about Python programming. Let's get started with the basics.

[00:15] Python is a high-level programming language. It's known for its simplicity and readability. Many beginners start with Python.

[00:32] Now let's write our first program. Open your text editor and type the following code.
```

### Raw Mode

```bash
tubefetch VIDEO_ID --txt-raw
```

Bare concatenation with spaces, no paragraph formatting.

**Example output:**
```
Hello and welcome to this tutorial. Today we're going to learn about Python programming. Let's get started with the basics. Python is a high-level programming language. It's known for its simplicity and readability. Many beginners start with Python. Now let's write our first program. Open your text editor and type the following code.
```

## Gap Threshold Configuration

Control paragraph breaks with `--txt-gap-threshold`:

```bash
# Tighter paragraphs (more breaks)
tubefetch VIDEO_ID --txt-gap-threshold 1.0

# Looser paragraphs (fewer breaks)
tubefetch VIDEO_ID --txt-gap-threshold 5.0

# Default
tubefetch VIDEO_ID --txt-gap-threshold 2.0
```

### Recommended Thresholds by Content Type

| Content Type | Threshold | Reasoning |
|--------------|-----------|-----------|
| Lectures/Tutorials | 2.0-3.0s | Natural topic transitions |
| Podcasts/Interviews | 3.0-4.0s | Conversational pauses |
| News/Presentations | 1.5-2.5s | Structured content |
| Casual vlogs | 2.5-3.5s | Informal speech patterns |

## Auto-Generated Notice

For machine-generated transcripts, tubefetch prepends a notice:

```
[Auto-generated transcript]

Hello and welcome to this tutorial...
```

This helps downstream systems understand transcript quality.

## Library Usage

```python
from tubefetch import fetch_video, FetchOptions

# Timestamped with custom gap threshold
opts = FetchOptions(
    txt_timestamps=True,
    txt_gap_threshold=3.0
)
result = fetch_video("dQw4w9WgXcQ", opts)

# Raw mode
opts = FetchOptions(txt_raw=True)
result = fetch_video("dQw4w9WgXcQ", opts)
```

## Best Practices

### For RAG Systems

```bash
# Balanced chunking with timestamps for citation
tubefetch VIDEO_ID --txt-timestamps --txt-gap-threshold 2.5
```

- Timestamps enable source attribution
- Moderate gap threshold creates semantic chunks
- Paragraph breaks help with vector embeddings

### For Summarization

```bash
# Looser paragraphs for context
tubefetch VIDEO_ID --txt-gap-threshold 4.0
```

- Larger chunks preserve context
- Fewer breaks reduce fragmentation
- Better for extractive summarization

### For Training Data

```bash
# Raw mode for maximum tokens
tubefetch VIDEO_ID --txt-raw
```

- No formatting overhead
- Maximum token density
- Suitable for language model training

## Technical Details

### Paragraph Chunking Algorithm

1. Iterate through transcript segments
2. Calculate gap between consecutive segments: `gap = next_start - (current_start + current_duration)`
3. If `gap > gap_threshold`, start new paragraph
4. Join segments within paragraph with spaces
5. Join paragraphs with double newlines

### Timestamp Calculation

Timestamps use the `start` time of the first segment in each paragraph:

```python
minutes = int(start_time // 60)
seconds = int(start_time % 60)
marker = f"[{minutes:02d}:{seconds:02d}]"
```

## Output Location

Formatted text is written to:

```
out/<video_id>/transcript.txt
```

## Related Features

- **[Token Counting](token-counting.md)** — Estimate LLM costs for formatted text
- **[Video Bundles](video-bundles.md)** — Include formatted text in unified output
- **[Content Hashing](content-hashing.md)** — Detect changes in transcript content

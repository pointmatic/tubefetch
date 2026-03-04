# Usage

Comprehensive guide to using TubeFetch from the command line.

## Overview

TubeFetch uses a **default command pattern** for the most common use case (fetching metadata + transcripts), with specialized commands for exceptional cases:

| Command | Purpose | Output |
|---------|---------|--------|
| *(default)* | Fetch everything | Metadata + Transcript + Optional Media |
| `metadata` | Metadata only | Video info (title, channel, duration, etc.) |
| `transcript` | Transcript only | Captions/subtitles text |
| `media` | Media only | Video/audio files |

## Command Syntax

The default command accepts video IDs or URLs as **positional arguments**:

```bash
tubefetch <video-id-or-url> [<video-id-or-url>...] [OPTIONS]
```

For specialized use cases, use explicit commands:

```bash
tubefetch <command> <video-id-or-url> [<video-id-or-url>...] [OPTIONS]
```

**Supported input formats:**
- Video IDs: `dQw4w9WgXcQ`
- Full URLs: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short URLs: `https://youtu.be/dQw4w9WgXcQ`

---

## Default Command

Fetch metadata, transcripts, and optionally media for YouTube videos (no command name needed).

### Basic Usage

```bash
# Single video
tubefetch dQw4w9WgXcQ

# Multiple videos
tubefetch dQw4w9WgXcQ abc123def https://youtu.be/xyz789

# Batch from file
tubefetch --file video_ids.txt
```

### With Media Download

```bash
# Download video (merged video+audio MP4)
tubefetch dQw4w9WgXcQ --download video

# Download audio only (M4A extraction)
tubefetch dQw4w9WgXcQ --download audio

# Download both (separate files)
tubefetch dQw4w9WgXcQ --download both

# Limit video quality
tubefetch dQw4w9WgXcQ --download video --max-height 720
```

### Output Structure

```
output/
└── dQw4w9WgXcQ/
    ├── metadata.json
    ├── transcript.json
    ├── transcript.txt
    ├── transcript.vtt
    ├── transcript.srt
    └── media/
        ├── dQw4w9WgXcQ.mp4          # if --download video
        └── dQw4w9WgXcQ_audio.m4a    # if --download audio
```

---

## `metadata` Command

Fetch video metadata only (no transcripts or media).

### When to Use

- Quick info lookup (title, channel, duration, tags)
- Building video catalogs or indexes
- Checking video availability before full fetch

### Usage

```bash
# Single video
tubefetch metadata dQw4w9WgXcQ

# Multiple videos
tubefetch metadata dQw4w9WgXcQ abc123def xyz789

# Batch processing
tubefetch metadata --file video_ids.txt --out ./metadata-only
```

### Output

```
output/
└── dQw4w9WgXcQ/
    └── metadata.json
```

**metadata.json contains:**
- `video_id`, `title`, `channel`, `channel_id`
- `duration_seconds`, `upload_date`, `view_count`
- `like_count`, `description`, `tags`
- `thumbnail_url`, `fetched_at`

---

## `transcript` Command

Fetch video transcripts only (no metadata or media).

### When to Use

- Text extraction for NLP/LLM processing
- Transcript-only workflows (already have metadata)
- Language-specific content extraction

### Usage

```bash
# Single video
tubefetch transcript dQw4w9WgXcQ

# With language preferences
tubefetch transcript dQw4w9WgXcQ --languages en,es,fr

# Allow auto-generated transcripts
tubefetch transcript dQw4w9WgXcQ --allow-generated

# Allow any language as fallback
tubefetch transcript dQw4w9WgXcQ --allow-any-language
```

### Language Options

```bash
# Prefer English, fall back to Spanish
tubefetch transcript VIDEO_ID --languages en,es

# Accept auto-generated if manual unavailable
tubefetch transcript VIDEO_ID --allow-generated

# Use any available language if preferred not found
tubefetch transcript VIDEO_ID --languages en --allow-any-language
```

### Output

```
output/
└── dQw4w9WgXcQ/
    ├── transcript.json  # Structured segments with timestamps
    ├── transcript.txt   # Plain text (paragraph-formatted)
    ├── transcript.vtt   # WebVTT format
    └── transcript.srt   # SubRip format
```

---

## `media` Command

Download video/audio files only (no metadata or transcripts).

### When to Use

- Media-only downloads (already have metadata/transcripts)
- Audio extraction for speech processing
- Video archival

### Usage

```bash
# Download video (defaults to video if no --download flag)
tubefetch media dQw4w9WgXcQ

# Explicit video download (merged video+audio MP4)
tubefetch media dQw4w9WgXcQ --download video

# Audio-only download (M4A extraction)
tubefetch media dQw4w9WgXcQ --download audio

# Both video and audio as separate files
tubefetch media dQw4w9WgXcQ --download both
```

### Download Modes Explained

| Mode | Output | Description |
|------|--------|-------------|
| `video` | `VIDEO_ID.mp4` | Merged video+audio in single MP4 file (default) |
| `audio` | `VIDEO_ID_audio.m4a` | Audio-only M4A extraction |
| `both` | Both files above | Separate video and audio files |

### Quality Options

```bash
# Limit video resolution
tubefetch media VIDEO_ID --download video --max-height 720

# Specify formats
tubefetch media VIDEO_ID --download both --format mp4 --audio-format m4a
```

### Output

```
output/
└── dQw4w9WgXcQ/
    └── media/
        ├── dQw4w9WgXcQ.mp4          # video+audio merged
        └── dQw4w9WgXcQ_audio.m4a    # audio-only (if --download audio/both)
```

---

## Common Options

These options work with all commands:

### Input Sources

```bash
# Positional arguments (recommended)
tubefetch dQw4w9WgXcQ abc123def

# From text file (one ID per line)
tubefetch --file video_ids.txt

# From JSONL file
tubefetch --jsonl videos.jsonl --id-field video_id

# Legacy --id flag (deprecated)
tubefetch --id dQw4w9WgXcQ  # Shows deprecation warning
```

### Output Control

```bash
# Custom output directory
tubefetch VIDEO_ID --out ./my-output

# Force re-fetch (ignore cache)
tubefetch VIDEO_ID --force

# Selective force
tubefetch VIDEO_ID --force-metadata
tubefetch VIDEO_ID --force-transcript
tubefetch VIDEO_ID --force-media
```

### Retry and Rate Limiting

```bash
# Configure retries (default: 3)
tubefetch VIDEO_ID --retries 5

# Disable retries
tubefetch VIDEO_ID --retries 0

# Set rate limit (requests per second, default: 2.0)
tubefetch VIDEO_ID --rate-limit 1.5
```

### Batch Processing

```bash
# Parallel workers (default: 3)
tubefetch --file ids.txt --workers 5

# Fail fast (stop on first error)
tubefetch --file ids.txt --fail-fast

# Strict mode (exit code 2 on partial failure)
tubefetch --file ids.txt --strict

# Verbose output
tubefetch --file ids.txt --verbose
```

---

## Examples

### Quick Metadata Lookup

```bash
tubefetch metadata dQw4w9WgXcQ
```

### Transcript for LLM Processing

```bash
tubefetch transcript dQw4w9WgXcQ \
  --languages en \
  --allow-generated \
  --out ./transcripts
```

### High-Quality Video Download

```bash
tubefetch media dQw4w9WgXcQ \
  --download video \
  --max-height 1080 \
  --out ./videos
```

### Complete Fetch with Media

```bash
tubefetch dQw4w9WgXcQ \
  --download both \
  --languages en,es \
  --out ./complete
```

### Batch Processing

```bash
tubefetch --file video_ids.txt \
  --out ./batch-output \
  --workers 5 \
  --verbose
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (or partial failure without `--strict`) |
| `1` | Generic error (bad arguments, initialization failure) |
| `2` | Partial failure with `--strict` mode |
| `3` | All videos failed |

---

## Troubleshooting

### "This video is not available" Errors

If you see errors like `ERROR: [youtube] VIDEO_ID: This video is not available` but the video plays in your browser, this is likely due to:

- **Age-restricted content** - Video requires sign-in
- **Geographic restrictions** - Content blocked in your region
- **YouTube bot detection** - yt-dlp being blocked

**Solution:** Use the YouTube Data API v3 backend:

```bash
pip install tubefetch[youtube-api]
export TUBEFETCH_YT_API_KEY="your-api-key"
tubefetch VIDEO_ID
```

See the [Troubleshooting Guide](troubleshooting.md) for detailed setup instructions and solutions to common issues.

---

## Next Steps

- Check the [API Reference](api.md) for library usage
- Explore [Advanced](advanced.md) features like retry configuration and caching
- Read the [Troubleshooting Guide](troubleshooting.md) for common issues

![tubefetch](https://raw.githubusercontent.com/pointmatic/tubefetch/main/docs/site/images/tubefetch_header_readme.png)

# tubefetch

![CI](https://github.com/pointmatic/tubefetch/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/pointmatic/tubefetch/graph/badge.svg)](https://codecov.io/gh/pointmatic/tubefetch)
[![PyPI](https://img.shields.io/pypi/v/tubefetch)](https://pypi.org/project/tubefetch/)
![Python](https://img.shields.io/pypi/pyversions/tubefetch)
![Typed](https://img.shields.io/badge/typed-mypy%20strict-blue)
![License](https://img.shields.io/github/license/pointmatic/tubefetch)

A Python CLI and library that fetches and extracts structured metadata and transcripts from YouTube videos, producing LLM-ready plain text, content hashes for change detection, and unified video bundles with batch processing, caching, and retry logic.

TubeFetch is a Python tool that extracts structured, AI-ready content from YouTube videos. Given one or more video IDs, URLs, playlists, or channels, it produces normalized metadata, transcripts, and optional media in formats optimized for downstream AI/LLM pipelines (summarization, fact-checking, RAG, search indexing, etc.). It provides content hashes for change detection, optional token count estimates, and unified video bundles. The tool supports both CLI and library usage with batch processing, intelligent caching, configurable retries via gentlify, and rate limiting.

## Features

- **Metadata** — title, channel, duration, tags, upload date via yt-dlp (or YouTube Data API v3)
- **Transcripts** — fetched via youtube-transcript-api with language preference and fallback
- **LLM-ready text** — intelligent paragraph chunking, optional timestamps, configurable gap thresholds
- **Content hashing** — SHA-256 hashes for change detection on metadata and transcripts
- **Token counting** — optional token count estimation via tiktoken for LLM cost planning
- **Playlist/Channel resolution** — resolve playlists and channels to video IDs with max_videos limiting
- **Video bundles** — unified JSON output combining metadata, transcript, errors, and hashes
- **Media** — optional video/audio download via yt-dlp
- **Export formats** — JSON, plain text, WebVTT (.vtt), SubRip (.srt)
- **Batch processing** — concurrent workers with per-video error isolation
- **Caching** — skip already-fetched data; selective `--force` overrides
- **Retry** — powered by gentlify with exponential backoff and jitter on transient errors
- **Rate limiting** — token bucket algorithm, shared across workers
- **CLI + Library** — use from the command line or import as a Python package

## Installation

Requires **Python 3.14+**.

```bash
pip install tubefetch
```

### Optional: Token Counting

Install for LLM token count estimation:

```bash
pip install 'tubefetch[tokens]'
```

Enables the `--tokenizer` flag for estimating token counts using tiktoken (useful for LLM cost planning).

### Optional: YouTube Data API v3

Install for age-restricted or geo-restricted videos:

```bash
pip install 'tubefetch[youtube-api]'
export TUBEFETCH_YT_API_KEY="your-api-key"
```

The YouTube Data API backend is used when:
- Videos are age-restricted (require sign-in)
- yt-dlp is blocked by YouTube's bot detection
- You need higher rate limits

Get a free API key from [Google Cloud Console](https://console.cloud.google.com/). See [Troubleshooting](https://github.com/pointmatic/tubefetch/blob/main/docs/site/troubleshooting.md) for setup instructions.

> **Note:** The CLI accepts video IDs/URLs as positional arguments. Use `tubefetch VIDEO_ID` for the default behavior (metadata + transcript), or specialized commands like `metadata`, `transcript`, `media` for specific content.

## Quick Start

### CLI

```bash
# Fetch a single video
tubefetch dQw4w9WgXcQ

# Multiple videos
tubefetch VIDEO_ID_1 VIDEO_ID_2 VIDEO_ID_3

# From a file
tubefetch --file video_ids.txt

# With media download
tubefetch VIDEO_ID --download video

# Batch from a file
tubefetch --file video_ids.txt --workers 3

# Transcript only
tubefetch transcript dQw4w9WgXcQ --languages en,fr

# Metadata only
tubefetch metadata dQw4w9WgXcQ

# Media only (downloads video+audio by default)
tubefetch media dQw4w9WgXcQ
```

### Specialized Commands

For exceptional cases when you only need specific data:

```bash
# Metadata only
tubefetch metadata VIDEO_ID

# Transcript only
tubefetch transcript VIDEO_ID

# Media only
tubefetch media VIDEO_ID
```

### Library API

```python
from tubefetch import fetch_video, fetch_batch, FetchOptions

# Single video
result = fetch_video("dQw4w9WgXcQ")
print(result.metadata.title)
print(result.transcript.segments[0].text)

# With options
opts = FetchOptions(out="./output", languages=["en", "fr"], download="audio")
result = fetch_video("dQw4w9WgXcQ", opts)

# Batch
results = fetch_batch(["dQw4w9WgXcQ", "abc12345678"], opts)
print(f"{results.succeeded}/{results.total} succeeded")
```

### AI Pipeline Usage

```bash
# LLM-ready transcript with token counting
tubefetch VIDEO_ID --tokenizer cl100k_base --bundle

# Playlist processing with unified bundles
tubefetch --playlist "https://www.youtube.com/playlist?list=PLxxx" --bundle --tokenizer cl100k_base

# Content monitoring with hashing
tubefetch VIDEO_ID --force
# Check content_hash in metadata.json and transcript.json for changes
```

```python
from tubefetch import fetch_video, FetchOptions

# AI-optimized output
opts = FetchOptions(
    tokenizer="cl100k_base",  # Estimate token counts
    bundle=True,              # Unified video_bundle.json
    txt_timestamps=True,      # Add [MM:SS] markers
    txt_gap_threshold=3.0     # Paragraph chunking threshold
)
result = fetch_video("dQw4w9WgXcQ", opts)
print(f"Token count: {result.transcript.token_count}")
print(f"Content hash: {result.metadata.content_hash}")
```

### Playlist & Channel Processing

```bash
# Fetch entire playlist
tubefetch --playlist "https://www.youtube.com/playlist?list=PLxxx"

# Limit to first 10 videos
tubefetch --playlist "https://www.youtube.com/playlist?list=PLxxx" --max-videos 10

# Fetch from channel
tubefetch --channel "https://www.youtube.com/@channelname" --max-videos 20

# Combine with other options
tubefetch --playlist "https://..." --bundle --tokenizer cl100k_base --workers 5
```

```python
from tubefetch import resolve_playlist, resolve_channel, fetch_batch, FetchOptions

# Resolve playlist to video IDs
video_ids = resolve_playlist("https://www.youtube.com/playlist?list=PLxxx", max_videos=10)
print(f"Found {len(video_ids)} videos")

# Resolve channel uploads
video_ids = resolve_channel("https://www.youtube.com/@channelname", max_videos=20)

# Process with AI-ready options
opts = FetchOptions(bundle=True, tokenizer="cl100k_base")
results = fetch_batch(video_ids, opts)
```

## Output Structure

```
out/
├── <video_id>/
│   ├── metadata.json          # Metadata with content_hash
│   ├── transcript.json         # Transcript with content_hash and token_count
│   ├── transcript.txt          # LLM-ready plain text
│   ├── transcript.vtt          # WebVTT subtitles
│   ├── transcript.srt          # SubRip subtitles
│   ├── video_bundle.json       # Unified bundle (with --bundle)
│   └── media/
│       ├── video.mp4
│       └── audio.m4a
├── resolved_ids.json           # Playlist/channel resolution output
└── summary.json                # Batch processing summary
```

## Configuration

Options are resolved in this order (first wins):

1. **CLI flags**
2. **Environment variables** (prefix `TUBEFETCH_`)
3. **YAML config file** (`tubefetch.yaml`)
4. **Defaults**

### CLI Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--id` | Video ID or URL (repeatable) | — |
| `--file` | Text/CSV file with IDs | — |
| `--jsonl` | JSONL file with IDs | — |
| `--id-field` | Field name in CSV/JSONL | `id` |
| `--out` | Output directory | `./out` |
| `--languages` | Comma-separated language codes | `en` |
| `--allow-generated` | Allow auto-generated transcripts | `true` |
| `--allow-any-language` | Fall back to any language | `false` |
| `--download` | `none`, `video`, `audio`, `both` | `none` |
| `--max-height` | Max video height (e.g. 720) | — |
| `--format` | Video format | `best` |
| `--audio-format` | Audio format | `best` |
| `--force` | Force re-fetch everything | `false` |
| `--force-metadata` | Force re-fetch metadata only | `false` |
| `--force-transcript` | Force re-fetch transcript only | `false` |
| `--force-media` | Force re-download media only | `false` |
| `--retries` | Max retries per request | `3` |
| `--rate-limit` | Requests per second | `2.0` |
| `--workers` | Parallel workers for batch | `3` |
| `--fail-fast` | Stop on first failure | `false` |
| `--strict` | Exit code 2 on partial failure | `false` |
| `--verbose` | Verbose output | `false` |

### Environment Variables

All options can be set via environment variables with the `TUBEFETCH_` prefix:

```bash
export TUBEFETCH_OUT=./output
export TUBEFETCH_LANGUAGES=en,fr
export TUBEFETCH_DOWNLOAD=video
export TUBEFETCH_YT_API_KEY=your-api-key
```

### YAML Config File

Create `tubefetch.yaml` in the working directory:

```yaml
out: ./output
languages:
  - en
  - fr
download: none
allow_generated: true
retries: 3
rate_limit: 2.0
workers: 3
```

## Retry Configuration

`tubefetch` uses [gentlify](https://github.com/pointmatic/gentlify) for intelligent retry management with exponential backoff and jitter.

### How Retries Work

- **Transient errors** (rate limits, network errors, service errors) are automatically retried
- **Permanent errors** (video not found, transcripts disabled) fail immediately without retry
- **Configurable attempts**: Set `--retries N` to control max retry attempts (default: 3)
- **Disable retries**: Set `--retries 0` for external retry management (e.g., with your own gentlify configuration)

### Examples

```python
from tubefetch import fetch_video, FetchOptions

# Default: 3 retry attempts
result = fetch_video("dQw4w9WgXcQ")

# Custom retry count
opts = FetchOptions(retries=5)
result = fetch_video("dQw4w9WgXcQ", opts)

# Disable internal retries (for external retry management)
opts = FetchOptions(retries=0)
result = fetch_video("dQw4w9WgXcQ", opts)
```

CLI:
```bash
# Custom retry count
tubefetch dQw4w9WgXcQ --retries 5

# Disable retries
tubefetch dQw4w9WgXcQ --retries 0
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (or partial failure without `--strict`) |
| 1 | Generic error (e.g. no IDs provided) |
| 2 | Partial failure with `--strict` |
| 3 | All videos failed |

## Roadmap

TubeFetch v1.4.1 is a production-ready AI content extraction tool. **Phase M (AI-Ready Content Extraction) is complete** with the following features now available:

- ✅ **LLM-ready transcript formatting** (v1.0.0) — intelligent paragraph chunking with configurable silence gap detection, optional timestamp markers for citation support, and auto-generated transcript notices
- ✅ **Content hashing** (v1.1.0) — SHA-256 hashes for metadata and transcripts to enable change detection in incremental pipelines
- ✅ **Token count estimation** (v1.2.0) — optional token counting via tiktoken for context window planning (GPT-4, GPT-4o, etc.)
- ✅ **Playlist/channel resolution** (v1.3.0) — accept playlist and channel URLs as batch input sources with automatic video ID extraction
- ✅ **Video bundles** (v1.4.0) — unified `video_bundle.json` output combining metadata + transcript + errors in a single file

See the [AI-Ready Features guide](https://github.com/pointmatic/tubefetch/blob/main/docs/guides/ai-ready-features.md) for usage examples and the [stories.md](https://github.com/pointmatic/tubefetch/blob/main/docs/specs/stories.md#phase-m-ai-ready-content-extraction) for implementation details.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=tubefetch --cov-report=term-missing

# Run integration tests (requires network)
RUN_INTEGRATION=1 python -m pytest tests/integration/
```

## License

Apache-2.0

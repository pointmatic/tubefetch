![tubefetch](https://raw.githubusercontent.com/pointmatic/tubefetch/main/docs/site/images/tubefetch_header_readme.png)

# tubefetch

![CI](https://github.com/pointmatic/tubefetch/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/pointmatic/tubefetch/graph/badge.svg)](https://codecov.io/gh/pointmatic/tubefetch)
[![PyPI](https://img.shields.io/pypi/v/tubefetch)](https://pypi.org/project/tubefetch/)
![Python](https://img.shields.io/pypi/pyversions/tubefetch)
![License](https://img.shields.io/github/license/pointmatic/tubefetch)

A Python CLI and library that fetches and extracts structured metadata and transcripts from YouTube videos, producing LLM-ready plain text, content hashes for change detection, and unified video bundles with batch processing, caching, and retry logic.

TubeFetch is a Python tool that extracts structured, AI-ready content from YouTube videos. Given one or more video IDs, URLs, playlists, or channels, it produces normalized metadata, transcripts, and optional media in formats optimized for downstream AI/LLM pipelines (summarization, fact-checking, RAG, search indexing, etc.). It provides content hashes for change detection, optional token count estimates, and unified video bundles. The tool supports both CLI and library usage with batch processing, intelligent caching, configurable retries via gentlify, and rate limiting.

## Features

- **Metadata** — title, channel, duration, tags, upload date via yt-dlp (or YouTube Data API v3)
- **Transcripts** — fetched via youtube-transcript-api with language preference and fallback
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

For YouTube Data API v3 support (optional):

```bash
pip install tubefetch[youtube-api]
```

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

## Output Structure

```
out/
├── <video_id>/
│   ├── metadata.json
│   ├── transcript.json
│   ├── transcript.txt
│   ├── transcript.vtt
│   ├── transcript.srt
│   └── media/
│       ├── video.mp4
│       └── audio.m4a
└── summary.json
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

MPL-2.0

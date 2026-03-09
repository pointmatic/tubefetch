# AI-Ready Features

TubeFetch is designed from the ground up to produce AI-ready content optimized for LLM pipelines, RAG systems, and content analysis workflows.

## Overview

Phase M (AI-Ready Content Extraction) introduces five key capabilities:

1. **LLM-Ready Text Formatting** — Intelligent paragraph chunking and optional timestamps
2. **Content Hashing** — SHA-256 hashes for change detection
3. **Token Counting** — Cost estimation for LLM processing
4. **Playlist & Channel Resolution** — Batch input from playlists and channels
5. **Unified Video Bundles** — Single JSON file with all video data

## Quick Start

### Basic AI Pipeline

```bash
# Fetch with token counting and unified bundle
tubefetch VIDEO_ID --tokenizer cl100k_base --bundle
```

This produces:
- `metadata.json` with `content_hash`
- `transcript.json` with `content_hash` and `token_count`
- `transcript.txt` with intelligent paragraph formatting
- `video_bundle.json` with all data in one file

### Batch Processing from Playlist

```bash
# Process entire playlist with AI-ready output
tubefetch --playlist "https://www.youtube.com/playlist?list=PLxxx" \
  --bundle \
  --tokenizer cl100k_base \
  --workers 5
```

### Library Usage

```python
from tubefetch import fetch_video, FetchOptions

opts = FetchOptions(
    tokenizer="cl100k_base",  # Estimate token counts
    bundle=True,              # Unified output
    txt_timestamps=True,      # Add [MM:SS] markers
    txt_gap_threshold=3.0     # Paragraph chunking
)

result = fetch_video("dQw4w9WgXcQ", opts)
print(f"Tokens: {result.transcript.token_count}")
print(f"Hash: {result.metadata.content_hash}")
```

## Feature Guides

Detailed documentation for each AI-ready feature:

- **[LLM Text Formatting](llm-text-formatting.md)** — Paragraph chunking, timestamps, gap thresholds
- **[Content Hashing](content-hashing.md)** — Change detection workflows
- **[Token Counting](token-counting.md)** — Cost estimation for LLMs
- **[Playlist Resolution](playlist-resolution.md)** — Batch input sources
- **[Video Bundles](video-bundles.md)** — Unified output format

## Use Cases

See the **[Use Cases Guide](use-cases.md)** for real-world examples:

- RAG pipeline integration
- Content monitoring and change detection
- Batch channel analysis
- Training data preparation
- Fact-checking workflows

## Installation

Install with token counting support:

```bash
pip install 'tubefetch[tokens]'
```

This enables the `--tokenizer` flag for token count estimation using tiktoken.

## Next Steps

1. Choose a feature guide above based on your use case
2. Review the [Use Cases Guide](use-cases.md) for workflow examples
3. Check the [CLI Reference](../reference/cli.md) for all available flags
4. Explore the [API Reference](../reference/api.md) for programmatic usage

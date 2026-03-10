# Playlist & Channel Resolution

TubeFetch can resolve entire playlists and channels to video IDs, enabling batch processing of large content collections.

## Overview

Resolution features:

- **Playlist URLs** — Extract all video IDs from a playlist
- **Channel URLs** — Extract video IDs from channel uploads
- **Auto-detection** — Automatically detect input type
- **Max videos limiting** — Control batch size
- **Resolved IDs output** — Save resolved IDs to JSON for reproducibility

## Basic Usage

### Playlist Resolution

```bash
# Fetch entire playlist
tubefetch --playlist "https://www.youtube.com/playlist?list=PLxxx"

# Limit to first 10 videos
tubefetch --playlist "https://www.youtube.com/playlist?list=PLxxx" --max-videos 10
```

### Channel Resolution

```bash
# Fetch from channel uploads
tubefetch --channel "https://www.youtube.com/@channelname"

# Limit to most recent 20 videos
tubefetch --channel "https://www.youtube.com/@channelname" --max-videos 20

# Also works with channel IDs
tubefetch --channel "https://www.youtube.com/channel/UCxxx"
```

### Combined with Other Features

```bash
# Playlist with AI-ready output
tubefetch --playlist "https://..." --bundle --tokenizer cl100k_base

# Channel with specific languages
tubefetch --channel "https://..." --languages en,es --max-videos 50

# Parallel processing
tubefetch --playlist "https://..." --workers 10
```

## Library Usage

### Resolve Playlist

```python
from tubefetch import resolve_playlist

# Get all video IDs
video_ids = resolve_playlist("https://www.youtube.com/playlist?list=PLxxx")
print(f"Found {len(video_ids)} videos")

# Limit results
video_ids = resolve_playlist(
    "https://www.youtube.com/playlist?list=PLxxx",
    max_videos=10
)
```

### Resolve Channel

```python
from tubefetch import resolve_channel

# Get channel uploads
video_ids = resolve_channel("https://www.youtube.com/@channelname")

# Limit to recent videos
video_ids = resolve_channel(
    "https://www.youtube.com/@channelname",
    max_videos=20
)
```

### Auto-Detection

```python
from tubefetch.services.resolver import resolve_input

# Automatically detect input type
video_ids = resolve_input("https://www.youtube.com/playlist?list=PLxxx")
video_ids = resolve_input("https://www.youtube.com/@channelname")
video_ids = resolve_input("dQw4w9WgXcQ")  # Single video
```

### Batch Processing

```python
from tubefetch import resolve_playlist, fetch_batch, FetchOptions

# Resolve and process
video_ids = resolve_playlist(
    "https://www.youtube.com/playlist?list=PLxxx",
    max_videos=50
)

opts = FetchOptions(
    bundle=True,
    tokenizer="cl100k_base",
    workers=5
)

results = fetch_batch(video_ids, opts)
print(f"Processed {results.succeeded}/{results.total} videos")
```

## Resolved IDs Output

Resolution creates `resolved_ids.json` in the output directory:

```json
{
  "source_url": "https://www.youtube.com/playlist?list=PLxxx",
  "count": 15,
  "video_ids": [
    "dQw4w9WgXcQ",
    "abc12345678",
    "xyz98765432",
    ...
  ],
  "resolved_at": "2026-03-09T16:30:00Z"
}
```

This file provides:
- **Reproducibility** — Re-run with same IDs
- **Audit trail** — Track what was processed
- **Debugging** — Verify resolution worked correctly

## Use Cases

### 1. Channel Archival

Archive all content from a channel:

```bash
#!/bin/bash
# archive_channel.sh

CHANNEL="https://www.youtube.com/@channelname"
OUT_DIR="./archive/$(date +%Y%m%d)"

tubefetch --channel "$CHANNEL" \
  --out "$OUT_DIR" \
  --bundle \
  --tokenizer cl100k_base \
  --workers 5
```

### 2. Playlist Analysis

Analyze an educational playlist:

```python
from tubefetch import resolve_playlist, fetch_batch, FetchOptions
import json

# Resolve playlist
playlist_url = "https://www.youtube.com/playlist?list=PLxxx"
video_ids = resolve_playlist(playlist_url)

# Fetch with AI features
opts = FetchOptions(
    bundle=True,
    tokenizer="cl100k_base"
)
results = fetch_batch(video_ids, opts)

# Analyze
total_tokens = 0
total_duration = 0

for result in results.results:
    if result.transcript:
        total_tokens += result.transcript.token_count or 0
    if result.metadata:
        total_duration += result.metadata.duration_seconds or 0

print(f"Playlist stats:")
print(f"  Videos: {len(video_ids)}")
print(f"  Total duration: {total_duration / 3600:.1f} hours")
print(f"  Total tokens: {total_tokens:,}")
print(f"  Avg tokens/video: {total_tokens // len(video_ids):,}")
```

### 3. Incremental Updates

Monitor channel for new content:

```python
from tubefetch import resolve_channel, fetch_batch, FetchOptions
from pathlib import Path
import json

def update_channel_archive(channel_url: str, out_dir: Path):
    """Fetch only new videos from a channel."""
    # Load previously processed IDs
    resolved_path = out_dir / "resolved_ids.json"
    if resolved_path.exists():
        with open(resolved_path) as f:
            previous_ids = set(json.load(f)["video_ids"])
    else:
        previous_ids = set()
    
    # Resolve current channel state
    current_ids = resolve_channel(channel_url, max_videos=100)
    
    # Find new videos
    new_ids = [vid for vid in current_ids if vid not in previous_ids]
    
    if not new_ids:
        print("No new videos")
        return
    
    print(f"Found {len(new_ids)} new videos")
    
    # Fetch new videos
    opts = FetchOptions(bundle=True, tokenizer="cl100k_base")
    results = fetch_batch(new_ids, opts)
    
    print(f"Processed {results.succeeded}/{results.total} new videos")
```

### 4. Selective Processing

Process only specific videos from a playlist:

```python
from tubefetch import resolve_playlist, fetch_video, FetchOptions

# Resolve playlist
all_ids = resolve_playlist("https://www.youtube.com/playlist?list=PLxxx")

# Filter by criteria (e.g., skip already processed)
processed_ids = load_processed_ids()  # Your tracking
new_ids = [vid for vid in all_ids if vid not in processed_ids]

# Process with budget limit
opts = FetchOptions(tokenizer="cl100k_base")
max_tokens = 500_000
total_tokens = 0

for vid in new_ids:
    result = fetch_video(vid, opts)
    if result.transcript and result.transcript.token_count:
        total_tokens += result.transcript.token_count
        if total_tokens >= max_tokens:
            print(f"Reached token budget at {total_tokens:,} tokens")
            break
```

## Max Videos Behavior

The `--max-videos` flag limits the number of videos returned:

```bash
# Get first 10 videos
tubefetch --playlist "https://..." --max-videos 10
```

**Important notes:**
- Videos are returned in **playlist order**
- For channels, returns **most recent** uploads first
- Useful for testing or staying within budgets
- Can be combined with any other flags

## URL Formats

### Supported Playlist URLs

```
https://www.youtube.com/playlist?list=PLxxx
https://youtube.com/playlist?list=PLxxx
www.youtube.com/playlist?list=PLxxx
PLxxx  # Just the playlist ID
```

### Supported Channel URLs

```
https://www.youtube.com/@channelname
https://www.youtube.com/channel/UCxxx
https://youtube.com/@channelname
@channelname  # Just the handle
```

## Error Handling

### Invalid URLs

```python
from tubefetch.services.resolver import resolve_playlist
from tubefetch.core.errors import MetadataError

try:
    video_ids = resolve_playlist("invalid-url")
except MetadataError as e:
    print(f"Resolution failed: {e}")
```

### Empty Playlists

```python
video_ids = resolve_playlist("https://www.youtube.com/playlist?list=PLempty")
# Returns: []
```

### Private/Deleted Content

Private or deleted playlists/channels will raise a `MetadataError`.

## Performance

Resolution is **fast** because it uses yt-dlp's `extract_flat=True`:

- Only extracts video IDs, not full metadata
- No video downloads
- Minimal API calls
- Typical speed: 100+ videos/second

## Technical Details

### Resolution Process

1. Pass URL to yt-dlp with `extract_flat=True`
2. Extract `entries` from response
3. Parse video IDs from entries
4. Apply `max_videos` limit if specified
5. Write `resolved_ids.json`

### ID Extraction

```python
# From entry with 'id' field
video_id = entry["id"]

# From entry with 'url' field
from tubefetch.utils.id_parser import parse_one
video_id = parse_one(entry["url"])
```

### Output Location

```
out/
├── resolved_ids.json  # Resolution output
└── <video_id>/        # Individual videos
    └── ...
```

## Related Features

- **[Video Bundles](video-bundles.md)** — Process playlists with unified output
- **[Token Counting](token-counting.md)** — Estimate costs for entire playlists
- **[Content Hashing](content-hashing.md)** — Monitor channels for changes
- **[Batch Processing](../advanced/batch-processing.md)** — Optimize parallel processing

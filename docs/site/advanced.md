# Advanced Features

Advanced usage patterns and integration with AI/LLM pipelines.

## Retry Configuration with gentlify

yt-fetch uses [gentlify](https://github.com/pointmatic/gentlify) for intelligent retry logic with exponential backoff and jitter.

### Default Retry Behavior

```python
from yt_fetch import fetch_video, FetchOptions

# Default: 3 retries with exponential backoff
options = FetchOptions(retries=3)
result = fetch_video("VIDEO_ID", options)
```

### Custom Retry Configuration

```python
from yt_fetch import fetch_video, FetchOptions

# More aggressive retries
options = FetchOptions(
    retries=5,
    rate_limit=1.0  # Slower rate to avoid throttling
)
result = fetch_video("VIDEO_ID", options)
```

### Disable Internal Retries

For advanced use cases where you want to manage retries externally:

```python
from yt_fetch import fetch_video, FetchOptions

# Disable internal retries
options = FetchOptions(retries=0)
result = fetch_video("VIDEO_ID", options)

# Handle retries with your own gentlify configuration
```

## Rate Limiting

### Built-in Rate Limiting

```python
from yt_fetch import fetch_videos, FetchOptions

# Limit to 1 request per second
options = FetchOptions(rate_limit=1.0)
batch_result = fetch_videos(video_ids, options)
```

### Disable Rate Limiting

For library consumers managing throttling externally:

```python
options = FetchOptions(rate_limit=0)  # Disable internal rate limiting
```

## AI/LLM Integration

### Transcript for Summarization

```python
from yt_fetch import fetch_video

result = fetch_video("VIDEO_ID")

if result.transcript:
    # Read plain text transcript
    with open(f"./out/{result.video_id}/transcript.txt") as f:
        transcript_text = f.read()
    
    # Send to LLM for summarization
    # summary = llm.summarize(transcript_text)
```

### Structured Data for RAG

```python
import json
from yt_fetch import fetch_video

result = fetch_video("VIDEO_ID")

# Load structured transcript
with open(f"./out/{result.video_id}/transcript.json") as f:
    transcript_data = json.load(f)

# Use segments for RAG with timestamps
for segment in transcript_data["segments"]:
    # Store in vector database with metadata
    # db.add(
    #     text=segment["text"],
    #     metadata={
    #         "video_id": result.video_id,
    #         "timestamp": segment["start"],
    #         "title": result.metadata.title
    #     }
    # )
    pass
```

### Batch Processing for Dataset Creation

```python
from yt_fetch import fetch_videos, FetchOptions

# Fetch large dataset
video_ids = [...]  # List of video IDs

options = FetchOptions(
    out_dir="./dataset",
    retries=5,
    rate_limit=1.0,
    fail_fast=False
)

batch_result = fetch_videos(video_ids, options)

# Filter successful results
successful = [r for r in batch_result.results if r.success]
print(f"Successfully fetched {len(successful)} videos")
```

## Caching and Idempotency

### Default Caching Behavior

yt-fetch automatically caches fetched data. Re-running the same fetch will use cached files:

```python
from yt_fetch import fetch_video

# First fetch - downloads from YouTube
result1 = fetch_video("VIDEO_ID")

# Second fetch - uses cached files (no network request)
result2 = fetch_video("VIDEO_ID")
```

### Force Re-fetch

```python
from yt_fetch import fetch_video, FetchOptions

# Force re-fetch everything
options = FetchOptions(force=True)
result = fetch_video("VIDEO_ID", options)

# Selective force
options = FetchOptions(
    force_metadata=True,  # Re-fetch metadata only
    force_transcript=False  # Use cached transcript
)
```

## Error Classification

### Programmatic Error Handling

```python
from yt_fetch import fetch_video, FetchErrorCode, FetchPhase

result = fetch_video("VIDEO_ID")

for error in result.errors:
    # Check error type
    if error.code == FetchErrorCode.TRANSCRIPTS_DISABLED:
        print("No transcripts available")
    elif error.code == FetchErrorCode.VIDEO_UNAVAILABLE:
        print("Video is private or deleted")
    elif error.code == FetchErrorCode.RATE_LIMITED:
        print("Rate limited - retry later")
    
    # Check which phase failed
    if error.phase == FetchPhase.METADATA:
        print("Metadata fetch failed")
    elif error.phase == FetchPhase.TRANSCRIPT:
        print("Transcript fetch failed")
    
    # Check if retryable
    if error.retryable:
        print("Transient error - retry may succeed")
    else:
        print("Permanent error - retry won't help")
```

## Media Download

### Video and Audio Download

```python
from yt_fetch import fetch_video, FetchOptions

options = FetchOptions(
    download="both",  # Download video and audio
    max_height=1080,  # Max resolution
)

result = fetch_video("VIDEO_ID", options)

# Media files saved to ./out/VIDEO_ID/media/
```

### Audio-Only for Speech-to-Text

```python
from yt_fetch import fetch_video, FetchOptions

# Download audio for STT fallback when no transcript exists
options = FetchOptions(download="audio")
result = fetch_video("VIDEO_ID", options)

if not result.transcript:
    # Use downloaded audio for speech-to-text
    audio_path = f"./out/{result.video_id}/media/audio.m4a"
    # transcript = stt_service.transcribe(audio_path)
```

## YouTube Data API v3

For richer metadata, use the YouTube Data API v3 (requires API key):

```python
import os
from yt_fetch import fetch_video, FetchOptions

# Set API key via environment variable
os.environ["YOUTUBE_API_KEY"] = "your-api-key"

options = FetchOptions(
    metadata_source="youtube-data-api"  # Use API instead of yt-dlp
)

result = fetch_video("VIDEO_ID", options)
```

## Parallel Processing

```python
import asyncio
from yt_fetch import fetch_videos, FetchOptions

# Concurrent workers (default: 3)
options = FetchOptions(
    workers=5,  # Process 5 videos concurrently
    rate_limit=2.0  # Shared rate limit across workers
)

batch_result = fetch_videos(video_ids, options)
```

## Next Steps

- Check the [API Reference](api.md) for detailed API documentation
- Review [Usage](usage.md) for CLI commands
- Read [Getting Started](getting-started.md) for basics

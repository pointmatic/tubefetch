# API Reference

Use tubefetch as a Python library in your projects.

## Installation

```bash
pip install tubefetch
```

## Quick Start

```python
from tubefetch import fetch_video, FetchOptions

# Fetch a single video
result = fetch_video("dQw4w9WgXcQ")

# Access metadata
print(result.metadata.title)
print(result.metadata.channel_title)

# Access transcript
if result.transcript:
    for segment in result.transcript.segments:
        print(f"[{segment.start}s] {segment.text}")
```

## Core Functions

### `fetch_video()`

Fetch metadata, transcript, and optionally media for a single video.

```python
def fetch_video(
    video_id: str,
    options: FetchOptions | None = None
) -> FetchResult
```

**Parameters:**
- `video_id` (str): YouTube video ID or URL
- `options` (FetchOptions, optional): Configuration options

**Returns:**
- `FetchResult`: Contains metadata, transcript, and errors

**Example:**

```python
from tubefetch import fetch_video, FetchOptions

options = FetchOptions(
    out_dir="./output",
    languages=["en", "en-US"],
    allow_generated=True
)

result = fetch_video("VIDEO_ID", options)
```

### `fetch_videos()`

Fetch multiple videos with batch processing.

```python
def fetch_videos(
    video_ids: list[str],
    options: FetchOptions | None = None
) -> BatchResult
```

**Parameters:**
- `video_ids` (list[str]): List of video IDs or URLs
- `options` (FetchOptions, optional): Configuration options

**Returns:**
- `BatchResult`: Contains list of FetchResult objects

**Example:**

```python
from tubefetch import fetch_videos

video_ids = ["ID1", "ID2", "ID3"]
batch_result = fetch_videos(video_ids)

for result in batch_result.results:
    print(f"Video: {result.metadata.title}")
```

## Data Models

### `FetchOptions`

Configuration for fetch operations.

```python
class FetchOptions(BaseModel):
    out_dir: str = "./out"
    languages: list[str] = ["en"]
    allow_generated: bool = False
    allow_any_language: bool = False
    download: str = "none"  # "none", "video", "audio", "both"
    max_height: int | None = None
    retries: int = 3
    rate_limit: float = 2.0
    fail_fast: bool = False
    force: bool = False
    force_metadata: bool = False
    force_transcript: bool = False
    force_media: bool = False
```

### `Metadata`

Video metadata information.

```python
class Metadata(BaseModel):
    video_id: str
    source_url: str
    title: str | None
    channel_title: str | None
    channel_id: str | None
    upload_date: str | None  # ISO 8601
    duration_seconds: float | None
    description: str | None
    tags: list[str]
    view_count: int | None
    like_count: int | None
    fetched_at: datetime
    metadata_source: str  # "yt-dlp" or "youtube-data-api"
```

### `Transcript`

Transcript with segments.

```python
class TranscriptSegment(BaseModel):
    start: float  # seconds
    duration: float  # seconds
    text: str

class Transcript(BaseModel):
    video_id: str
    language: str
    is_generated: bool | None
    segments: list[TranscriptSegment]
    fetched_at: datetime
    transcript_source: str  # "youtube-transcript-api"
    available_languages: list[str]
```

### `FetchResult`

Result of fetching a single video.

```python
class FetchResult(BaseModel):
    video_id: str
    metadata: Metadata | None
    transcript: Transcript | None
    errors: list[FetchError]
    success: bool
```

### `FetchError`

Structured error information.

```python
class FetchError(BaseModel):
    code: FetchErrorCode  # Enum
    phase: FetchPhase  # "metadata", "transcript", "media"
    retryable: bool
    message: str
    details: dict | None
```

## Error Handling

```python
from tubefetch import fetch_video, FetchErrorCode

result = fetch_video("VIDEO_ID")

if not result.success:
    for error in result.errors:
        if error.code == FetchErrorCode.TRANSCRIPTS_DISABLED:
            print("Transcripts are disabled for this video")
        elif error.retryable:
            print("Transient error, retry may succeed")
        else:
            print("Permanent error, retry won't help")
```

## Advanced Usage

### Custom Retry Configuration

```python
from tubefetch import fetch_video, FetchOptions

options = FetchOptions(
    retries=5,  # Max retry attempts
    rate_limit=1.0  # 1 request per second
)

result = fetch_video("VIDEO_ID", options)
```

### Media Download

```python
from tubefetch import fetch_video, FetchOptions

options = FetchOptions(
    download="both",  # Download video and audio
    max_height=720,  # Max 720p resolution
)

result = fetch_video("VIDEO_ID", options)
```

### Batch Processing with Error Handling

```python
from tubefetch import fetch_videos, FetchOptions

options = FetchOptions(
    fail_fast=False,  # Continue on errors
    retries=3
)

batch_result = fetch_videos(["ID1", "ID2", "ID3"], options)

successful = [r for r in batch_result.results if r.success]
failed = [r for r in batch_result.results if not r.success]

print(f"Success: {len(successful)}, Failed: {len(failed)}")
```

## Next Steps

- Learn about [Advanced](advanced.md) features
- Check [Usage](usage.md) for CLI commands

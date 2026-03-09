# Video Bundles

TubeFetch can create unified `video_bundle.json` files that combine metadata, transcript, errors, content hash, and token count in a single output file.

## Overview

Video bundles provide:

- **Single source of truth** — All video data in one file
- **Simplified pipelines** — Read one file instead of multiple
- **Complete context** — Includes errors and processing metadata
- **AI-ready format** — Optimized for LLM consumption

Bundles are created with the `--bundle` flag.

## Basic Usage

### CLI

```bash
# Create bundle for single video
tubefetch VIDEO_ID --bundle

# Combine with other features
tubefetch VIDEO_ID --bundle --tokenizer cl100k_base

# Batch processing with bundles
tubefetch --file videos.txt --bundle --workers 5
```

### Library

```python
from tubefetch import fetch_video, FetchOptions

opts = FetchOptions(bundle=True)
result = fetch_video("dQw4w9WgXcQ", opts)

# Bundle is written to out/<video_id>/video_bundle.json
```

## Bundle Structure

### Complete Example

```json
{
  "video_id": "dQw4w9WgXcQ",
  "metadata": {
    "video_id": "dQw4w9WgXcQ",
    "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "title": "Example Video",
    "channel_title": "Example Channel",
    "channel_id": "UCxxx",
    "upload_date": "2024-01-01",
    "duration_seconds": 180.5,
    "description": "Video description...",
    "tags": ["tutorial", "python"],
    "view_count": 1000000,
    "like_count": 50000,
    "fetched_at": "2026-03-09T16:30:00Z",
    "metadata_source": "yt-dlp",
    "content_hash": "a1b2c3d4e5f6..."
  },
  "transcript": {
    "video_id": "dQw4w9WgXcQ",
    "language": "en",
    "is_generated": false,
    "segments": [
      {
        "start": 0.0,
        "duration": 2.5,
        "text": "Hello and welcome"
      },
      {
        "start": 2.5,
        "duration": 3.0,
        "text": "to this tutorial"
      }
    ],
    "fetched_at": "2026-03-09T16:30:00Z",
    "transcript_source": "youtube-transcript-api",
    "available_languages": ["en", "es", "fr"],
    "content_hash": "f6e5d4c3b2a1...",
    "token_count": 1523
  },
  "errors": [],
  "content_hash": "9876543210ab...",
  "token_count": 1523,
  "fetched_at": "2026-03-09T16:30:00Z"
}
```

### With Errors

```json
{
  "video_id": "abc12345678",
  "metadata": {
    "video_id": "abc12345678",
    "title": "Example Video",
    ...
  },
  "transcript": null,
  "errors": [
    {
      "code": "transcript_not_found",
      "message": "No transcript available for this video",
      "phase": "transcript",
      "retryable": false,
      "video_id": "abc12345678"
    }
  ],
  "content_hash": "a1b2c3d4e5f6...",
  "token_count": null,
  "fetched_at": "2026-03-09T16:30:00Z"
}
```

## Bundle Fields

| Field | Type | Description |
|-------|------|-------------|
| `video_id` | string | YouTube video ID |
| `metadata` | object \| null | Full metadata object with `content_hash` |
| `transcript` | object \| null | Full transcript object with `content_hash` and `token_count` |
| `errors` | array | List of errors encountered during fetch |
| `content_hash` | string | Combined hash of metadata + transcript |
| `token_count` | int \| null | Token count from transcript (if available) |
| `fetched_at` | string | ISO timestamp of bundle creation |

## Use Cases

### 1. Simplified RAG Ingestion

Read one file per video instead of multiple:

```python
import json
from pathlib import Path

def ingest_video_bundle(bundle_path: Path):
    """Ingest video bundle into RAG system."""
    with open(bundle_path) as f:
        bundle = json.load(f)
    
    # All data in one place
    video_id = bundle["video_id"]
    title = bundle["metadata"]["title"]
    description = bundle["metadata"]["description"]
    
    # Check for transcript
    if bundle["transcript"]:
        segments = bundle["transcript"]["segments"]
        text = " ".join(seg["text"] for seg in segments)
        token_count = bundle["token_count"]
        
        # Create embeddings and index
        chunks = create_chunks(text)
        embeddings = create_embeddings(chunks)
        
        index_video(
            video_id=video_id,
            title=title,
            chunks=chunks,
            embeddings=embeddings,
            content_hash=bundle["content_hash"],
            token_count=token_count
        )
    else:
        # Handle missing transcript
        errors = bundle["errors"]
        log_ingestion_failure(video_id, errors)
```

### 2. Batch Processing Pipeline

Process bundles in parallel:

```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json

def process_bundle(bundle_path: Path):
    """Process a single video bundle."""
    with open(bundle_path) as f:
        bundle = json.load(f)
    
    # Your processing logic
    result = analyze_video(bundle)
    return result

def process_all_bundles(out_dir: Path):
    """Process all video bundles in parallel."""
    bundle_paths = list(out_dir.glob("*/video_bundle.json"))
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_bundle, bundle_paths))
    
    return results
```

### 3. Error Handling

Easily identify and handle failures:

```python
import json
from pathlib import Path

def find_failed_videos(out_dir: Path):
    """Find videos with transcript errors."""
    failed = []
    
    for bundle_path in out_dir.glob("*/video_bundle.json"):
        with open(bundle_path) as f:
            bundle = json.load(f)
        
        # Check for transcript errors
        transcript_errors = [
            e for e in bundle["errors"]
            if e["phase"] == "transcript"
        ]
        
        if transcript_errors:
            failed.append({
                "video_id": bundle["video_id"],
                "title": bundle["metadata"]["title"],
                "errors": transcript_errors
            })
    
    return failed
```

### 4. Content Monitoring

Track changes using bundle hashes:

```python
import json
from pathlib import Path

def check_bundle_changes(video_id: str, out_dir: Path):
    """Check if bundle content has changed."""
    bundle_path = out_dir / video_id / "video_bundle.json"
    
    with open(bundle_path) as f:
        current = json.load(f)
    
    # Load previous hash from database
    previous_hash = get_previous_bundle_hash(video_id)
    current_hash = current["content_hash"]
    
    if previous_hash != current_hash:
        print(f"Content changed for {video_id}")
        
        # Check what changed
        if current["metadata"]["content_hash"] != get_previous_metadata_hash(video_id):
            print("  - Metadata changed")
        if current["transcript"] and current["transcript"]["content_hash"] != get_previous_transcript_hash(video_id):
            print("  - Transcript changed")
        
        return True
    return False
```

### 5. Data Export

Export bundles to other formats:

```python
import json
from pathlib import Path
import csv

def export_bundles_to_csv(out_dir: Path, output_csv: Path):
    """Export bundle metadata to CSV."""
    rows = []
    
    for bundle_path in out_dir.glob("*/video_bundle.json"):
        with open(bundle_path) as f:
            bundle = json.load(f)
        
        rows.append({
            "video_id": bundle["video_id"],
            "title": bundle["metadata"]["title"],
            "channel": bundle["metadata"]["channel_title"],
            "duration": bundle["metadata"]["duration_seconds"],
            "token_count": bundle["token_count"],
            "has_transcript": bundle["transcript"] is not None,
            "content_hash": bundle["content_hash"],
            "fetched_at": bundle["fetched_at"]
        })
    
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
```

## Bundle Hash

The bundle `content_hash` is computed from metadata and transcript hashes:

```python
from tubefetch.utils.hashing import hash_bundle

# Computed as:
# SHA-256(metadata.content_hash + transcript.content_hash)
bundle_hash = hash_bundle(metadata, transcript)
```

**Behavior:**
- If metadata is `None`, uses empty string
- If transcript is `None`, uses empty string
- Provides single hash for entire video content

## Output Location

Bundles are written to:

```
out/
└── <video_id>/
    ├── metadata.json
    ├── transcript.json
    ├── transcript.txt
    ├── video_bundle.json  ← Bundle file
    └── ...
```

## Performance Considerations

### Bundle Size

Bundles can be large if transcripts are long:

```python
import json
from pathlib import Path

def get_bundle_size(bundle_path: Path):
    """Get bundle file size in KB."""
    size_bytes = bundle_path.stat().st_size
    size_kb = size_bytes / 1024
    return size_kb

# Typical sizes:
# - 5-10 minute video: 20-50 KB
# - 30-60 minute video: 100-300 KB
# - 2-3 hour video: 500-1000 KB
```

### Storage Optimization

If storage is a concern, bundles are optional:

```bash
# Without bundles (saves ~30% storage)
tubefetch VIDEO_ID

# With bundles (convenience vs storage)
tubefetch VIDEO_ID --bundle
```

You can always reconstruct bundle data from individual files:

```python
import json
from pathlib import Path

def reconstruct_bundle(video_id: str, out_dir: Path):
    """Reconstruct bundle from individual files."""
    video_dir = out_dir / video_id
    
    # Load metadata
    with open(video_dir / "metadata.json") as f:
        metadata = json.load(f)
    
    # Load transcript
    transcript_path = video_dir / "transcript.json"
    if transcript_path.exists():
        with open(transcript_path) as f:
            transcript = json.load(f)
    else:
        transcript = None
    
    # Reconstruct bundle
    bundle = {
        "video_id": video_id,
        "metadata": metadata,
        "transcript": transcript,
        "errors": [],
        "content_hash": compute_bundle_hash(metadata, transcript),
        "token_count": transcript["token_count"] if transcript else None,
        "fetched_at": metadata["fetched_at"]
    }
    
    return bundle
```

## Library Usage

### Reading Bundles

```python
import json
from pathlib import Path
from tubefetch.core.models import VideoBundle

def load_bundle(video_id: str, out_dir: Path = Path("out")) -> VideoBundle:
    """Load and parse video bundle."""
    bundle_path = out_dir / video_id / "video_bundle.json"
    
    with open(bundle_path) as f:
        data = json.load(f)
    
    # Parse as Pydantic model
    bundle = VideoBundle(**data)
    return bundle
```

### Creating Bundles Programmatically

```python
from tubefetch import fetch_video, FetchOptions
from tubefetch.core.writer import write_bundle
from pathlib import Path

# Fetch video
result = fetch_video("dQw4w9WgXcQ")

# Write bundle manually
bundle_path = write_bundle(result, Path("out"))
print(f"Bundle written to {bundle_path}")
```

## Related Features

- **[Content Hashing](content-hashing.md)** — Bundle hash for change detection
- **[Token Counting](token-counting.md)** — Bundle includes token count
- **[Playlist Resolution](playlist-resolution.md)** — Create bundles for entire playlists
- **[LLM Text Formatting](llm-text-formatting.md)** — Transcript formatting in bundles

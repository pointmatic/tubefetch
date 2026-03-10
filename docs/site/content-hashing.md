# Content Hashing

TubeFetch computes SHA-256 content hashes for metadata and transcripts, enabling change detection and content monitoring workflows.

## Overview

Content hashes are automatically computed for:

- **Metadata** — Based on canonical fields (title, description, tags, etc.)
- **Transcripts** — Based on concatenated segment text
- **Bundles** — Combined hash of metadata + transcript

Hashes are **stable** — they only change when actual content changes, not when volatile fields like view counts update.

## Hash Fields

### Metadata Hash

Found in `metadata.json`:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Example Video",
  "content_hash": "a1b2c3d4e5f6...",
  ...
}
```

**Canonical fields used:**
- `title`
- `description`
- `tags` (sorted for consistency)
- `upload_date`
- `duration_seconds`
- `channel_title`
- `channel_id`

**Excluded fields:**
- `view_count` (volatile)
- `like_count` (volatile)
- `fetched_at` (timestamp)
- `raw` (implementation detail)

### Transcript Hash

Found in `transcript.json`:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "content_hash": "f6e5d4c3b2a1...",
  "segments": [...],
  ...
}
```

**Based on:**
- Concatenated text from all segments
- Segment order matters
- Whitespace normalized

### Bundle Hash

Found in `video_bundle.json` (with `--bundle`):

```json
{
  "video_id": "dQw4w9WgXcQ",
  "content_hash": "9876543210ab...",
  "metadata": {...},
  "transcript": {...},
  ...
}
```

**Computed from:**
- SHA-256 of `metadata.content_hash + transcript.content_hash`
- If either is missing, uses empty string

## Use Cases

### 1. Content Monitoring

Detect when videos are updated or re-uploaded:

```bash
# Initial fetch
tubefetch VIDEO_ID

# Later, check for changes
tubefetch VIDEO_ID --force

# Compare hashes
python check_changes.py
```

```python
import json
from pathlib import Path

def check_content_changed(video_id: str, out_dir: Path = Path("out")):
    """Check if content has changed since last fetch."""
    metadata_path = out_dir / video_id / "metadata.json"
    
    # Load current hash
    with open(metadata_path) as f:
        current = json.load(f)
    
    # Load previous hash (from database, cache, etc.)
    previous_hash = get_previous_hash(video_id)
    
    if current["content_hash"] != previous_hash:
        print(f"Content changed for {video_id}")
        return True
    return False
```

### 2. Deduplication

Identify duplicate or re-uploaded content:

```python
from collections import defaultdict
import json
from pathlib import Path

def find_duplicates(out_dir: Path = Path("out")):
    """Find videos with identical content."""
    hash_to_videos = defaultdict(list)
    
    for video_dir in out_dir.iterdir():
        if not video_dir.is_dir():
            continue
            
        metadata_path = video_dir / "metadata.json"
        if not metadata_path.exists():
            continue
            
        with open(metadata_path) as f:
            data = json.load(f)
            
        content_hash = data.get("content_hash")
        if content_hash:
            hash_to_videos[content_hash].append(data["video_id"])
    
    # Find duplicates
    duplicates = {h: vids for h, vids in hash_to_videos.items() if len(vids) > 1}
    return duplicates
```

### 3. Change Detection Pipeline

Monitor a channel for content updates:

```bash
#!/bin/bash
# monitor_channel.sh

CHANNEL_URL="https://www.youtube.com/@channelname"
OUT_DIR="./channel_archive"

# Resolve channel to video IDs
tubefetch --channel "$CHANNEL_URL" --max-videos 50 --out "$OUT_DIR"

# Check for changes
python detect_changes.py "$OUT_DIR"
```

```python
# detect_changes.py
import json
import sys
from pathlib import Path

def detect_changes(out_dir: Path):
    """Compare current hashes with stored hashes."""
    hash_db = load_hash_database()  # Your storage
    changes = []
    
    for video_dir in out_dir.iterdir():
        if not video_dir.is_dir():
            continue
            
        video_id = video_dir.name
        metadata_path = video_dir / "metadata.json"
        
        with open(metadata_path) as f:
            current = json.load(f)
        
        current_hash = current.get("content_hash")
        previous_hash = hash_db.get(video_id)
        
        if previous_hash and current_hash != previous_hash:
            changes.append({
                "video_id": video_id,
                "title": current["title"],
                "previous_hash": previous_hash,
                "current_hash": current_hash
            })
        
        # Update database
        hash_db[video_id] = current_hash
    
    save_hash_database(hash_db)
    return changes

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    changes = detect_changes(out_dir)
    
    if changes:
        print(f"Found {len(changes)} changed videos:")
        for change in changes:
            print(f"  - {change['title']} ({change['video_id']})")
    else:
        print("No changes detected")
```

### 4. RAG Index Updates

Only re-index content that has changed:

```python
from tubefetch import fetch_video, FetchOptions
from your_vector_db import VectorDB

def update_rag_index(video_id: str, db: VectorDB):
    """Update RAG index only if content changed."""
    opts = FetchOptions(force=True)
    result = fetch_video(video_id, opts)
    
    # Check if content changed
    stored_hash = db.get_content_hash(video_id)
    current_hash = result.metadata.content_hash
    
    if stored_hash == current_hash:
        print(f"Skipping {video_id} - no changes")
        return
    
    # Content changed, re-index
    print(f"Re-indexing {video_id}")
    chunks = create_chunks(result.transcript.segments)
    embeddings = create_embeddings(chunks)
    
    db.delete_video(video_id)  # Remove old entries
    db.insert_video(video_id, chunks, embeddings, current_hash)
```

## Hash Stability

### What Triggers Hash Changes

✅ **Will change hash:**
- Title edited
- Description updated
- Tags added/removed
- Transcript corrected
- Video re-uploaded with different content

❌ **Won't change hash:**
- View count increased
- Like count changed
- Comments added
- Thumbnail updated
- Metadata fetched at different time

### Tag Sorting

Tags are sorted alphabetically before hashing to ensure consistency:

```python
# These produce the same hash
tags_1 = ["python", "tutorial", "beginner"]
tags_2 = ["beginner", "python", "tutorial"]
```

## Library Usage

```python
from tubefetch import fetch_video
from tubefetch.utils.hashing import hash_metadata, hash_transcript, hash_bundle

result = fetch_video("dQw4w9WgXcQ")

# Hashes are automatically computed
print(f"Metadata hash: {result.metadata.content_hash}")
print(f"Transcript hash: {result.transcript.content_hash}")

# Manual hash computation
metadata_hash = hash_metadata(result.metadata)
transcript_hash = hash_transcript(result.transcript)
bundle_hash = hash_bundle(result.metadata, result.transcript)
```

## Technical Details

### Hash Algorithm

- **Algorithm**: SHA-256
- **Encoding**: Hexadecimal lowercase
- **Length**: 64 characters

### Canonical Serialization

Metadata fields are serialized in a consistent order:

```python
canonical_data = {
    "title": metadata.title,
    "description": metadata.description,
    "tags": sorted(metadata.tags or []),  # Sorted!
    "upload_date": metadata.upload_date,
    "duration_seconds": metadata.duration_seconds,
    "channel_title": metadata.channel_title,
    "channel_id": metadata.channel_id,
}
```

### Transcript Hashing

Segments are concatenated with spaces:

```python
text = " ".join(segment.text for segment in transcript.segments)
hash_value = hashlib.sha256(text.encode("utf-8")).hexdigest()
```

## Related Features

- **[Video Bundles](video-bundles.md)** — Bundle hash combines metadata + transcript
- **[Token Counting](token-counting.md)** — Track both content and cost
- **[Playlist Resolution](playlist-resolution.md)** — Monitor entire channels for changes

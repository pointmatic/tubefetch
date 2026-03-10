# Use Cases

Real-world examples of using TubeFetch for AI/LLM pipelines, content monitoring, and data analysis.

## RAG Pipeline Integration

Build a Retrieval-Augmented Generation system with YouTube content.

### Basic RAG Workflow

```python
from tubefetch import fetch_video, FetchOptions
from your_vector_db import VectorDB
from your_embedding_service import create_embeddings

def ingest_video_for_rag(video_id: str, db: VectorDB):
    """Ingest video into RAG system."""
    # Fetch with AI-ready features
    opts = FetchOptions(
        tokenizer="cl100k_base",
        bundle=True,
        txt_timestamps=True
    )
    result = fetch_video(video_id, opts)
    
    if not result.transcript:
        print(f"No transcript for {video_id}")
        return
    
    # Create chunks with metadata
    chunks = []
    for i, segment in enumerate(result.transcript.segments):
        chunks.append({
            "text": segment.text,
            "video_id": video_id,
            "title": result.metadata.title,
            "channel": result.metadata.channel_title,
            "timestamp": segment.start,
            "chunk_id": f"{video_id}_{i}"
        })
    
    # Create embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = create_embeddings(texts)
    
    # Store in vector database
    db.insert_batch(
        video_id=video_id,
        chunks=chunks,
        embeddings=embeddings,
        metadata={
            "content_hash": result.metadata.content_hash,
            "token_count": result.transcript.token_count
        }
    )
    
    print(f"Indexed {len(chunks)} chunks for {video_id}")
```

### Playlist RAG Ingestion

```python
from tubefetch import resolve_playlist, fetch_batch, FetchOptions
from pathlib import Path

def ingest_playlist_for_rag(playlist_url: str, db: VectorDB):
    """Ingest entire playlist into RAG system."""
    # Resolve playlist
    video_ids = resolve_playlist(playlist_url, max_videos=100)
    print(f"Found {len(video_ids)} videos")
    
    # Fetch with bundles
    opts = FetchOptions(
        bundle=True,
        tokenizer="cl100k_base",
        workers=5
    )
    results = fetch_batch(video_ids, opts)
    
    # Ingest each video
    for result in results.results:
        if result.success and result.transcript:
            ingest_video_for_rag(result.video_id, db)
    
    print(f"Ingested {results.succeeded}/{results.total} videos")
```

### Incremental Updates

```python
def update_rag_index(video_id: str, db: VectorDB):
    """Update RAG index only if content changed."""
    opts = FetchOptions(force=True, bundle=True, tokenizer="cl100k_base")
    result = fetch_video(video_id, opts)
    
    # Check if content changed
    stored_hash = db.get_content_hash(video_id)
    current_hash = result.metadata.content_hash
    
    if stored_hash == current_hash:
        print(f"No changes for {video_id}")
        return
    
    # Content changed, re-index
    print(f"Re-indexing {video_id}")
    db.delete_video(video_id)
    ingest_video_for_rag(video_id, db)
```

## Content Monitoring

Track changes in video content over time.

### Channel Monitoring

```python
from tubefetch import resolve_channel, fetch_video, FetchOptions
from pathlib import Path
import json
from datetime import datetime

class ChannelMonitor:
    def __init__(self, channel_url: str, db_path: Path):
        self.channel_url = channel_url
        self.db_path = db_path
        self.load_database()
    
    def load_database(self):
        """Load hash database."""
        if self.db_path.exists():
            with open(self.db_path) as f:
                self.db = json.load(f)
        else:
            self.db = {"videos": {}, "last_check": None}
    
    def save_database(self):
        """Save hash database."""
        self.db["last_check"] = datetime.now().isoformat()
        with open(self.db_path, "w") as f:
            json.dump(self.db, f, indent=2)
    
    def check_for_changes(self):
        """Check channel for content changes."""
        # Resolve channel
        video_ids = resolve_channel(self.channel_url, max_videos=50)
        
        changes = []
        new_videos = []
        
        opts = FetchOptions(force=True)
        
        for vid in video_ids:
            result = fetch_video(vid, opts)
            
            if not result.metadata:
                continue
            
            current_hash = result.metadata.content_hash
            previous_hash = self.db["videos"].get(vid, {}).get("content_hash")
            
            if previous_hash is None:
                # New video
                new_videos.append({
                    "video_id": vid,
                    "title": result.metadata.title,
                    "upload_date": result.metadata.upload_date
                })
            elif current_hash != previous_hash:
                # Content changed
                changes.append({
                    "video_id": vid,
                    "title": result.metadata.title,
                    "previous_hash": previous_hash,
                    "current_hash": current_hash
                })
            
            # Update database
            self.db["videos"][vid] = {
                "content_hash": current_hash,
                "title": result.metadata.title,
                "last_checked": datetime.now().isoformat()
            }
        
        self.save_database()
        
        return {
            "new_videos": new_videos,
            "changed_videos": changes
        }

# Usage
monitor = ChannelMonitor(
    "https://www.youtube.com/@channelname",
    Path("channel_monitor.json")
)

report = monitor.check_for_changes()
print(f"New videos: {len(report['new_videos'])}")
print(f"Changed videos: {len(report['changed_videos'])}")
```

### Automated Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Run daily via cron

CHANNEL="https://www.youtube.com/@channelname"
OUT_DIR="./monitoring/$(date +%Y%m%d)"
REPORT_EMAIL="alerts@example.com"

# Fetch latest videos
tubefetch --channel "$CHANNEL" --max-videos 20 --out "$OUT_DIR" --force

# Check for changes
python check_changes.py "$OUT_DIR" > changes.txt

# Send alert if changes detected
if [ -s changes.txt ]; then
    mail -s "Channel Update Detected" "$REPORT_EMAIL" < changes.txt
fi
```

## Batch Channel Analysis

Analyze content across an entire channel.

### Channel Statistics

```python
from tubefetch import resolve_channel, fetch_batch, FetchOptions
import json
from collections import Counter

def analyze_channel(channel_url: str):
    """Generate comprehensive channel statistics."""
    # Resolve channel
    video_ids = resolve_channel(channel_url)
    print(f"Analyzing {len(video_ids)} videos...")
    
    # Fetch with AI features
    opts = FetchOptions(
        bundle=True,
        tokenizer="cl100k_base",
        workers=10
    )
    results = fetch_batch(video_ids, opts)
    
    # Collect statistics
    stats = {
        "total_videos": len(video_ids),
        "successful_fetches": results.succeeded,
        "total_duration_hours": 0,
        "total_tokens": 0,
        "languages": Counter(),
        "tags": Counter(),
        "avg_duration": 0,
        "avg_tokens": 0,
    }
    
    for result in results.results:
        if not result.metadata:
            continue
        
        # Duration
        duration = result.metadata.duration_seconds or 0
        stats["total_duration_hours"] += duration / 3600
        
        # Tokens
        if result.transcript and result.transcript.token_count:
            stats["total_tokens"] += result.transcript.token_count
        
        # Languages
        if result.transcript:
            stats["languages"][result.transcript.language] += 1
        
        # Tags
        if result.metadata.tags:
            for tag in result.metadata.tags:
                stats["tags"][tag] += 1
    
    # Averages
    if results.succeeded > 0:
        stats["avg_duration"] = (stats["total_duration_hours"] * 3600) / results.succeeded
        stats["avg_tokens"] = stats["total_tokens"] / results.succeeded
    
    # Top tags
    stats["top_tags"] = stats["tags"].most_common(10)
    
    return stats

# Usage
stats = analyze_channel("https://www.youtube.com/@channelname")
print(json.dumps(stats, indent=2))
```

## Training Data Preparation

Prepare datasets for fine-tuning or training.

### Dataset Creation

```python
from tubefetch import resolve_playlist, fetch_batch, FetchOptions
from pathlib import Path
import json

def create_training_dataset(playlist_url: str, output_path: Path):
    """Create training dataset from playlist."""
    # Resolve playlist
    video_ids = resolve_playlist(playlist_url)
    
    # Fetch with raw text (maximum tokens)
    opts = FetchOptions(
        txt_raw=True,
        tokenizer="cl100k_base"
    )
    results = fetch_batch(video_ids, opts)
    
    # Create dataset
    dataset = []
    for result in results.results:
        if not result.transcript:
            continue
        
        # Read raw transcript text
        txt_path = Path(opts.out) / result.video_id / "transcript.txt"
        if not txt_path.exists():
            continue
        
        text = txt_path.read_text()
        
        dataset.append({
            "video_id": result.video_id,
            "title": result.metadata.title if result.metadata else None,
            "text": text,
            "token_count": result.transcript.token_count,
            "language": result.transcript.language
        })
    
    # Save dataset
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
    
    total_tokens = sum(item["token_count"] for item in dataset)
    print(f"Created dataset with {len(dataset)} videos ({total_tokens:,} tokens)")
    
    return dataset
```

## Fact-Checking Pipeline

Extract claims from videos for verification.

### Claim Extraction

```python
from tubefetch import fetch_video, FetchOptions
from your_llm_service import extract_claims

def extract_video_claims(video_id: str):
    """Extract factual claims from video."""
    # Fetch with timestamps for citation
    opts = FetchOptions(
        txt_timestamps=True,
        tokenizer="cl100k_base"
    )
    result = fetch_video(video_id, opts)
    
    if not result.transcript:
        return []
    
    # Read formatted transcript
    txt_path = Path(opts.out) / video_id / "transcript.txt"
    text = txt_path.read_text()
    
    # Extract claims using LLM
    claims = extract_claims(text)
    
    # Add metadata
    for claim in claims:
        claim["video_id"] = video_id
        claim["title"] = result.metadata.title
        claim["channel"] = result.metadata.channel_title
        claim["source_url"] = result.metadata.source_url
    
    return claims

# Usage
claims = extract_video_claims("dQw4w9WgXcQ")
for claim in claims:
    print(f"[{claim['timestamp']}] {claim['text']}")
```

## Cost Estimation

Estimate LLM processing costs before running pipelines.

### Batch Cost Estimation

```python
from tubefetch import resolve_playlist, fetch_video, FetchOptions

def estimate_playlist_cost(playlist_url: str, cost_per_1k_tokens: float = 0.03):
    """Estimate cost to process entire playlist."""
    # Resolve playlist
    video_ids = resolve_playlist(playlist_url)
    
    # Fetch with token counting (fast, no processing)
    opts = FetchOptions(tokenizer="cl100k_base")
    
    total_tokens = 0
    for vid in video_ids:
        result = fetch_video(vid, opts)
        if result.transcript and result.transcript.token_count:
            total_tokens += result.transcript.token_count
    
    # Estimate cost
    estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
    
    return {
        "video_count": len(video_ids),
        "total_tokens": total_tokens,
        "avg_tokens_per_video": total_tokens // len(video_ids),
        "estimated_cost": estimated_cost,
        "cost_per_video": estimated_cost / len(video_ids)
    }

# Usage
estimate = estimate_playlist_cost("https://www.youtube.com/playlist?list=PLxxx")
print(f"Estimated cost: ${estimate['estimated_cost']:.2f}")
print(f"Per video: ${estimate['cost_per_video']:.4f}")
```

## Best Practices

### 1. Use Bundles for Pipelines

```python
# ✅ Good: Single file read
opts = FetchOptions(bundle=True, tokenizer="cl100k_base")
result = fetch_video(vid, opts)
bundle_path = Path("out") / vid / "video_bundle.json"
# Process bundle...

# ❌ Avoid: Multiple file reads
metadata_path = Path("out") / vid / "metadata.json"
transcript_path = Path("out") / vid / "transcript.json"
# Read both files separately...
```

### 2. Enable Token Counting Early

```python
# ✅ Good: Count tokens during fetch
opts = FetchOptions(tokenizer="cl100k_base")
result = fetch_video(vid, opts)
cost = estimate_cost(result.transcript.token_count)

# ❌ Avoid: Count tokens later
result = fetch_video(vid)
# Have to re-read and count manually...
```

### 3. Use Content Hashing for Updates

```python
# ✅ Good: Check hash before re-processing
current_hash = get_current_hash(vid)
if current_hash != stored_hash:
    reprocess_video(vid)

# ❌ Avoid: Always re-process
reprocess_video(vid)  # Wasteful if unchanged
```

### 4. Limit Playlist Resolution

```python
# ✅ Good: Use max_videos for testing
video_ids = resolve_playlist(url, max_videos=10)

# ❌ Avoid: Fetch entire large playlist for testing
video_ids = resolve_playlist(url)  # Could be 1000+ videos
```

## Related Guides

- **[AI-Ready Features](ai-ready-features.md)** — Overview of all AI features
- **[LLM Text Formatting](llm-text-formatting.md)** — Optimize text for LLMs
- **[Content Hashing](content-hashing.md)** — Change detection workflows
- **[Token Counting](token-counting.md)** — Cost estimation
- **[Video Bundles](video-bundles.md)** — Unified output format

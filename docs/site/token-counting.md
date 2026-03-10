# Token Counting

TubeFetch provides optional token count estimation for transcripts using tiktoken, enabling LLM cost planning and optimization.

## Overview

Token counting helps you:

- **Estimate LLM costs** before processing
- **Optimize chunk sizes** for embeddings
- **Plan batch operations** within token budgets
- **Track content size** for different models

Token counts are computed using OpenAI's `tiktoken` library and stored in `transcript.json` and `video_bundle.json`.

## Installation

Token counting requires the optional `tokens` dependency:

```bash
pip install 'tubefetch[tokens]'
```

Without this dependency, the `--tokenizer` flag will log a warning and skip token counting.

## Basic Usage

### CLI

```bash
# Count tokens with cl100k_base (GPT-4, GPT-3.5-turbo)
tubefetch VIDEO_ID --tokenizer cl100k_base

# Count tokens for multiple videos
tubefetch --file videos.txt --tokenizer cl100k_base

# Combine with other features
tubefetch VIDEO_ID --tokenizer cl100k_base --bundle
```

### Library

```python
from tubefetch import fetch_video, FetchOptions

opts = FetchOptions(tokenizer="cl100k_base")
result = fetch_video("dQw4w9WgXcQ", opts)

print(f"Token count: {result.transcript.token_count}")
```

## Supported Tokenizers

| Tokenizer | Models | Use Case |
|-----------|--------|----------|
| `cl100k_base` | GPT-4, GPT-3.5-turbo, text-embedding-ada-002 | Most common (recommended) |
| `p50k_base` | Codex, text-davinci-002, text-davinci-003 | Legacy models |
| `r50k_base` | GPT-3 (davinci, curie, babbage, ada) | Older GPT-3 models |
| `gpt2` | GPT-2 | Research/compatibility |

**Recommendation**: Use `cl100k_base` for modern OpenAI models and embeddings.

## Output

### transcript.json

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "token_count": 1523,
  "segments": [...],
  ...
}
```

### video_bundle.json

```json
{
  "video_id": "dQw4w9WgXcQ",
  "token_count": 1523,
  "metadata": {...},
  "transcript": {...},
  ...
}
```

## Cost Estimation

### Example: GPT-4 Processing

```python
from tubefetch import fetch_video, FetchOptions

opts = FetchOptions(tokenizer="cl100k_base")
result = fetch_video("dQw4w9WgXcQ", opts)

token_count = result.transcript.token_count

# GPT-4 pricing (example rates)
input_cost_per_1k = 0.03  # $0.03 per 1K tokens
output_cost_per_1k = 0.06  # $0.06 per 1K tokens

# Estimate input cost
input_cost = (token_count / 1000) * input_cost_per_1k

# Assume 2:1 compression for summary
output_tokens = token_count / 2
output_cost = (output_tokens / 1000) * output_cost_per_1k

total_cost = input_cost + output_cost
print(f"Estimated cost: ${total_cost:.4f}")
```

### Batch Cost Estimation

```python
from tubefetch import fetch_batch, FetchOptions
from pathlib import Path
import json

opts = FetchOptions(tokenizer="cl100k_base")
results = fetch_batch(["vid1", "vid2", "vid3"], opts)

total_tokens = 0
for result in results.results:
    if result.transcript and result.transcript.token_count:
        total_tokens += result.transcript.token_count

# Estimate embedding cost (text-embedding-ada-002)
embedding_cost_per_1k = 0.0001  # $0.0001 per 1K tokens
total_cost = (total_tokens / 1000) * embedding_cost_per_1k

print(f"Total tokens: {total_tokens:,}")
print(f"Estimated embedding cost: ${total_cost:.4f}")
```

## Graceful Degradation

If `tiktoken` is not installed:

```bash
$ tubefetch VIDEO_ID --tokenizer cl100k_base
WARNING: tiktoken not installed, skipping token count estimation
```

The fetch will continue normally, but `token_count` will be `None`:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "token_count": null,
  ...
}
```

## Use Cases

### 1. RAG Pipeline Optimization

Determine optimal chunk sizes for embeddings:

```python
from tubefetch import fetch_video, FetchOptions

opts = FetchOptions(tokenizer="cl100k_base")
result = fetch_video("dQw4w9WgXcQ", opts)

# Target: 512 tokens per chunk
target_chunk_size = 512
num_chunks = result.transcript.token_count // target_chunk_size

print(f"Recommended chunks: {num_chunks}")
```

### 2. Batch Budget Planning

Stay within token budgets:

```python
from tubefetch import resolve_playlist, fetch_video, FetchOptions

# Get video IDs
video_ids = resolve_playlist("https://www.youtube.com/playlist?list=PLxxx")

# Estimate tokens
opts = FetchOptions(tokenizer="cl100k_base")
total_tokens = 0
max_budget = 1_000_000  # 1M token budget

selected_videos = []
for vid in video_ids:
    result = fetch_video(vid, opts)
    if result.transcript and result.transcript.token_count:
        if total_tokens + result.transcript.token_count <= max_budget:
            total_tokens += result.transcript.token_count
            selected_videos.append(vid)
        else:
            break

print(f"Selected {len(selected_videos)} videos ({total_tokens:,} tokens)")
```

### 3. Cost Tracking

Track LLM costs over time:

```python
import json
from pathlib import Path
from datetime import datetime

def track_token_usage(out_dir: Path = Path("out")):
    """Track total token usage across all fetched videos."""
    usage_log = []
    
    for video_dir in out_dir.iterdir():
        if not video_dir.is_dir():
            continue
            
        transcript_path = video_dir / "transcript.json"
        if not transcript_path.exists():
            continue
            
        with open(transcript_path) as f:
            data = json.load(f)
        
        if data.get("token_count"):
            usage_log.append({
                "video_id": data["video_id"],
                "token_count": data["token_count"],
                "fetched_at": data["fetched_at"],
            })
    
    total_tokens = sum(entry["token_count"] for entry in usage_log)
    
    # Save usage report
    report = {
        "total_tokens": total_tokens,
        "video_count": len(usage_log),
        "generated_at": datetime.now().isoformat(),
        "videos": usage_log
    }
    
    with open(out_dir / "token_usage_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return report
```

## Technical Details

### Token Counting Method

tubefetch uses tiktoken's encoding:

```python
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
text = " ".join(segment.text for segment in transcript.segments)
token_count = len(encoding.encode(text))
```

### Text Preparation

- Segments are joined with single spaces
- No additional preprocessing
- Counts tokens in the formatted text that would be sent to the LLM

### Accuracy

Token counts are **estimates**:

- ✅ Accurate for the transcript text itself
- ⚠️ Doesn't include system prompts, formatting, or chat structure
- ⚠️ Actual API usage may vary slightly

For precise billing, always check actual API usage.

## Configuration

### Environment Variable

```bash
export TUBEFETCH_TOKENIZER="cl100k_base"
tubefetch VIDEO_ID  # Uses cl100k_base automatically
```

### YAML Config

```yaml
# tubefetch.yaml
tokenizer: cl100k_base
```

### Programmatic

```python
from tubefetch import FetchOptions

opts = FetchOptions(tokenizer="cl100k_base")
```

## Related Features

- **[LLM Text Formatting](llm-text-formatting.md)** — Optimize text for token efficiency
- **[Video Bundles](video-bundles.md)** — Bundle includes token count
- **[Content Hashing](content-hashing.md)** — Track content changes and re-count tokens
- **[Playlist Resolution](playlist-resolution.md)** — Estimate costs for entire playlists

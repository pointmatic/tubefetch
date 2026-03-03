# Usage

Comprehensive guide to using yt-fetch from the command line.

## CLI Commands

### fetch

Fetch metadata, transcripts, and optionally media for YouTube videos.

```bash
yt_fetch fetch [OPTIONS]
```

### Common Options

#### Input Sources

```bash
# Single video by ID
yt_fetch fetch --id VIDEO_ID

# Multiple videos
yt_fetch fetch --id ID1 --id ID2 --id ID3

# From a text file (one ID per line)
yt_fetch fetch --file video_ids.txt

# From a JSONL file
yt_fetch fetch --jsonl input.jsonl --id-field video_id
```

#### Output Options

```bash
# Custom output directory
yt_fetch fetch --id VIDEO_ID --out ./my-output

# Force re-fetch (ignore cache)
yt_fetch fetch --id VIDEO_ID --force

# Selective force
yt_fetch fetch --id VIDEO_ID --force-metadata
yt_fetch fetch --id VIDEO_ID --force-transcript
```

#### Transcript Options

```bash
# Specify language preferences
yt_fetch fetch --id VIDEO_ID --languages en,en-US,es

# Allow auto-generated transcripts
yt_fetch fetch --id VIDEO_ID --allow-generated

# Allow any language as fallback
yt_fetch fetch --id VIDEO_ID --allow-any-language
```

#### Media Download

```bash
# Download video only
yt_fetch fetch --id VIDEO_ID --download video

# Download audio only
yt_fetch fetch --id VIDEO_ID --download audio

# Download both
yt_fetch fetch --id VIDEO_ID --download both

# Specify max resolution
yt_fetch fetch --id VIDEO_ID --download video --max-height 720
```

#### Retry and Rate Limiting

```bash
# Configure retries
yt_fetch fetch --id VIDEO_ID --retries 5

# Disable retries
yt_fetch fetch --id VIDEO_ID --retries 0

# Set rate limit (requests per second)
yt_fetch fetch --id VIDEO_ID --rate-limit 2
```

#### Error Handling

```bash
# Fail fast (stop on first error)
yt_fetch fetch --file ids.txt --fail-fast

# Verbose output
yt_fetch fetch --id VIDEO_ID --verbose
```

## Examples

### Basic Fetch

```bash
yt_fetch fetch --id dQw4w9WgXcQ
```

### Batch Processing

```bash
yt_fetch fetch --file video_ids.txt --out ./batch-output --verbose
```

### High-Quality Media Download

```bash
yt_fetch fetch --id VIDEO_ID \
  --download both \
  --max-height 1080 \
  --format mp4 \
  --audio-format m4a
```

### Multi-Language Transcript

```bash
yt_fetch fetch --id VIDEO_ID \
  --languages es,en \
  --allow-generated \
  --allow-any-language
```

## Exit Codes

- `0` - Success (even if some videos failed without `--fail-fast`)
- `1` - Generic error (bad arguments, initialization failure)
- `2` - Partial failure with `--strict` mode
- `3` - All videos failed

## Next Steps

- Check the [API Reference](api.md) for library usage
- Explore [Advanced](advanced.md) features

# Usage

Comprehensive guide to using TubeFetch from the command line.

## CLI Commands

### fetch

Fetch metadata, transcripts, and optionally media for YouTube videos.

```bash
tubefetch fetch [OPTIONS]
```

### Common Options

#### Input Sources

```bash
# Single video by ID
tubefetch fetch --id VIDEO_ID

# Multiple videos
tubefetch fetch --id ID1 --id ID2 --id ID3

# From a text file (one ID per line)
tubefetch fetch --file video_ids.txt

# From a JSONL file
tubefetch fetch --jsonl input.jsonl --id-field video_id
```

#### Output Options

```bash
# Custom output directory
tubefetch fetch --id VIDEO_ID --out ./my-output

# Force re-fetch (ignore cache)
tubefetch fetch --id VIDEO_ID --force

# Selective force
tubefetch fetch --id VIDEO_ID --force-metadata
tubefetch fetch --id VIDEO_ID --force-transcript
```

#### Transcript Options

```bash
# Specify language preferences
tubefetch fetch --id VIDEO_ID --languages en,en-US,es

# Allow auto-generated transcripts
tubefetch fetch --id VIDEO_ID --allow-generated

# Allow any language as fallback
tubefetch fetch --id VIDEO_ID --allow-any-language
```

#### Media Download

```bash
# Download video only
tubefetch fetch --id VIDEO_ID --download video

# Download audio only
tubefetch fetch --id VIDEO_ID --download audio

# Download both
tubefetch fetch --id VIDEO_ID --download both

# Specify max resolution
tubefetch fetch --id VIDEO_ID --download video --max-height 720
```

#### Retry and Rate Limiting

```bash
# Configure retries
tubefetch fetch --id VIDEO_ID --retries 5

# Disable retries
tubefetch fetch --id VIDEO_ID --retries 0

# Set rate limit (requests per second)
tubefetch fetch --id VIDEO_ID --rate-limit 2
```

#### Error Handling

```bash
# Fail fast (stop on first error)
tubefetch fetch --file ids.txt --fail-fast

# Verbose output
tubefetch fetch --id VIDEO_ID --verbose
```

## Examples

### Basic Fetch

```bash
tubefetch fetch --id dQw4w9WgXcQ
```

### Batch Processing

```bash
tubefetch fetch --file video_ids.txt --out ./batch-output --verbose
```

### High-Quality Media Download

```bash
tubefetch fetch --id VIDEO_ID \
  --download both \
  --max-height 1080 \
  --format mp4 \
  --audio-format m4a
```

### Multi-Language Transcript

```bash
tubefetch fetch --id VIDEO_ID \
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

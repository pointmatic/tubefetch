# Getting Started

Welcome to yt-fetch! This guide will help you get started with fetching YouTube video metadata and transcripts.

## Installation

Install yt-fetch using pip:

```bash
pip install tubefetch
```

For YouTube Data API v3 support (optional):

```bash
pip install tubefetch[youtube-api]
```

## Prerequisites

- Python 3.14 or higher
- Internet connection
- YouTube video IDs or URLs

## Quick Start

### Fetch a Single Video

```bash
yt_fetch fetch --id dQw4w9WgXcQ
```

This will create an output directory with:
- `metadata.json` - Video metadata
- `transcript.json` - Structured transcript
- `transcript.txt` - Plain text transcript

### Fetch Multiple Videos

```bash
yt_fetch fetch --id VIDEO_ID_1 --id VIDEO_ID_2 --id VIDEO_ID_3
```

### From a File

Create a text file with one video ID per line:

```bash
yt_fetch fetch --file video_ids.txt
```

## Next Steps

- Learn about [Usage](usage.md) options and commands
- Explore the [API Reference](api.md) for library usage
- Check out [Advanced](advanced.md) features

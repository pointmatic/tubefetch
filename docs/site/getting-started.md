# Getting Started

Welcome to tubefetch! This guide will help you get started with fetching YouTube video metadata and transcripts.

## Installation

Install tubefetch using pip:

```bash
pip install tubefetch
```

!!! tip "YouTube Data API Support"
    For enhanced metadata fetching and access to age-restricted videos, install the optional YouTube Data API v3 support:
    
    ```bash
    pip install 'tubefetch[youtube-api]'
    ```
    
    See the [Troubleshooting Guide](troubleshooting.md#this-video-is-not-available-errors) for setup instructions.

## Prerequisites

!!! info "Requirements"
    - Python 3.14 or higher
    - Internet connection
    - YouTube video IDs or URLs
    - (Optional) ffmpeg for media downloads

## Quick Start

### Fetch a Single Video

```bash
tubefetch dQw4w9WgXcQ
```

This will create an output directory with:
- `metadata.json` - Video metadata (title, channel, duration, etc.)
- `transcript.json` - Structured transcript with timestamps
- `transcript.txt` - Plain text transcript optimized for LLM processing
- `transcript.vtt` - WebVTT subtitle format
- `transcript.srt` - SubRip subtitle format

### Fetch Multiple Videos

```bash
tubefetch VIDEO_ID_1 VIDEO_ID_2 VIDEO_ID_3
```

### From a File

Create a text file with one video ID per line:

```bash
tubefetch --file video_ids.txt
```

## Next Steps

!!! success "Ready to Learn More?"
    - **[Usage Guide](usage.md)** - Comprehensive CLI options and commands
    - **[API Reference](api.md)** - Use TubeFetch as a Python library
    - **[Advanced Features](advanced.md)** - Retry logic, caching, and configuration
    - **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

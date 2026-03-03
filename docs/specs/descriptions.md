# descriptions.md — yt-fetch

Canonical source of truth for all descriptive language used across the project. All consumer files (README.md, docs/index.html, pyproject.toml, features.md) should draw from these definitions.

---

## Name

- yt-fetch (GitHub)
- yt-fetch (PyPI)

## Tagline

Fetch AI-ready YouTube content

## Long Tagline

Extract AI-ready YouTube content: metadata, transcripts, and media in structured formats.

## One-liner

Fetch structured, AI-ready content from YouTube videos.

### Friendly Brief Description (follows one-liner)

yt-fetch fetches and extracts metadata, transcripts, and media from YouTube videos in formats optimized for AI/LLM pipelines — with batch processing, caching, retries, and rate limiting.

## Two-clause Technical Description

A Python CLI and library that fetches and extracts structured metadata and transcripts from YouTube videos, producing LLM-ready plain text, content hashes for change detection, and unified video bundles with batch processing, caching, and retry logic.

## Benefits

- **Metadata** — title, channel, duration, tags, upload date via yt-dlp (or YouTube Data API v3)
- **Transcripts** — fetched via youtube-transcript-api with language preference and fallback
- **Media** — optional video/audio download via yt-dlp
- **Export formats** — JSON, plain text, WebVTT (.vtt), SubRip (.srt)
- **Batch processing** — concurrent workers with per-video error isolation
- **Caching** — skip already-fetched data; selective `--force` overrides
- **Retry** — powered by gentlify with exponential backoff and jitter on transient errors
- **Rate limiting** — token bucket algorithm, shared across workers
- **CLI + Library** — use from the command line or import as a Python package

## Technical Description

yt-fetch is a Python tool that extracts structured, AI-ready content from YouTube videos. Given one or more video IDs, URLs, playlists, or channels, it produces normalized metadata, transcripts, and optional media in formats optimized for downstream AI/LLM pipelines (summarization, fact-checking, RAG, search indexing, etc.). It provides content hashes for change detection, optional token count estimates, and unified video bundles. The tool supports both CLI and library usage with batch processing, intelligent caching, configurable retries via gentlify, and rate limiting.

## Keywords

`youtube`, `transcript`, `metadata`, `yt-dlp`, `video`, `ai`, `llm`, `content-extraction`, `batch-processing`, `cli`, `python`, `async`, `rate-limiting`, `retry`, `gentlify`

---

## Feature Cards

Short blurbs for landing pages and feature grids. Each card has a title and a one-to-two sentence description.

| # | Title | Description |
|---|-------|-------------|
| 1 | Structured Metadata | Extract title, channel, duration, tags, and upload date via yt-dlp or YouTube Data API v3. |
| 2 | Multi-Format Transcripts | Fetch transcripts with language preference and fallback, export as JSON, plain text, WebVTT, or SubRip. |
| 3 | LLM-Ready Output | Produce plain text transcripts optimized for AI pipelines with content hashes and optional token counts. |
| 4 | Batch Processing | Process multiple videos concurrently with per-video error isolation and progress tracking. |
| 5 | Intelligent Caching | Skip already-fetched data automatically; use `--force` for selective re-fetching. |
| 6 | Resilient Retry Logic | Powered by gentlify with exponential backoff, jitter, and smart classification of transient vs. permanent errors. |
| 7 | Rate Limiting | Token bucket algorithm shared across workers prevents API throttling and service errors. |
| 8 | Dual Interface | Use as a CLI tool for quick extraction or import as a Python library for programmatic workflows. |

---

## Usage Notes

| File | Which descriptions to use |
|------|--------------------------|
| `README.md` line 7 | Two-clause Technical Description |
| `README.md` line 13 | Benefits (inline) |
| `README.md` line 11 | Technical Description |
| `docs/index.html` hero `<h1>` | One-liner |
| `docs/index.html` hero `<p>` | Friendly Brief Description |
| `docs/index.html` feature grid | Feature Cards |
| `docs/specs/features.md` line 1 | One-liner + Long Tagline |
| (GitHub Repository) | One-liner + ":" + Long Tagline |
# stories.md — YouTube Fetch + Transcript Collector (Python)

This is a detailed breakdown of the step-by-step stories (tasks) with detailed checklists that can be completed independently. Stories are organized by phase (identified A, B, C and reference modules defined in `tech_spec.md`).

Each story is numbered (e.g. A.a, A.b, etc. according to the phase), followed by an application version number (e.g. v0.0.1) that will be bumped in the app when the story is completed. Stories that have no code changes will have no version number and no bump. Story titles are suffixed with [Planned] initially and [Done] when completed.

---

## Phase A: Foundation

### Story A.a: v0.0.1 Hello World [Done]

Minimal runnable package with CLI entry point.

- [x] Create `pyproject.toml` with project metadata and dependencies (see tech_spec.md)
- [x] Create `yt_fetch/__init__.py` with `__version__`
- [x] Create `yt_fetch/__main__.py` for `python -m yt_fetch` support
- [x] Create `yt_fetch/cli.py` with a Click group and a `--version` flag
- [x] Verify: `python -m yt_fetch --version` prints version and exits

### Story A.b: v0.0.2 Project Structure [Done]

Full package layout per tech_spec.md.

- [x] Create all package directories: `yt_fetch/core/`, `yt_fetch/services/`, `yt_fetch/utils/`
- [x] Create all `__init__.py` files
- [x] Create `tests/` directory with `conftest.py`
- [x] Create `tests/integration/` directory
- [x] Verify: package imports work (`from yt_fetch.core import models`)

### Story A.c: v0.0.3 Core Models and Options [Done]

Pydantic data models and settings.

- [x] Implement `yt_fetch/core/models.py`:
  - [x] `Metadata` model with all fields per tech_spec.md
  - [x] `TranscriptSegment` model
  - [x] `Transcript` model
  - [x] `FetchResult` model
  - [x] `BatchResult` model
- [x] Implement `yt_fetch/core/options.py`:
  - [x] `FetchOptions` Pydantic `BaseSettings` with all fields per tech_spec.md
  - [x] Environment variable prefix `YT_FETCH_`
  - [x] YAML config file support (`yt_fetch.yaml`)
- [x] Write `tests/test_models.py`:
  - [x] Validation tests for each model
  - [x] Serialization round-trip tests
  - [x] Default values tests for `FetchOptions`

### Story A.d: v0.0.4 Configuration System [Done]

CLI flags, env vars, and YAML config file integration.

- [x] Wire `FetchOptions` into `cli.py` Click commands
- [x] Implement config precedence: CLI flags → env vars → YAML → defaults
- [x] Create a sample `yt_fetch.yaml.example` file
- [x] Verify: CLI flag overrides env var overrides YAML overrides default

### Story A.e: v0.0.5 Logging Framework [Done]

Console and structured JSONL logging.

- [x] Implement `yt_fetch/core/logging.py`:
  - [x] Console logger using `rich` (concise by default, verbose with `--verbose`)
  - [x] Structured JSONL logger with fields: `timestamp`, `level`, `video_id`, `event`, `details`, `error`
- [x] Wire logging into CLI (respect `--verbose` flag)
- [x] Verify: console output is clean; JSONL output is valid JSON per line

---

## Phase B: Core Services

### Story B.a: v0.1.0 Video ID Parsing and Validation [Done]

- [x] Implement `yt_fetch/services/id_parser.py`:
  - [x] `parse_video_id(input_str) -> str | None` — extract ID from URL or raw string
  - [x] `parse_many(inputs) -> list[str]` — parse, deduplicate, preserve order
  - [x] `load_ids_from_file(path) -> list[str]` — load from text, CSV, or JSONL
- [x] Supported URL patterns:
  - [x] `https://www.youtube.com/watch?v=<id>`
  - [x] `https://youtu.be/<id>`
  - [x] `https://www.youtube.com/shorts/<id>`
  - [x] URLs with extra query parameters
  - [x] Raw 11-character IDs
- [x] Validation: 11 chars, alphanumeric + `-` + `_`
- [x] Write `tests/test_id_parser.py`:
  - [x] All URL forms
  - [x] Raw IDs
  - [x] Invalid inputs return `None`
  - [x] Deduplication preserves order
  - [x] File loading (text, CSV, JSONL)

### Story B.b: v0.1.1 Metadata Retrieval (yt-dlp) [Done]

- [x] Implement `yt_fetch/services/metadata.py`:
  - [x] `get_metadata(video_id, options) -> Metadata`
  - [x] `_yt_dlp_backend(video_id) -> dict` — extract metadata via yt-dlp
- [x] Map yt-dlp raw output to `Metadata` model fields
- [x] Store raw payload in `Metadata.raw`
- [x] Handle errors: video not found, private video, network failure
- [x] Write unit tests with mocked yt-dlp responses

### Story B.c: v0.1.2 Metadata Retrieval (YouTube Data API v3, optional) [Done]

- [x] Implement `_youtube_api_backend(video_id, api_key) -> dict` in `metadata.py`
- [x] Add `google-api-python-client` as optional dependency
- [x] Implement automatic fallback to yt-dlp backend on API failure
- [x] Guard behind `yt_api_key` option — skip if not configured
- [x] Write unit tests with mocked API responses

### Story B.d: v0.1.3 Transcript Fetching [Done]

- [x] Implement `yt_fetch/services/transcript.py`:
  - [x] `get_transcript(video_id, options) -> Transcript`
  - [x] `list_available_transcripts(video_id) -> list[TranscriptInfo]`
- [x] Language selection algorithm:
  - [x] Try preferred languages in order
  - [x] Prefer manual over generated (when `allow_generated` is false)
  - [x] Fall back to any language (when `allow_any_language` is true)
  - [x] Return structured `TRANSCRIPT_NOT_FOUND` error when none available
- [x] Edge cases:
  - [x] Video has no transcript
  - [x] Transcripts blocked by region/permissions
  - [x] Multiple language variants
- [x] Write unit tests with mocked `youtube-transcript-api` responses

### Story B.e: v0.1.4 Media Download [Done]

- [x] Implement `yt_fetch/services/media.py`:
  - [x] `download_media(video_id, options, out_dir) -> MediaResult`
  - [x] `check_ffmpeg() -> bool`
- [x] Implement `yt_fetch/utils/ffmpeg.py` — ffmpeg detection helper
- [x] Download modes: `none`, `video`, `audio`, `both`
- [x] Respect `max_height` and format preferences
- [x] Handle missing ffmpeg: error or skip based on `ffmpeg_fallback` option
- [x] Write unit tests with mocked yt-dlp download calls

---

## Phase 3: Pipeline & Orchestration

### Story C.a: v0.2.0 Per-Video Pipeline [Done]

- [x] Implement `yt_fetch/core/pipeline.py`:
  - [x] `process_video(video_id, options) -> FetchResult`
- [x] Workflow steps:
  - [x] Create output folder `<out_dir>/<video_id>/`
  - [x] Check cache — skip steps where output exists (unless `--force*`)
  - [x] Fetch metadata → pass to writer
  - [x] Fetch transcript → pass to writer
  - [x] Download media (if enabled) → write to `media/` subfolder
  - [x] Return structured `FetchResult`
- [x] Write `tests/test_pipeline.py` with mocked services

### Story C.b: v0.2.1 Output File Writing [Done]

- [x] Implement `yt_fetch/core/writer.py`:
  - [x] `write_metadata(metadata, out_dir) -> Path`
  - [x] `write_transcript_json(transcript, out_dir) -> Path`
  - [x] `write_transcript_txt(transcript, out_dir) -> Path` — plain text, no timestamps
  - [x] `write_transcript_vtt(transcript, out_dir) -> Path`
  - [x] `write_transcript_srt(transcript, out_dir) -> Path`
  - [x] `write_summary(results, out_dir) -> Path`
- [x] Implement `yt_fetch/utils/time_fmt.py` — VTT/SRT timestamp formatting
- [x] All writes are atomic: write to `.tmp`, then `os.rename()`
- [x] Write `tests/test_writer.py`:
  - [x] Verify JSON output structure
  - [x] Verify transcript.txt has no timestamps
  - [x] Verify VTT/SRT timestamp formatting correctness
- [x] Write `tests/test_transcript_format.py` for timestamp edge cases

### Story C.c: v0.2.2 Caching and Idempotency [Done]

- [x] Before each pipeline step, check if output file exists
- [x] If exists and no `--force*` flag: skip that step, log skip
- [x] Selective force: `--force-metadata`, `--force-transcript`, `--force-media`
- [x] `--force` overrides all selective flags
- [x] Write idempotency tests:
  - [x] Re-run without `--force` skips work
  - [x] Re-run with `--force` overwrites

### Story C.d: v0.2.3 Batch Processing with Concurrency [Done]

- [x] Implement `process_batch(video_ids, options) -> BatchResult` in `pipeline.py`
- [x] Use `asyncio` with semaphore for concurrency (`--workers N`, default 3)
- [x] Per-video error isolation: one failure does not stop the batch
- [x] `--fail-fast` mode: stop on first error
- [x] Write batch tests:
  - [x] Mixed valid/invalid IDs
  - [x] Error isolation
  - [x] Fail-fast behavior

### Story C.e: v0.2.4 Error Handling and Retry [Done]

- [x] Implement `yt_fetch/utils/retry.py`:
  - [x] Exponential backoff with jitter (base 1s, multiplier 2x, jitter ±25%)
  - [x] Configurable max retries (default 3)
  - [x] Applies to network errors, HTTP 429/5xx
- [x] Apply retry decorator to metadata, transcript, and media service calls
- [x] Write retry tests with simulated failures

### Story C.f: v0.2.5 Rate Limiting [Done]

- [x] Implement `yt_fetch/utils/rate_limit.py`:
  - [x] Token bucket algorithm
  - [x] Configurable rate (default 2 RPS)
  - [x] Thread-safe, shared across all workers
- [x] Integrate rate limiter into pipeline before each external call
- [x] Write rate limiter unit tests

### Story C.g: v0.2.6 Summary Reporting [Done]

- [x] At end of batch run, print summary to console:
  - [x] Total IDs processed, successes, failures
  - [x] Transcript successes/failures
  - [x] Media downloads
  - [x] Output directory path
- [x] Optionally write `out/summary.json` with list of results and status
- [x] Write summary output tests

---

## Phase 4: CLI & Library API

### Story D.a: v0.3.0 CLI Subcommands [Done]

- [x] Implement Click subcommands in `yt_fetch/cli.py`:
  - [x] `yt_fetch fetch` — full pipeline (metadata + transcript + media)
  - [x] `yt_fetch transcript` — transcript only
  - [x] `yt_fetch metadata` — metadata only
  - [x] `yt_fetch media` — media download only
- [x] Shared input flags: `--id`, `--file`, `--jsonl` + `--id-field`
- [x] All option flags per features.md (--out, --languages, --download, etc.)
- [x] Exit codes: 0 (success), 1 (generic error), 2 (partial failure + --strict), 3 (all failed)
- [x] Write `tests/test_cli.py` — smoke tests for each subcommand

### Story D.b: v0.3.1 Library API [Done]

- [x] Export public API from `yt_fetch/__init__.py`:
  - [x] `fetch_video(video_id, options) -> FetchResult`
  - [x] `fetch_batch(video_ids, options) -> BatchResult`
- [x] Ensure library usage does not require CLI context
- [x] Write library API tests

---

## Phase E: Testing & Quality

### Story E.a: v0.4.0 Unit Test Suite [Done]

- [x] Ensure all unit tests pass: ID parsing, models, transcript formatting, writer, rate limiter
- [x] Achieve meaningful coverage across core modules (96% overall)
- [x] All tests run without network access

### Story E.b: v0.4.1 Integration Tests [Done]

- [x] Implement `tests/integration/test_fetch_live.py`:
  - [x] Fetch metadata for a known public video
  - [x] Fetch transcript for a known public video
  - [x] Full pipeline end-to-end
  - [x] Batch with mixed valid/invalid IDs
- [x] Guard all integration tests behind `RUN_INTEGRATION=1` env var

### Story E.c: v0.4.2 Pipeline and Error Tests [Done]

- [x] Idempotency: verify skip behavior and force overwrite
- [x] Error isolation: one bad ID doesn't crash batch
- [x] Fail-fast: verify early termination
- [x] Retry: verify backoff on transient failures

---

## Phase F: Documentation & Release

### Story F.a: README and Documentation [Done]

- [x] Create `README.md` with:
  - [x] Project description and features
  - [x] Installation instructions
  - [x] Quick start / usage examples
  - [x] Configuration reference
  - [x] Library API usage
- [x] Create `CHANGELOG.md`

### Story F.b: v0.5.0 Final Testing and Refinement [Done]

- [x] Run full test suite (unit + integration)
- [x] Fix any remaining bugs
- [x] Review and clean up code
- [x] Verify acceptance criteria from features.md:
  - [x] `yt_fetch fetch --id dQw4w9WgXcQ` produces metadata + transcript
  - [x] Batch mode with summary and per-video isolation
  - [x] Re-run without `--force` skips completed work
  - [x] Transcript exports (.txt, .json, .vtt, .srt) are correct
  - [x] Errors are structured and do not crash the run

### Story F.c: v0.5.1 Hyphen or Underscore CLI Command [Done]

- [x] Ensure `yt_fetch` and `yt-fetch` both work
- [x] Correct license and add copyright/license headers to all files

### Story F.d: v0.5.2 Bugfixes and API Feature Improvements [Done]

Bug 1 & 2: Pipeline must always populate in-memory metadata/transcript objects.
Bug 3: Transcript failures must be reported in result.errors.
Issue 4: CLI and library API must behave identically.
Feature Requests: Report available languages on transcript failure.

- [x] Add `read_metadata(out_dir, video_id) -> Metadata | None` to `core/writer.py`
  - [x] Read and parse `<out_dir>/<video_id>/metadata.json` into a `Metadata` model
  - [x] Return `None` if file does not exist or is unparseable
- [x] Add `read_transcript_json(out_dir, video_id) -> Transcript | None` to `core/writer.py`
  - [x] Read and parse `<out_dir>/<video_id>/transcript.json` into a `Transcript` model
  - [x] Return `None` if file does not exist or is unparseable
- [x] Fix `process_video()` in `core/pipeline.py` — metadata cache branch
  - [x] When metadata is cached (skip fetch), call `read_metadata()` to populate the in-memory `metadata` object
  - [x] Assign the loaded `Metadata` to `FetchResult.metadata`
- [x] Fix `process_video()` in `core/pipeline.py` — transcript cache branch
  - [x] When transcript is cached (skip fetch), call `read_transcript_json()` to populate the in-memory `transcript` object
  - [x] Assign the loaded `Transcript` to `FetchResult.transcript`
- [x] Fix error reporting when transcript is unavailable
  - [x] When `get_transcript()` raises `TranscriptError`, probe for available languages and include them in the error message
  - [x] Append a descriptive warning to `result.errors` (e.g., `"No transcript in ['en']; available: ['es', 'fr']"`)
  - [x] Keep `result.success = True` when metadata succeeded but transcript failed (partial failure)
- [x] Update `FetchResult` success logic in `core/pipeline.py`
  - [x] `success` should be `False` only when metadata fetch fails (critical failure)
  - [x] Transcript absence is a warning, not a failure — append to `errors` but do not set `success = False`
- [x] Write/update unit tests
  - [x] Test `read_metadata()` round-trip: write then read back
  - [x] Test `read_transcript_json()` round-trip: write then read back
  - [x] Test pipeline populates `result.metadata` from cache (no force flag)
  - [x] Test pipeline populates `result.transcript` from cache (no force flag)
  - [x] Test `result.errors` contains descriptive message when transcript unavailable
  - [x] Test `result.success` is `True` when metadata succeeds but transcript fails
- [x] Update `features.md`, `tech_spec.md` to reflect the changes
- [x] Verify: `fetch_video("dQw4w9WgXcQ", FetchOptions(download="none"))` returns non-None `metadata` and `transcript` on both first run and cached re-run
- [x] Bump version to `0.5.2` in `__init__.py` and `pyproject.toml`

---

## Phase G: Structured Error Handling

### Story G.a: v0.6.0 Error Models and Exception Hierarchy [Done]

Create `core/errors.py` with all error enums, the `FetchError` model, and the full exception hierarchy.

- [x] Create `yt_fetch/core/errors.py`:
  - [x] `FetchErrorCode(StrEnum)` with all codes per `error_handling_features.md`
  - [x] `FetchPhase(StrEnum)` — `METADATA`, `TRANSCRIPT`, `MEDIA`
  - [x] `FetchError(BaseModel)` — `code`, `message`, `phase`, `retryable`, `video_id`, `details: dict[str, Any] | None`
  - [x] `FetchException(Exception)` base class with `code: FetchErrorCode` and `retryable: bool`
  - [x] Transcript exceptions: `TranscriptError`, `TranscriptNotFound`, `TranscriptsDisabledError`, `TranscriptServiceError`
  - [x] Metadata exceptions: `MetadataError`, `VideoNotFoundError`, `MetadataServiceError`
  - [x] Media exceptions: `MediaError`, `MediaServiceError`
- [x] Add copyright/license header to `core/errors.py`
- [x] Export public types from `yt_fetch/__init__.py`: `FetchErrorCode`, `FetchPhase`, `FetchError`, `FetchException`
- [x] Update `FetchResult.errors` in `core/models.py` from `list[str]` to `list[FetchError]`
- [x] Write `tests/test_errors.py`:
  - [x] Test `FetchErrorCode` enum values and serialization
  - [x] Test `FetchPhase` enum values
  - [x] Test `FetchError` model creation and JSON round-trip
  - [x] Test exception hierarchy: `TranscriptNotFound` is a `TranscriptError` is a `FetchException`
  - [x] Test each exception subclass carries the correct default `code` and `retryable`
- [x] Verify: all existing tests still pass (no regressions from model type change)
- [x] Bump version to `0.6.0` in `__init__.py` and `pyproject.toml`

---

## Phase H: Replace Custom Retry with Gentlify

### Story H.a: v0.6.7 Add Gentlify as Core Dependency [Done]

Replace custom retry implementation with gentlify as the primary retry mechanism.

- [x] Add `gentlify` to core `dependencies` in `pyproject.toml`
- [x] Remove `gentlify` from any optional dependencies (it's now required)
- [x] Update documentation to reflect gentlify as the retry engine (completed in H.c)
- [x] No version bump (dependency-only change)

### Story H.b: v0.6.8 Replace Custom Retry with Gentlify [Done]

Remove `utils/retry.py` and replace all retry decorators with gentlify. Since gentlify is async-native and yt-fetch services are synchronous, use gentlify's `Throttle.execute()` within async wrappers.

- [x] Remove `yt_fetch/utils/retry.py` entirely
- [x] Create `yt_fetch/utils/gentlify_config.py`:
  - [x] `create_throttle(options: FetchOptions) -> Throttle` — creates configured gentlify Throttle instance
  - [x] Configure retry based on `FetchOptions.retries` (0 = no retry, N = max N attempts)
  - [x] Use `RetryConfig(backoff="exponential_jitter", retryable=...)` with custom retryable filter
  - [x] Retryable filter checks `FetchException.retryable` attribute on caught exceptions
  - [x] Exponential backoff for transient errors (retryable=True)
  - [x] No retry for permanent errors (retryable=False)
  - [x] `async_retry_wrapper(func, throttle) -> callable` — wraps sync function for gentlify execution
- [x] Update `services/metadata.py`:
  - [x] Remove `@retry` decorator
  - [x] Keep functions synchronous (no async conversion)
  - [x] Retry logic will be applied at pipeline level via gentlify wrapper
- [x] Update `services/transcript.py`:
  - [x] Remove `@retry` decorator
  - [x] Keep functions synchronous
  - [x] Retry logic will be applied at pipeline level via gentlify wrapper
- [x] Update `services/media.py`:
  - [x] Remove `@retry` decorator
  - [x] Keep functions synchronous
  - [x] Retry logic will be applied at pipeline level via gentlify wrapper
- [x] Update `core/pipeline.py`:
  - [x] Create throttle instance from `FetchOptions` at start of `process_video()`
  - [x] Wrap service calls (get_metadata, get_transcript, download_media) with gentlify async executor
  - [x] Use `asyncio.run()` or existing async context to execute wrapped calls
  - [x] Maintain synchronous pipeline API (internal async execution only)
- [x] Add copyright/license header to `utils/gentlify_config.py`
- [x] Update all tests that mock or test retry behavior:
  - [x] Update `tests/test_pipeline_errors.py` to work with gentlify
  - [x] Remove `tests/test_retry.py` if it exists
  - [x] Add `tests/test_gentlify_config.py` to test throttle configuration (completed in H.c)
- [x] Verify all existing tests pass with gentlify
- [x] Bump version to `0.6.8`

### Story H.c: v0.6.9 Gentlify Integration Testing and Documentation [Done]

Comprehensive testing and documentation for gentlify integration.

- [x] Write `tests/test_gentlify_config.py`:
  - [x] Test retryable errors are retried with exponential backoff
  - [x] Test non-retryable errors fail immediately
  - [x] Test retry exhaustion after max attempts
  - [x] Test `retries=0` disables all retries
  - [x] Test `retries=N` respects max retry count
  - [x] Test different error codes map to correct retry strategies
- [x] Update `README.md`:
  - [x] Document that yt-fetch uses gentlify for retry management
  - [x] Add examples showing retry configuration via `FetchOptions(retries=N)`
  - [x] Explain how `retries=0` disables retries for external retry management
- [x] Update `features.md` and `tech_spec.md`:
  - [x] Replace custom retry documentation with gentlify-based retry
  - [x] Document gentlify configuration and error code mapping
  - [x] Update retry strategy section to reference gentlify
- [x] Verify: all retry behavior works identically to previous custom implementation
- [x] Bump version to `0.6.9`

### Story H.d: v0.7.0 Service Error Classification and Exception Migration [Done]

Migrate services to use centralized exception hierarchy and implement exception classification helper.

- [x] Implement `_classify_exception(exc: Exception) -> FetchErrorCode` in `core/errors.py`:
  - [x] Priority 1: classify by exception type (upstream exceptions from `youtube-transcript-api`, `yt-dlp`)
  - [x] Priority 2: classify by HTTP status code (`status_code` or `code` attribute)
  - [x] Priority 3: classify by message string (fragile fallback)
  - [x] Default: `FetchErrorCode.UNKNOWN`
- [x] Update `services/transcript.py`:
  - [x] Remove local `TranscriptError` and `TranscriptNotFound` class definitions
  - [x] Import exception classes from `core/errors.py`
  - [x] Update error handling to use `_classify_exception()` and raise appropriate exceptions
  - [x] Map `TranscriptsDisabled` → `TranscriptsDisabledError`
  - [x] Map `NoTranscriptFound` → `TranscriptNotFound`
  - [x] Map network/service errors → `TranscriptServiceError` with proper error codes
- [x] Update `services/metadata.py`:
  - [x] Remove local `MetadataError` class definition
  - [x] Import exception classes from `core/errors.py`
  - [x] Update error handling to classify `yt_dlp.utils.DownloadError` properly
  - [x] Raise `VideoNotFoundError`, `MetadataServiceError`, or `MetadataError` as appropriate
- [x] Update `services/media.py`:
  - [x] Remove local `MediaError` class definition
  - [x] Import exception classes from `core/errors.py`
  - [x] Update error handling to classify `yt_dlp.utils.DownloadError` properly
  - [x] Raise `MediaServiceError` or `MediaError` as appropriate
- [x] Write tests in `tests/test_errors.py`:
  - [x] Test `_classify_exception()` for known upstream exception types (already implemented in core/errors.py)
  - [x] Test HTTP status code classification (already implemented)
  - [x] Test message-string fallback (already implemented)
  - [x] Test unknown exception → UNKNOWN (already implemented)
- [x] Update service tests to expect new exception types
- [x] Verify all tests pass (329 passed, 9 skipped)
- [x] Bump version to `0.7.0`

---

## Phase I: CI/CD & Automation

### Story I.a: v0.7.0 CI Workflow [Done]

GitHub Actions workflow for linting, testing, and coverage on every push and PR.

- [x] Create `.github/workflows/ci.yml`
  - [x] Trigger on `push` (all branches) and `pull_request` (all branches)
  - [x] Job: `lint` — install dev deps, run `ruff check .` and `ruff format --check .`
  - [x] Job: `test` — Python version matrix (3.14)
    - [x] Install package with dev extras (`pip install -e ".[dev]"`)
    - [x] Install `pytest-cov`
    - [x] Run `pytest --cov=yt_fetch --cov-report=xml --cov-report=term-missing`
    - [x] Upload `coverage.xml` to Codecov via `codecov/codecov-action@v4`
  - [x] Job: `integration` (optional, manual trigger via `workflow_dispatch` or gated by `RUN_INTEGRATION` secret)
    - [x] Run `RUN_INTEGRATION=1 pytest tests/integration/`
- [x] Add `pytest-cov` to `[project.optional-dependencies] dev` in `pyproject.toml`
- [x] Verify: coverage command works locally (94% coverage, 329 tests passed)

### Story I.b: Codecov Configuration [Done]

Configure Codecov for coverage thresholds and dynamic badge.

- [x] Create `codecov.yml` at repo root
  - [x] Set project coverage target (90%)
  - [x] Set patch coverage target (80%)
  - [x] Exclude `tests/` and `docs/` from coverage reporting
- [x] Enable the Codecov GitHub App on the `pointmatic/yt-fetch` repository (manual step - requires user action)
- [x] Verify: Codecov receives coverage data after a CI run and the badge URL resolves (94.15% coverage reported)

### Story I.c: v0.7.1 License Migration to Apache-2.0 [Done]

Migrate project license from MPL-2.0 to Apache-2.0 to align with current licensing preference.

- [x] Replace `LICENSE` file with Apache-2.0 license text
- [x] Update `pyproject.toml`:
  - [x] Change `license = "MPL-2.0"` to `license = "Apache-2.0"`
  - [x] Bump version to `0.7.1`
- [x] Update all source file headers to use Apache-2.0 boilerplate:
  - [x] Python files (`yt_fetch/**/*.py`, `tests/**/*.py`) - 42 files updated
  - [x] Replace MPL-2.0 header with Apache-2.0 header
  - [x] Keep copyright year and holder unchanged: `Copyright (c) 2026 Pointmatic`
- [x] Verify: all files have consistent Apache-2.0 headers (0 MPL-2.0 references remaining)
- [x] Run linting and tests to ensure no issues introduced (329 passed, 9 skipped)

### Story I.d: v0.7.2 Release Workflow — Auto-Publish to PyPI [Done]

Automated build and publish to PyPI on version tags using OIDC trusted publishing.

- [ ] Configure PyPI trusted publisher (manual step in PyPI project settings - requires user action)
  - [ ] Set GitHub repository: `pointmatic/yt-fetch`
  - [ ] Set workflow file: `release.yml`
  - [ ] Set environment: `pypi`
- [x] Create `.github/workflows/release.yml`
  - [x] Trigger on `push` tags matching `v*`
  - [x] Job: `build`
    - [x] Checkout code
    - [x] Install `build` package
    - [x] Run `python -m build` to produce sdist + wheel in `dist/`
    - [x] Upload `dist/` as a workflow artifact
  - [x] Job: `publish` (depends on `build`)
    - [x] Use environment `pypi` (for OIDC trusted publishing)
    - [x] Download the `dist/` artifact
    - [x] Use `pypa/gh-action-pypi-publish@release/v1` to publish to PyPI
- [x] Add `build` to `[project.optional-dependencies] dev` in `pyproject.toml`
- [ ] Verify: tagging `v0.7.2` and pushing triggers the release workflow; package appears on PyPI (requires PyPI setup and tag push)

### Story I.e: v0.7.3 README Badges [Done]

Add dynamic badges to the top of `README.md`.

- [x] Add badge block immediately after the `# yt-fetch` heading:
  - [x] **CI status** — `![CI](https://github.com/pointmatic/yt-fetch/actions/workflows/ci.yml/badge.svg)`
  - [x] **Codecov** — `[![codecov](https://codecov.io/gh/pointmatic/yt-fetch/graph/badge.svg)](https://codecov.io/gh/pointmatic/yt-fetch)`
  - [x] **PyPI version** — `[![PyPI](https://img.shields.io/pypi/v/yt-fetch)](https://pypi.org/project/yt-fetch/)`
  - [x] **Python versions** — `![Python](https://img.shields.io/pypi/pyversions/yt-fetch)`
  - [x] **License** — `![License](https://img.shields.io/github/license/pointmatic/yt-fetch)`
  - [ ] **Typed** — `![Typed](https://img.shields.io/badge/typed-py.typed-blue)` (deferred - py.typed created in Story J.a, badge can be added later)
- [x] Verify: badges render correctly on GitHub (CI and Codecov badges rendering; PyPI badges will render after first publish)

---

## Phase J: Production Polish

### Story J.a: v0.8.0 PyPI Metadata & Package Quality [Done]

Polish `pyproject.toml` for discoverability and PEP 561 compliance.

- [x] Add `[project.urls]` section to `pyproject.toml`:
  - [x] `Homepage = "https://github.com/pointmatic/yt-fetch"`
  - [x] `Repository = "https://github.com/pointmatic/yt-fetch"`
  - [x] `Bug Tracker = "https://github.com/pointmatic/yt-fetch/issues"`
  - [x] `Changelog = "https://github.com/pointmatic/yt-fetch/blob/main/CHANGELOG.md"`
- [x] Add `keywords` to `[project]`: `["youtube", "transcript", "metadata", "yt-dlp", "video", "ai", "llm", "content-extraction"]`
- [x] Add Trove `classifiers` to `[project]`:
  - [x] `"Development Status :: 4 - Beta"`
  - [x] `"License :: OSI Approved :: Apache Software License"`
  - [x] `"Programming Language :: Python :: 3"`
  - [x] `"Programming Language :: Python :: 3.14"`
  - [x] `"Topic :: Multimedia :: Video"`
  - [x] `"Typing :: Typed"`
- [x] Create `yt_fetch/py.typed` marker file (empty, PEP 561)
- [x] Ensure `py.typed` is included in the built package (setuptools auto-includes package data)
- [x] Bump version to `0.8.0`

### Story J.b: Dependency Management & Maintenance [Planned]

Automated dependency updates and contribution guidelines.

- [ ] Create `.github/dependabot.yml`
  - [ ] Enable `pip` ecosystem updates (weekly schedule)
  - [ ] Enable `github-actions` ecosystem updates (weekly schedule)
- [ ] Create `CONTRIBUTING.md` with:
  - [ ] Development setup instructions (clone, install dev deps, run tests)
  - [ ] Code style expectations (ruff, license headers)
  - [ ] PR process (branch, test, review)
- [ ] Create `SECURITY.md` with vulnerability reporting instructions

### Story J.c: Branch Protection & Repo Settings [Planned]

Manual configuration steps for repository hardening.

- [ ] Enable branch protection on `main`:
  - [ ] Require CI status checks to pass before merge
  - [ ] Require at least one review (if collaborators exist)
  - [ ] Require branches to be up to date before merge
- [ ] Verify: PRs to `main` cannot be merged without passing CI

### Story J.d: Changelog Automation [Planned]

Streamline release notes generation.

- [ ] Add a `release` section to the release workflow (`.github/workflows/release.yml`):
  - [ ] After successful PyPI publish, create a GitHub Release from the tag
  - [ ] Auto-generate release notes from merged PR titles since the last tag
- [ ] Document the release process in `CONTRIBUTING.md`:
  - [ ] Bump version in `pyproject.toml` and `yt_fetch/__init__.py`
  - [ ] Update `CHANGELOG.md`
  - [ ] Commit, tag `vX.Y.Z`, push tag
  - [ ] CI builds and publishes automatically

---

## Phase K: GitHub Pages Documentation

### Story K.a: v0.7.4 MkDocs Configuration & Project Structure [Planned]

Set up MkDocs with Material theme and create documentation directory structure.

- [ ] Install MkDocs dependencies locally:
  - [ ] `pip install mkdocs-material mkdocs-git-revision-date-localized-plugin`
- [ ] Create `mkdocs.yml` at repository root:
  - [ ] Set `site_name: yt-fetch`
  - [ ] Set `site_description` from descriptions.md (Friendly Brief Description)
  - [ ] Set `site_url: https://pointmatic.github.io/yt-fetch`
  - [ ] Set `repo_url: https://github.com/pointmatic/yt-fetch`
  - [ ] Configure Material theme with teal/cyan palette (matching brand color `#3ee8c8`)
  - [ ] Enable dark/light mode toggle
  - [ ] Enable navigation features (instant, tracking, tabs, sections, expand, top)
  - [ ] Enable search features (suggest, highlight)
  - [ ] Enable content features (code.copy, code.annotate)
  - [ ] Set `docs_dir: docs/site`
  - [ ] Set `site_dir: site`
  - [ ] Configure `nav` structure with Home (index.html) and placeholder pages
  - [ ] Add markdown extensions (admonition, pymdownx.details, pymdownx.superfences, pymdownx.highlight, pymdownx.tabbed, tables, toc)
  - [ ] Add plugins (search, git-revision-date-localized)
- [ ] Create `docs/site/` directory structure
- [ ] Create `docs/site/.gitignore`:
  - [ ] Ignore `/site/` build output
  - [ ] Ignore `.DS_Store`
- [ ] Add `mkdocs-material` and `mkdocs-git-revision-date-localized-plugin` to `[project.optional-dependencies] dev` in `pyproject.toml`
- [ ] Verify: `mkdocs serve` runs locally and shows placeholder site

### Story K.b: v0.7.5 Custom Landing Page [Planned]

Create a branded landing page with hero section, quick start, and feature cards.

- [ ] Create `docs/site/index.html`:
  - [ ] Add HTML5 boilerplate with meta tags (title, description, keywords from descriptions.md)
  - [ ] Add inline CSS with dark theme (background `#0a0f14`, accent `#3ee8c8`)
  - [ ] Create sticky navigation bar with logo and links (Features, Quick Start, Docs, GitHub)
  - [ ] Create hero section:
    - [ ] Use One-liner from descriptions.md as `<h1>` with accent color on "yt-fetch"
    - [ ] Use Friendly Brief Description from descriptions.md as subtitle
    - [ ] Add CTA buttons (View on GitHub, Get Started, Documentation)
  - [ ] Create Quick Start section:
    - [ ] Installation command: `pip install yt-fetch`
    - [ ] Basic usage example: `yt_fetch fetch --id VIDEO_ID`
    - [ ] Styled code block with syntax highlighting
  - [ ] Create Features section:
    - [ ] Use Feature Cards from descriptions.md (8 cards in responsive grid)
    - [ ] Each card with icon, title, and description
    - [ ] Styled with dark theme and teal accents
  - [ ] Ensure responsive design (mobile-friendly)
  - [ ] Use system fonts (no external font dependencies)
- [ ] Verify: Landing page renders correctly with `mkdocs serve`

### Story K.c: v0.7.6 Documentation Pages [Planned]

Create markdown documentation pages for getting started, usage, and API reference.

- [ ] Create `docs/site/getting-started.md`:
  - [ ] Installation section (pip, from source, optional dependencies)
  - [ ] Prerequisites (Python 3.14+, optional: ffmpeg for media download)
  - [ ] Quick start examples (single video, batch processing, library usage)
  - [ ] Configuration overview (CLI flags, config file)
  - [ ] Next steps (links to usage guide, API reference)
- [ ] Create `docs/site/usage.md`:
  - [ ] CLI commands overview (`fetch`, `batch`)
  - [ ] Common options (--id, --file, --jsonl, --output, --format, --download)
  - [ ] Metadata extraction (yt-dlp vs YouTube API)
  - [ ] Transcript fetching (language preference, fallback)
  - [ ] Media download (video, audio, both)
  - [ ] Caching and force re-fetch
  - [ ] Examples for each use case
- [ ] Create `docs/site/api.md`:
  - [ ] Library API overview
  - [ ] `fetch_video()` function signature and examples
  - [ ] `FetchOptions` configuration class
  - [ ] `FetchResult` output model
  - [ ] `Metadata`, `Transcript` models
  - [ ] Error handling (`FetchException`, `FetchErrorCode`)
  - [ ] Batch processing with `process_batch()`
- [ ] Create `docs/site/advanced.md`:
  - [ ] Retry configuration (gentlify integration)
  - [ ] Rate limiting (token bucket algorithm)
  - [ ] Playlist and channel resolution
  - [ ] Custom output formats
  - [ ] Integration with AI/LLM pipelines
- [ ] Update `mkdocs.yml` nav to include all pages
- [ ] Verify: All pages render correctly with proper navigation and cross-links

### Story K.d: v0.7.7 GitHub Actions Deployment Workflow [Planned]

Automate MkDocs deployment to GitHub Pages via GitHub Actions.

- [ ] Create `.github/workflows/deploy-docs.yml`:
  - [ ] Trigger on push to `main` branch
  - [ ] Trigger on manual `workflow_dispatch`
  - [ ] Set permissions: `contents: read`, `pages: write`, `id-token: write`
  - [ ] Set concurrency group: `pages` (cancel-in-progress: false)
  - [ ] Job: `build`
    - [ ] Checkout code
    - [ ] Set up Python 3.11
    - [ ] Install dependencies: `mkdocs-material`, `mkdocs-git-revision-date-localized-plugin`
    - [ ] Build MkDocs site: `mkdocs build --strict`
    - [ ] Upload artifact: `./site` directory
  - [ ] Job: `deploy` (depends on build)
    - [ ] Use environment: `github-pages`
    - [ ] Download artifact
    - [ ] Deploy to GitHub Pages
- [ ] Configure GitHub Pages (manual step - requires user action):
  - [ ] Go to repository Settings → Pages
  - [ ] Set Source to "GitHub Actions"
- [ ] Verify: Push to main triggers deployment; site available at `https://pointmatic.github.io/yt-fetch`

### Story K.e: v0.7.8 Documentation Polish & SEO [Planned]

Add final touches, SEO optimization, and cross-references.

- [ ] Update `index.html`:
  - [ ] Add Open Graph meta tags (og:title, og:description, og:image, og:url)
  - [ ] Add Twitter Card meta tags
  - [ ] Add favicon link (if available)
  - [ ] Ensure all links are correct (internal and external)
- [ ] Update all markdown pages:
  - [ ] Add cross-references between related pages
  - [ ] Use admonitions for notes, warnings, tips
  - [ ] Add code examples with proper syntax highlighting
  - [ ] Ensure consistent formatting and style
- [ ] Create `docs/site/changelog.md`:
  - [ ] Link to GitHub releases
  - [ ] Summarize major version changes
- [ ] Update `mkdocs.yml`:
  - [ ] Add `extra` section with social links (GitHub)
  - [ ] Add copyright notice
  - [ ] Verify all nav links are correct
- [ ] Test locally:
  - [ ] Run `mkdocs serve` and verify all pages load
  - [ ] Test navigation between pages
  - [ ] Test search functionality
  - [ ] Test dark/light mode toggle
  - [ ] Test mobile responsiveness
- [ ] Verify: Documentation site is complete, polished, and ready for public use

---

## Phase L: AI-Ready Content Extraction

### Story L.a: v0.9.0 LLM-Ready Transcript Text Formatting [Planned]

Replace bare concatenation in `transcript.txt` with intelligent paragraph chunking and optional features.

- [ ] Create `yt_fetch/utils/txt_formatter.py`:
  - [ ] `format_transcript_txt(segments, is_generated, gap_threshold, timestamps, raw) -> str`
  - [ ] **Default mode**: join segment text with spaces; insert `\n\n` paragraph breaks when the gap between consecutive segments exceeds `gap_threshold` (default 2.0 seconds)
  - [ ] **Timestamped mode** (`timestamps=True`): prepend `[MM:SS]` at each paragraph boundary
  - [ ] **Raw mode** (`raw=True`): bare concatenation with spaces, no paragraph formatting (backward-compatible)
  - [ ] **Auto-generated notice**: when `is_generated` is true, prepend `[Auto-generated transcript]\n\n`
  - [ ] `raw=True` overrides `timestamps`
- [ ] Add copyright/license header
- [ ] Update `core/writer.py`:
  - [ ] `write_transcript_txt()` calls `format_transcript_txt()` with options from `FetchOptions`
- [ ] Add `txt_timestamps`, `txt_raw`, `txt_gap_threshold` fields to `FetchOptions` in `core/options.py`
- [ ] Add `--txt-timestamps`, `--txt-raw`, `--txt-gap-threshold` CLI flags in `cli.py`
- [ ] Write `tests/test_txt_formatter.py`:
  - [ ] Test default paragraph chunking: segments with >2s gap produce paragraph breaks
  - [ ] Test segments with <2s gap are joined in same paragraph
  - [ ] Test custom gap threshold
  - [ ] Test timestamped mode produces `[MM:SS]` markers
  - [ ] Test raw mode produces bare concatenation
  - [ ] Test auto-generated notice is prepended when `is_generated=True`
  - [ ] Test auto-generated notice is absent when `is_generated=False` or `None`
- [ ] Update existing `test_writer.py` to verify new formatting is used
- [ ] Verify: `transcript.txt` output is readable, paragraph-chunked text by default
- [ ] Bump version to `0.9.0`

### Story L.b: v0.9.1 Content Hashing [Planned]

Add SHA-256 content hashes to metadata and transcript outputs for change detection.

- [ ] Create `yt_fetch/utils/hashing.py`:
  - [ ] `hash_metadata(metadata: Metadata) -> str` — SHA-256 of canonical fields (title, description, tags, upload_date, duration_seconds)
  - [ ] `hash_transcript(transcript: Transcript) -> str` — SHA-256 of concatenated segment text
  - [ ] `hash_bundle(metadata, transcript) -> str` — SHA-256 of combined content
  - [ ] All hashes are hex-encoded lowercase strings
  - [ ] Canonical field selection: exclude volatile fields (`view_count`, `like_count`, `fetched_at`, `raw`) so hashes are stable when content hasn't changed
- [ ] Add `content_hash: str | None = None` field to `Metadata` model in `core/models.py`
- [ ] Add `content_hash: str | None = None` field to `Transcript` model in `core/models.py`
- [ ] Update `services/metadata.py`: compute and set `content_hash` after metadata extraction
- [ ] Update `services/transcript.py`: compute and set `content_hash` after transcript extraction
- [ ] Write `tests/test_hashing.py`:
  - [ ] Test `hash_metadata` produces consistent hash for same content
  - [ ] Test `hash_metadata` produces different hash when title/description changes
  - [ ] Test `hash_metadata` produces same hash when only `view_count` changes
  - [ ] Test `hash_transcript` produces consistent hash for same segments
  - [ ] Test `hash_transcript` produces different hash when segment text changes
  - [ ] Test `hash_bundle` combines metadata and transcript hashes
- [ ] Verify: `metadata.json` and `transcript.json` contain `content_hash` field
- [ ] Bump version to `0.9.1`

### Story L.c: v0.9.2 Token Count Estimation [Planned]

Optionally estimate token counts for transcript text using `tiktoken`.

- [ ] Create `yt_fetch/utils/token_counter.py`:
  - [ ] `count_tokens(text: str, tokenizer: str = "cl100k_base") -> int`
  - [ ] `is_tokenizer_available() -> bool` — check if `tiktoken` is installed
  - [ ] Graceful degradation: if `tiktoken` not installed and tokenizer requested, log warning and return `None`
- [ ] Add `tiktoken` to `[project.optional-dependencies]` as `tokens` extra in `pyproject.toml`:
  - [ ] `tokens = ["tiktoken"]`
- [ ] Add `token_count: int | None = None` field to `Transcript` model in `core/models.py`
- [ ] Add `tokenizer: str | None = None` field to `FetchOptions` in `core/options.py`
- [ ] Add `--tokenizer` CLI flag in `cli.py`
- [ ] Update `services/transcript.py`: after fetching transcript, compute `token_count` if `options.tokenizer` is set
- [ ] Write `tests/test_token_counter.py`:
  - [ ] Test `count_tokens` returns correct count (mock `tiktoken` if needed)
  - [ ] Test `is_tokenizer_available` returns `False` when `tiktoken` not installed
  - [ ] Test graceful degradation: `token_count` is `None` when `tiktoken` unavailable
  - [ ] Test `token_count` is `None` when `tokenizer` option is not set
  - [ ] Test `token_count` is populated when `tokenizer` option is set and `tiktoken` available
- [ ] Verify: `transcript.json` contains `token_count` when tokenizer configured
- [ ] Bump version to `0.9.2`

### Story L.d: v0.9.3 Playlist and Channel Resolution [Planned]

Accept playlist and channel URLs as batch input sources.

- [ ] Create `yt_fetch/services/resolver.py`:
  - [ ] `resolve_playlist(url: str, max_videos: int | None = None) -> list[str]`
  - [ ] `resolve_channel(url: str, max_videos: int | None = None) -> list[str]`
  - [ ] `resolve_input(input_str: str, max_videos: int | None = None) -> list[str]` — auto-detect input type
  - [ ] Use `yt-dlp`'s `extract_info(url, download=False)` with `extract_flat=True` for efficient ID-only extraction
  - [ ] `max_videos` limits the number of IDs returned
  - [ ] Write resolved IDs to `<out>/resolved_ids.json` for reproducibility
- [ ] Add `max_videos: int | None = None` field to `FetchOptions` in `core/options.py`
- [ ] Add `--playlist`, `--channel`, `--max-videos` CLI flags in `cli.py`
- [ ] Update `core/pipeline.py` `process_batch()`: accept playlist/channel URLs, resolve to IDs, then process
- [ ] Export `resolve_playlist` and `resolve_channel` from `yt_fetch/__init__.py`
- [ ] Write `tests/test_resolver.py`:
  - [ ] Test `resolve_playlist` with mocked `yt-dlp` returns ordered video IDs
  - [ ] Test `resolve_channel` with mocked `yt-dlp` returns video IDs
  - [ ] Test `max_videos` limits the returned list
  - [ ] Test `resolve_input` auto-detects playlist vs channel vs video URL
  - [ ] Test `resolved_ids.json` is written to output directory
  - [ ] Test invalid URL raises appropriate error
- [ ] Add integration tests (guarded by `RUN_INTEGRATION=1`):
  - [ ] Resolve a known public playlist
  - [ ] Resolve a known public channel (with `max_videos=5`)
- [ ] Bump version to `0.9.3`

### Story K.e: v0.9.4 Video Bundle Output [Planned]

Optionally emit a unified `video_bundle.json` per video.

- [ ] Add `VideoBundle` model to `core/models.py`:
  - [ ] Fields: `video_id`, `metadata`, `transcript`, `errors`, `content_hash`, `token_count`, `fetched_at`
- [ ] Add `write_bundle(result: FetchResult, out_dir: Path) -> Path` to `core/writer.py`
- [ ] Add `bundle: bool = False` field to `FetchOptions` in `core/options.py`
- [ ] Add `--bundle` CLI flag in `cli.py`
- [ ] Update `core/pipeline.py` `process_video()`:
  - [ ] After all other outputs are written, if `options.bundle` is `True`, call `write_bundle()`
  - [ ] Bundle `content_hash` uses `hash_bundle()` from `utils/hashing.py`
  - [ ] Bundle `token_count` comes from `transcript.token_count`
- [ ] Write `tests/test_bundle.py`:
  - [ ] Test bundle contains correct `video_id`, `metadata`, `transcript`, `errors`
  - [ ] Test bundle `content_hash` matches `hash_bundle()` output
  - [ ] Test bundle `token_count` matches transcript `token_count`
  - [ ] Test bundle is NOT written when `bundle=False`
  - [ ] Test bundle IS written when `bundle=True`
  - [ ] Test bundle JSON round-trip (write + read back)
- [ ] Verify: `video_bundle.json` appears in output when `--bundle` is set
- [ ] Bump version to `0.9.4`

### Story K.f: v0.9.5 README and Documentation Update [Planned]

Update README and documentation to reflect the AI-ready positioning.

- [ ] Update `README.md`:
  - [ ] Change tagline to "AI-ready YouTube content extraction — metadata, transcripts, and media in structured formats"
  - [ ] Update Features list to highlight AI-ready capabilities (LLM-ready text, token counts, content hashes, playlist/channel resolution, video bundles)
  - [ ] Add "AI Pipeline" usage example showing `FetchOptions(tokenizer="cl100k_base", bundle=True)`
  - [ ] Add "Playlist Processing" usage example
  - [ ] Update CLI flags table with new flags
  - [ ] Add `[tokens]` optional dependency to installation section
- [ ] Update `pyproject.toml` description to "AI-ready YouTube content extraction — metadata, transcripts, and media in structured formats"
- [ ] Verify: README renders correctly on GitHub
- [ ] Bump version to `0.9.5`
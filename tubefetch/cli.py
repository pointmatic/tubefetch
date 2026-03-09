# Copyright (c) 2026 Pointmatic
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CLI entry point for tubefetch."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click

from tubefetch import __version__
from tubefetch.core.logging import get_logger, setup_logging
from tubefetch.core.options import FetchOptions
from tubefetch.services.id_parser import load_ids_from_file, parse_many

# Exit codes
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_PARTIAL = 2
EXIT_ALL_FAILED = 3


def _input_options(fn: Any) -> Any:
    """Shared input source options."""
    decorators = [
        click.argument("videos", nargs=-1),
        click.option(
            "--file",
            "file_path",
            type=click.Path(exists=True, path_type=Path),
            default=None,
            help="Text/CSV file with IDs.",
        ),  # noqa: E501
        click.option(
            "--jsonl",
            "jsonl_path",
            type=click.Path(exists=True, path_type=Path),
            default=None,
            help="JSONL file with video IDs.",
        ),  # noqa: E501
        click.option("--id-field", default="id", help="Field name for video ID in CSV/JSONL input."),
    ]
    for decorator in reversed(decorators):
        fn = decorator(fn)
    return fn


def _common_options(fn: Any) -> Any:
    """Shared Click options that map to FetchOptions fields."""
    decorators = [
        click.option("--out", type=click.Path(path_type=Path), default=None, help="Output directory."),
        click.option("--languages", type=str, default=None, help="Comma-separated language codes."),
        click.option("--allow-generated/--no-allow-generated", default=None, help="Allow auto-generated transcripts."),
        click.option("--allow-any-language/--no-allow-any-language", default=None, help="Fall back to any language."),
        click.option(
            "--download",
            type=click.Choice(["none", "video", "audio", "both"]),
            default=None,
            help="Media download mode.",
        ),  # noqa: E501
        click.option("--max-height", type=int, default=None, help="Max video height (e.g. 720)."),
        click.option("--format", "format_", type=str, default=None, help="Video format."),
        click.option("--audio-format", type=str, default=None, help="Audio format."),
        click.option("--force", is_flag=True, default=None, help="Force re-fetch everything."),
        click.option("--force-metadata", is_flag=True, default=None, help="Force re-fetch metadata."),
        click.option("--force-transcript", is_flag=True, default=None, help="Force re-fetch transcript."),
        click.option("--force-media", is_flag=True, default=None, help="Force re-download media."),
        click.option("--retries", type=int, default=None, help="Max retries per request."),
        click.option("--rate-limit", type=float, default=None, help="Requests per second."),
        click.option("--workers", type=int, default=None, help="Parallel workers for batch."),
        click.option("--fail-fast", is_flag=True, default=None, help="Stop on first failure."),
        click.option("--strict", is_flag=True, default=False, help="Exit 2 on partial failure."),
        click.option("--verbose", is_flag=True, default=None, help="Verbose console output."),
        click.option("--txt-timestamps", is_flag=True, default=None, help="Include [MM:SS] markers in transcript.txt."),
        click.option("--txt-raw", is_flag=True, default=None, help="Bare concatenation (no paragraph formatting)."),
        click.option(
            "--txt-gap-threshold", type=float, default=None, help="Silence gap (seconds) for paragraph breaks."
        ),
        click.option("--tokenizer", type=str, default=None, help="Tokenizer for token counting (e.g., cl100k_base)."),
    ]
    for decorator in reversed(decorators):
        fn = decorator(fn)
    return fn


def _build_options(strict: bool = False, **cli_kwargs: Any) -> FetchOptions:
    """Build FetchOptions from CLI kwargs, filtering out unset (None) values.

    Only explicitly-provided CLI flags are passed to FetchOptions as init
    overrides. Unset flags fall through to env vars → YAML → defaults.
    """
    overrides = {}
    for key, value in cli_kwargs.items():
        if value is None:
            continue
        if key == "format_":
            overrides["format"] = value
        elif key == "languages":
            overrides["languages"] = [lang.strip() for lang in value.split(",")]
        else:
            overrides[key] = value
    return FetchOptions(**overrides)


def _collect_ids(
    videos: tuple[str, ...],
    file_path: Path | None,
    jsonl_path: Path | None,
    id_field: str,
) -> list[str]:
    """Collect and deduplicate video IDs from all input sources."""
    raw: list[str] = list(videos)

    if file_path:
        raw.extend(load_ids_from_file(file_path, id_field=id_field))
    if jsonl_path:
        raw.extend(load_ids_from_file(jsonl_path, id_field=id_field))
    return parse_many(raw)


def _exit_code(total: int, failed: int, strict: bool) -> int:
    """Determine exit code from batch results."""
    if total == 0:
        return EXIT_OK
    if failed == 0:
        return EXIT_OK
    if failed == total:
        return EXIT_ALL_FAILED
    if strict:
        return EXIT_PARTIAL
    return EXIT_OK


def _print_simple_summary(content_type: str, total: int, succeeded: int, failed: int, out_dir: Path) -> None:
    """Print a simple summary for specialized commands."""
    log = get_logger()
    lines = [
        "",
        "=" * 40,
        f"  {content_type} Summary",
        "=" * 40,
        f"  Total:        {total}",
        f"  Succeeded:    {succeeded}",
        f"  Failed:       {failed}",
        f"  Output:       {out_dir.resolve()}",
        "=" * 40,
        "",
    ]
    log.info("\n".join(lines))


@click.group()
@click.version_option(version=__version__, prog_name="tubefetch")
def cli() -> None:
    """YouTube video metadata, transcript, and media fetcher.

    Fetch metadata, transcripts, and optionally media from YouTube videos.

    Examples:
      tubefetch VIDEO_ID
      tubefetch VIDEO_ID --download video
      tubefetch VIDEO_ID1 VIDEO_ID2 VIDEO_ID3
      tubefetch --file videos.txt

    Commands (for specialized use cases):
      metadata    Fetch metadata only
      transcript  Fetch transcripts only
      media       Download media only
    """
    pass


# Add a default command that handles when no subcommand is provided
@cli.command(name="default", hidden=True)
@_input_options
@_common_options
def default_cmd(
    videos: tuple[str, ...],
    file_path: Path | None,
    jsonl_path: Path | None,
    id_field: str,
    strict: bool,
    **kwargs: Any,
) -> None:
    """Default command - fetch metadata, transcripts, and optionally media."""
    options = _build_options(strict=strict, **kwargs)
    setup_logging(verbose=options.verbose)
    log = get_logger()

    video_ids = _collect_ids(videos, file_path, jsonl_path, id_field)
    if not video_ids:
        log.error("No video IDs provided. Provide video IDs/URLs as arguments, or use --file/--jsonl.")
        sys.exit(EXIT_ERROR)

    from tubefetch.core.pipeline import process_batch

    result = process_batch(video_ids, options)
    sys.exit(_exit_code(result.total, result.failed, strict))


# Override the group's main to handle default command
_original_cli_main = cli.main


def _cli_main_with_default(args: list[str] | None = None, **kwargs: Any) -> Any:
    """Wrapper that invokes default command if no subcommand is provided."""
    import sys as _sys

    if args is None:
        args = _sys.argv[1:]

    # Don't intercept --version or --help
    if args and args[0] in ("--version", "--help", "-h"):
        return _original_cli_main(args, **kwargs)

    # Check if first arg is a known subcommand
    known_commands = {"metadata", "transcript", "media"}
    if args and args[0] not in known_commands and not args[0].startswith("-"):
        # First arg is not a subcommand, invoke default command
        args = ["default"] + args
    elif not args or (args and args[0].startswith("-")):
        # No args or starts with option, invoke default command
        args = ["default"] + args

    return _original_cli_main(args, **kwargs)


cli.main = _cli_main_with_default  # type: ignore[method-assign,assignment]


@cli.command()
@_input_options
@_common_options
def transcript(
    videos: tuple[str, ...],
    file_path: Path | None,
    jsonl_path: Path | None,
    id_field: str,
    strict: bool,
    **kwargs: Any,
) -> None:
    """Fetch transcripts only."""
    options = _build_options(strict=strict, **kwargs)
    setup_logging(verbose=options.verbose)
    log = get_logger()

    video_ids = _collect_ids(videos, file_path, jsonl_path, id_field)
    if not video_ids:
        log.error("No video IDs provided. Provide video IDs/URLs as arguments, or use --file/--jsonl.")
        sys.exit(EXIT_ERROR)

    from tubefetch.core.writer import write_transcript_json
    from tubefetch.services.transcript import TranscriptError, get_transcript

    succeeded = 0
    failed = 0
    for vid in video_ids:
        try:
            t = get_transcript(vid, options)
            write_transcript_json(t, Path(options.out))
            log.info("Wrote transcript for %s", vid)
            succeeded += 1
        except TranscriptError as exc:
            log.error("Transcript error for %s: %s", vid, exc)
            failed += 1

    _print_simple_summary("Transcripts", len(video_ids), succeeded, failed, Path(options.out))
    sys.exit(_exit_code(len(video_ids), failed, strict))


@cli.command()
@_input_options
@_common_options
def metadata(
    videos: tuple[str, ...],
    file_path: Path | None,
    jsonl_path: Path | None,
    id_field: str,
    strict: bool,
    **kwargs: Any,
) -> None:
    """Fetch metadata only."""
    options = _build_options(strict=strict, **kwargs)
    setup_logging(verbose=options.verbose)
    log = get_logger()

    video_ids = _collect_ids(videos, file_path, jsonl_path, id_field)
    if not video_ids:
        log.error("No video IDs provided. Provide video IDs/URLs as arguments, or use --file/--jsonl.")
        sys.exit(EXIT_ERROR)

    from tubefetch.core.writer import write_metadata
    from tubefetch.services.metadata import MetadataError, get_metadata

    succeeded = 0
    failed = 0
    for vid in video_ids:
        try:
            m = get_metadata(vid, options)
            write_metadata(m, Path(options.out))
            log.info("Wrote metadata for %s", vid)
            succeeded += 1
        except MetadataError as exc:
            log.error("Metadata error for %s: %s", vid, exc)
            failed += 1

    _print_simple_summary("Metadata", len(video_ids), succeeded, failed, Path(options.out))
    sys.exit(_exit_code(len(video_ids), failed, strict))


@cli.command()
@_input_options
@_common_options
def media(
    videos: tuple[str, ...],
    file_path: Path | None,
    jsonl_path: Path | None,
    id_field: str,
    strict: bool,
    **kwargs: Any,
) -> None:
    """Download media only (defaults to video if --download not specified)."""
    options = _build_options(strict=strict, **kwargs)
    setup_logging(verbose=options.verbose)
    log = get_logger()

    video_ids = _collect_ids(videos, file_path, jsonl_path, id_field)
    if not video_ids:
        log.error("No video IDs provided. Provide video IDs/URLs as arguments, or use --file/--jsonl.")
        sys.exit(EXIT_ERROR)

    if options.download == "none":
        options = options.model_copy(update={"download": "video"})

    from tubefetch.services.media import MediaError, download_media

    succeeded = 0
    failed = 0
    for vid in video_ids:
        try:
            result = download_media(vid, options, Path(options.out))
            if result.skipped:
                log.warning("Skipped media for %s: %s", vid, result.errors)
            else:
                log.info("Downloaded media for %s", vid)
                succeeded += 1
        except MediaError as exc:
            log.error("Media error for %s: %s", vid, exc)
            failed += 1

    _print_simple_summary("Media", len(video_ids), succeeded, failed, Path(options.out))
    sys.exit(_exit_code(len(video_ids), failed, strict))


if __name__ == "__main__":
    cli()

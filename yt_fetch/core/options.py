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

"""FetchOptions settings model for yt-fetch."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class FetchOptions(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="YT_FETCH_",
        yaml_file="yt_fetch.yaml",
        yaml_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

    out: Path = Path("./out")
    languages: list[str] = ["en"]
    allow_generated: bool = True
    allow_any_language: bool = False
    download: Literal["none", "video", "audio", "both"] = "none"
    max_height: int | None = None
    format: str = "best"
    audio_format: str = "best"
    force: bool = False
    force_metadata: bool = False
    force_transcript: bool = False
    force_media: bool = False
    retries: int = 3
    rate_limit: float = 2.0
    workers: int = 3
    fail_fast: bool = False
    verbose: bool = False
    yt_api_key: str | None = None
    ffmpeg_fallback: Literal["error", "skip"] = "error"

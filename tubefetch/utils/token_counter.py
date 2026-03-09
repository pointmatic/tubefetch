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

"""Token count estimation using tiktoken."""

from __future__ import annotations

import logging

logger = logging.getLogger("tubefetch")


def is_tokenizer_available() -> bool:
    """Check if tiktoken is installed.

    Returns:
        True if tiktoken is available, False otherwise.
    """
    try:
        import tiktoken  # noqa: F401

        return True
    except ImportError:
        return False


def count_tokens(text: str, tokenizer: str = "cl100k_base") -> int | None:
    """Count tokens in text using the specified tiktoken tokenizer.

    Args:
        text: Text to count tokens for.
        tokenizer: Tokenizer name (e.g., "cl100k_base" for GPT-4, "p50k_base" for GPT-3).

    Returns:
        Token count, or None if tiktoken is not installed.
    """
    if not is_tokenizer_available():
        logger.warning(
            "tiktoken is not installed. Install with: pip install 'tubefetch[tokens]'. Token counting is disabled."
        )
        return None

    try:
        import tiktoken

        encoding = tiktoken.get_encoding(tokenizer)
        return len(encoding.encode(text))
    except Exception as exc:
        logger.warning("Failed to count tokens with tokenizer %s: %s", tokenizer, exc)
        return None

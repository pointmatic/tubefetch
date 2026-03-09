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

"""Tests for token counting."""

import pytest

from tubefetch.utils.token_counter import count_tokens, is_tokenizer_available


def test_is_tokenizer_available():
    """is_tokenizer_available returns bool indicating tiktoken availability."""
    result = is_tokenizer_available()
    assert isinstance(result, bool)


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_basic():
    """count_tokens returns token count for simple text."""
    text = "Hello world"
    count = count_tokens(text, "cl100k_base")

    assert count is not None
    assert isinstance(count, int)
    assert count > 0


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_empty_string():
    """count_tokens handles empty string."""
    count = count_tokens("", "cl100k_base")

    assert count is not None
    assert count == 0


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_longer_text():
    """count_tokens handles longer text."""
    text = "This is a longer piece of text that should have more tokens than a simple greeting."
    count = count_tokens(text, "cl100k_base")

    assert count is not None
    assert isinstance(count, int)
    assert count > 10  # Should have more than 10 tokens


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_different_tokenizers():
    """count_tokens works with different tokenizer names."""
    text = "Hello world"

    # cl100k_base (GPT-4)
    count1 = count_tokens(text, "cl100k_base")
    assert count1 is not None

    # p50k_base (GPT-3)
    count2 = count_tokens(text, "p50k_base")
    assert count2 is not None

    # Both should return valid counts
    assert isinstance(count1, int)
    assert isinstance(count2, int)


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_unicode():
    """count_tokens handles unicode text."""
    text = "Hello 世界 🌍"
    count = count_tokens(text, "cl100k_base")

    assert count is not None
    assert isinstance(count, int)
    assert count > 0


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_consistent():
    """count_tokens produces consistent results for same text."""
    text = "This is a test"

    count1 = count_tokens(text, "cl100k_base")
    count2 = count_tokens(text, "cl100k_base")

    assert count1 == count2


def test_count_tokens_without_tiktoken(monkeypatch):
    """count_tokens returns None when tiktoken is not available."""

    # Mock is_tokenizer_available to return False
    def mock_is_available():
        return False

    monkeypatch.setattr("tubefetch.utils.token_counter.is_tokenizer_available", mock_is_available)

    count = count_tokens("Hello world", "cl100k_base")
    assert count is None


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_invalid_tokenizer():
    """count_tokens returns None for invalid tokenizer name."""
    text = "Hello world"
    count = count_tokens(text, "invalid_tokenizer_name")

    # Should return None and log warning
    assert count is None


@pytest.mark.skipif(not is_tokenizer_available(), reason="tiktoken not installed")
def test_count_tokens_multiline():
    """count_tokens handles multiline text."""
    text = """This is line one.
This is line two.
This is line three."""

    count = count_tokens(text, "cl100k_base")

    assert count is not None
    assert isinstance(count, int)
    assert count > 10

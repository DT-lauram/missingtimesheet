"""Unit tests for the hello module."""

import pytest

from src.hello import greet


class TestGreet:
    """Test cases for the greet function."""

    def test_greet_with_valid_name(self) -> None:
        """Test greeting with a valid name."""
        result = greet("World")
        assert result == "Hello, World!"

    def test_greet_with_name_containing_spaces(self) -> None:
        """Test greeting with a name that has leading/trailing spaces."""
        result = greet("  Alice  ")
        assert result == "Hello, Alice!"

    def test_greet_with_different_names(self) -> None:
        """Test greeting with various valid names."""
        assert greet("Bob") == "Hello, Bob!"
        assert greet("Charlie") == "Hello, Charlie!"
        assert greet("123") == "Hello, 123!"

    def test_greet_with_empty_string_raises_error(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            greet("")

    def test_greet_with_whitespace_only_raises_error(self) -> None:
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            greet("   ")

    def test_greet_with_tab_only_raises_error(self) -> None:
        """Test that tab-only string raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            greet("\t")

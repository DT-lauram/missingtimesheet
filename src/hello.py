"""Simple Hello World module for template demonstration."""


def greet(name: str) -> str:
    """Generate a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A greeting message string.

    Raises:
        ValueError: If name is empty or whitespace only.
    """
    if not name or not name.strip():
        msg = "Name cannot be empty"
        raise ValueError(msg)

    return f"Hello, {name.strip()}!"


def main() -> None:
    """Entry point for the hello module."""
    message = greet("World")
    print(message)


if __name__ == "__main__":
    main()

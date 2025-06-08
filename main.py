"""Entry point for the Lucas project."""

# Import the scheduler to ensure scheduled jobs are registered on startup.
from lucas_project.core import scheduler  # noqa: F401


def main() -> None:
    """Placeholder main function."""
    print("Lucas project bootstrap")


if __name__ == "__main__":
    main()

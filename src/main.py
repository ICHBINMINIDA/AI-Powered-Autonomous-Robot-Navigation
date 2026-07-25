"""Application entry point."""

from __future__ import annotations

import logging

from config import SETTINGS
from controllers import RobotController


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    configure_logging()
    RobotController(SETTINGS).run()


if __name__ == "__main__":
    main()

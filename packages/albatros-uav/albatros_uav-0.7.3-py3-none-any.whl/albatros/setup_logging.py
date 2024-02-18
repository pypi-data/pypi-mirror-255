import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.CRITICAL,
        format="%(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    )

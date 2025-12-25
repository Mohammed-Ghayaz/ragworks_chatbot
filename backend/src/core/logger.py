import logging
import sys

logger = logging.getLogger("ragworks")

if not logger.handlers:
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    # Optional file handler (fine for dev)
    file = logging.FileHandler("app.log")
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)

    logger.propagate = False

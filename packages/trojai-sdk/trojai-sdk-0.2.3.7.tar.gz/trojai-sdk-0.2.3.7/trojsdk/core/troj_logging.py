import os
import logging


def getLogger(file: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    log = logging.getLogger(os.path.basename(file))

    return log

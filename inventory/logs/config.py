from pathlib import Path
import logging
import logging.config


BASE_DIR = Path(__file__).resolve().parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file": {"format": "%(asctime)s %(name)-25s %(levelname)-7s %(message)s"},
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": f"{BASE_DIR}/logs.log",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {
            "level": "ERROR",
            "handlers": ["file"],
        },
        "": {
            "level": "INFO",
            "handlers": ["file"],
        },
    },
}


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger("inventory consumer")
    logging.config.dictConfig(LOGGING)
    return logger

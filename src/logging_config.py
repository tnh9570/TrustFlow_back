# logging_config.py
from logging.config import dictConfig

# 로깅 설정
def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            #  "color_formatter": {
            #     "()": "colorlog.ColoredFormatter",
            #     "format": "%(log_color)s[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            #     "log_colors": {
            #         "DEBUG": "cyan",
            #         "INFO": "green",
            #         "WARNING": "yellow",
            #         "ERROR": "red",
            #         "CRITICAL": "red,bg_white",
            #     },
            # },
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            },
            "detailed": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "detailed",
                "level": "INFO",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    }

    dictConfig(logging_config)

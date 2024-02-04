from pydantic import BaseModel
import logging
import json
from pythonjsonlogger import jsonlogger

class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(JsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = self.formatTime(record)
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        if isinstance(message_dict, dict):
            for key, value in message_dict.items():
                log_record[key] = value


class LogConfig(BaseModel):
    """
    Logging-Konfiguration für den Server.

    Attributes:
        LOGGER_NAME (str): Der Name des Loggers.
        LOG_FORMAT (str): Das Format für die Standard-Logausgabe.
        JSON_LOG_FORMAT (str): Das Format für die JSON-Logausgabe.
        LOG_LEVEL (str): Das Log-Level für den Logger.
        LOG_FILE (str): Der Pfad zur Log-Datei.

    Example:
        config = LogConfig()
    """

    LOGGER_NAME: str = "GreenEcoHub"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    JSON_LOG_FORMAT: str = "%(timestamp)s %(level)s %(name)s %(message)s"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "./logs/server.log"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": JsonFormatter,
            "fmt": JSON_LOG_FORMAT,
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "encoding": "utf8",
            "mode": "a",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default", "file"], "level": LOG_LEVEL},
    }

class LogConfigRegistration(BaseModel):
    """
    Logging-Konfiguration für den Server-Registration-Logger.

    Attributes:
        LOGGER_NAME (str): Der Name des Loggers.
        LOG_FORMAT (str): Das Format für die Standard-Logausgabe.
        JSON_LOG_FORMAT (str): Das Format für die JSON-Logausgabe.
        LOG_LEVEL (str): Das Log-Level für den Logger.
        LOG_FILE (str): Der Pfad zur Log-Datei.

    Example:
        config = LogConfigRegistration()
    """

    LOGGER_NAME: str = "GreenEcoHubRegistration"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    JSON_LOG_FORMAT: str = "%(timestamp)s %(level)s %(name)s %(message)s"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "./logs/server_registration.log"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": JsonFormatter,
            "fmt": JSON_LOG_FORMAT,
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "encoding": "utf8",
            "mode": "a",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default", "file"], "level": LOG_LEVEL},
    }


class LogConfigAdresse(BaseModel):
    """
    Logging-Konfiguration für den Server-Adresse-Logger.

    Attributes:
        LOGGER_NAME (str): Der Name des Loggers.
        LOG_FORMAT (str): Das Format für die Standard-Logausgabe.
        JSON_LOG_FORMAT (str): Das Format für die JSON-Logausgabe.
        LOG_LEVEL (str): Das Log-Level für den Logger.
        LOG_FILE (str): Der Pfad zur Log-Datei.

    Example:
        config = LogConfigAdresse()
    """

    LOGGER_NAME: str = "GreenEcoHubAdresse"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    JSON_LOG_FORMAT: str = "%(timestamp)s %(level)s %(name)s %(message)s"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "./logs/server_adresse.log"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": JsonFormatter,
            "fmt": JSON_LOG_FORMAT,
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "encoding": "utf8",
            "mode": "a",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default", "file"], "level": LOG_LEVEL},
    }

class LogConfigBase(BaseModel):
    """
    Basisklasse für die Logging-Konfiguration für den Server.

    Attributes:
        LOGGER_NAME (str): Der Name des Loggers.
        LOG_FORMAT (str): Das Format für die Standard-Logausgabe.
        LOG_LEVEL (str): Das Log-Level für den Logger.
        LOG_FILE (str): Der Pfad zur Log-Datei.

    Example:
        config = LogConfigBase()
    """

    LOGGER_NAME: str = "GreenEcoHubBase"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "./logs/server_all.log"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "encoding": "utf-8",
            "mode": "a",  # Append mode
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default", "file"], "level": LOG_LEVEL},
    }
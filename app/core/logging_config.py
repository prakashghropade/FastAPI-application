import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in structured JSON format.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Capture traceback if exception is present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Capture any extra attributes passed with the log
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            for key, val in record.extra.items():
                if key not in log_record:
                    log_record[key] = val
                    
        return json.dumps(log_record)


def setup_logging():
    """
    Initializes and configures the logging system.
    Logs are written in structured JSON to logs/app.log and console.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "app.log")
    
    # Root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.setLevel(logging.INFO)
    
    # Console Handler (JSON formatted in production, pretty formatted if needed, or JSON for consistency)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = JSONFormatter()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # File Handler (JSON formatted, rotating)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024, # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logging.info("Logging configured successfully.")


# Obtain a standard logger for use in other modules
logger = logging.getLogger("app")

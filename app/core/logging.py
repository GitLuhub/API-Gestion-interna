import logging
import traceback
from datetime import datetime, timezone
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

class CustomJSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJSONFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
        log_record["request_id"] = request_id_ctx_var.get()
        
        if record.exc_info:
            log_record["exception"] = "".join(traceback.format_exception(*record.exc_info))

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    formatter = CustomJSONFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

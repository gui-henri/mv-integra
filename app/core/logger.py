import logging
import sys
from app.core.config import settings

def setup_logging():
    logger = logging.getLogger("mv_integra")
    logger.setLevel(settings.LOG_LEVEL)
    
    # Check if handler already exists to avoid duplicate logs
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(settings.LOG_LEVEL)
        
        # JSON-like format or simple text format, let's stick to simple text for now as requested "great logging"
        # but often JSON is better for systems. User said "great logging", I'll provide a clear format.
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        # Also set root logger level
        logging.getLogger().setLevel(settings.LOG_LEVEL)
    
    return logger

logger = setup_logging()

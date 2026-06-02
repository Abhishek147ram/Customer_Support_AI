import sys
from loguru import logger
from app.config.settings import settings

logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level.upper(),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    enqueue=True,
    backtrace=False,
    diagnose=False,
)
logger.add(
    "logs/app.log",
    level=settings.log_level.upper(),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{line} - {message}",
    rotation="10 MB",
    retention="7 days",
    enqueue=True,
    backtrace=False,
    diagnose=False,
)

import logging
import sys
from datetime import datetime
from typing import Optional
import traceback


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    colored: bool = True
) -> logging.Logger:
    """
    Setup application logging with console and optional file output
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        colored: Whether to use colored console output
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("gitgauge")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    if colored:
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all levels
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_function_call(func):
    """Decorator to log function calls with parameters and execution time"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("gitgauge")
        start_time = datetime.now()
        
        # Log function entry
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Function {func.__name__} completed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Function {func.__name__} failed after {execution_time:.3f}s: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    return wrapper


def log_api_request(request_id: str, method: str, path: str, status_code: int, duration: float):
    """Log API request details"""
    logger = logging.getLogger("gitgauge.api")
    
    # Color code based on status
    if 200 <= status_code < 300:
        level = logging.INFO
        status_color = "✅"
    elif 300 <= status_code < 400:
        level = logging.INFO
        status_color = "🔄"
    elif 400 <= status_code < 500:
        level = logging.WARNING
        status_color = "⚠️"
    else:
        level = logging.ERROR
        status_color = "❌"
    
    logger.log(level, f"{status_color} {method} {path} -> {status_code} ({duration:.3f}s) [ID: {request_id}]")


def log_job_progress(job_id: str, stage: str, message: str, level: str = "INFO"):
    """Log job processing progress"""
    logger = logging.getLogger("gitgauge.jobs")
    logger.log(
        getattr(logging, level.upper()),
        f"Job {job_id} | {stage} | {message}"
    )


def log_github_api_call(endpoint: str, status_code: int, rate_limit_remaining: int):
    """Log GitHub API calls"""
    logger = logging.getLogger("gitgauge.github")
    
    if 200 <= status_code < 300:
        logger.info(f"GitHub API: {endpoint} -> {status_code} (Rate limit: {rate_limit_remaining})")
    else:
        logger.warning(f"GitHub API: {endpoint} -> {status_code} (Rate limit: {rate_limit_remaining})")


def log_ai_analysis(job_id: str, model: str, tokens_used: int, duration: float):
    """Log AI analysis details"""
    logger = logging.getLogger("gitgauge.ai")
    logger.info(f"AI Analysis | Job: {job_id} | Model: {model} | Tokens: {tokens_used} | Duration: {duration:.3f}s")


def log_database_operation(operation: str, table: str, record_id: str, duration: float):
    """Log database operations"""
    logger = logging.getLogger("gitgauge.db")
    logger.debug(f"DB {operation} | Table: {table} | ID: {record_id} | Duration: {duration:.3f}s")


def log_error_with_context(error: Exception, context: dict = None):
    """Log error with additional context"""
    logger = logging.getLogger("gitgauge")
    
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        context_str = " | ".join([f"{k}: {v}" for k, v in context.items()])
        error_msg += f" | Context: {context_str}"
    
    logger.error(error_msg)
    logger.debug(f"Traceback: {traceback.format_exc()}")


# Global logger instance
logger = setup_logging()

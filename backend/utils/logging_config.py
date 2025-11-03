"""
Structured Logging Configuration for EduFunds Backend
Implements production-ready logging with PII redaction and JSON output
"""

import structlog
import logging
import sys
import re
import os
from typing import Any, Dict


def redact_pii(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact personally identifiable information from logs

    Args:
        logger: structlog logger instance
        method_name: Method name being called
        event_dict: Event dictionary to process

    Returns:
        Event dictionary with PII redacted
    """
    # Sensitive keys to redact completely
    sensitive_keys = [
        'password', 'token', 'api_key', 'secret', 'ssn',
        'credit_card', 'cvv', 'authorization', 'jwt',
        'access_token', 'refresh_token', 'session_id'
    ]

    for key in list(event_dict.keys()):
        if any(s in key.lower() for s in sensitive_keys):
            event_dict[key] = '***REDACTED***'

    # Redact email addresses in event message
    if 'event' in event_dict:
        event_dict['event'] = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '***EMAIL***',
            str(event_dict['event'])
        )

    # Redact phone numbers (German format)
    if 'event' in event_dict:
        event_dict['event'] = re.sub(
            r'\b(\+49|0)[1-9]\d{1,4}\s?\d{3,}\b',
            '***PHONE***',
            str(event_dict['event'])
        )

    # Hash IP addresses (keep first 2 octets for debugging)
    if 'client_ip' in event_dict:
        ip = event_dict['client_ip']
        if ip and '.' in ip:
            parts = ip.split('.')
            event_dict['client_ip'] = f'{parts[0]}.{parts[1]}.xxx.xxx'

    return event_dict


def add_app_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add application context to all log events

    Args:
        logger: structlog logger instance
        method_name: Method name being called
        event_dict: Event dictionary to process

    Returns:
        Event dictionary with application context added
    """
    event_dict['app'] = 'edufunds-backend'
    event_dict['env'] = os.getenv('ENV', 'development')
    event_dict['version'] = os.getenv('APP_VERSION', '1.0.0')

    return event_dict


def configure_logging(env: str = None, log_level: str = None) -> None:
    """
    Configure structured logging for FastAPI application

    Args:
        env: Environment (development, staging, production)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    if env is None:
        env = os.getenv('ENV', 'development')

    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO' if env == 'production' else 'DEBUG')

    # Base processors (always active)
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_app_context,
        redact_pii,
    ]

    # Environment-specific rendering
    if env == 'development':
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # JSON output for production (Loki/Grafana)
        processors.append(structlog.processors.JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Suppress noisy third-party loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.INFO)

    # Log configuration complete
    logger = structlog.get_logger()
    logger.info(
        'logging_configured',
        env=env,
        log_level=log_level,
        processors_count=len(processors),
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Example usage in routers:
"""
from utils.logging_config import get_logger

logger = get_logger(__name__)

@router.post('/generate-draft')
async def generate_draft(request: DraftRequest, user: User = Depends(get_current_user)):
    logger.info(
        'draft_generation_started',
        user_id=user.id,
        school_id=user.school_id,
        funding_id=request.funding_id,
    )

    try:
        draft = await generate_ai_draft(request)

        logger.info(
            'draft_generation_success',
            user_id=user.id,
            funding_id=request.funding_id,
            duration_ms=draft.generation_time,
            tokens_used=draft.tokens,
        )

        return draft

    except Exception as e:
        logger.error(
            'draft_generation_failed',
            user_id=user.id,
            funding_id=request.funding_id,
            error=str(e),
            exc_info=True,
        )
        raise
"""

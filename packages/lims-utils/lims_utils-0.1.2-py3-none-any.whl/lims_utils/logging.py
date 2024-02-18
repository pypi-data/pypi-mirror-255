import logging

from fastapi import Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException

app_logger = logging.getLogger("uvicorn")
uvicorn_logger = logging.getLogger("uvicorn.access")


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if type(record.args) is not tuple:
            return True

        return not record.args or record.args[2] != "/docs"


def register_loggers():
    """Register Uvicorn error and access logs, filtering out calls to /docs by default"""
    uvicorn_logger.addFilter(EndpointFilter())

    logging.basicConfig(format="%(levelname)s: %(message)s")
    app_logger.setLevel("INFO")


async def log_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler, takes HTTP exception and prints more details about the context
    of the exception before reraising it"""
    if exc.status_code != 401:
        user = "Unknown user"
        try:
            user = request.state.__getattr__("user")
        except AttributeError:
            pass
        finally:
            app_logger.warning(
                "%s @ %s: %s",
                user,
                request.url,
                exc.detail,
            )
    return await http_exception_handler(request, exc)

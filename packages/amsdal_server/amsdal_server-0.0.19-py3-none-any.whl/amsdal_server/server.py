from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from amsdal_models.errors import AmsdalValidationError
from amsdal_utils.lifecycle.enum import LifecycleEvent
from amsdal_utils.lifecycle.producer import LifecycleProducer
from fastapi import FastAPI
from fastapi import responses
from pydantic import ValidationError

from amsdal_server.apps.classes.errors import ClassNotFoundError
from amsdal_server.apps.classes.errors import TransactionNotFoundError
from amsdal_server.apps.common.error_handlers.class_not_found import class_not_found_handler
from amsdal_server.apps.common.error_handlers.validation_error_handler import validation_error_handler
from amsdal_server.apps.common.error_handlers.validation_error_handler import value_error_handler
from amsdal_server.apps.common.errors import AmsdalTransactionError
from amsdal_server.apps.common.middlewares.utils import init_middlewares
from amsdal_server.apps.router import init_routers
from amsdal_server.configs.constants import APP_DESCRIPTION
from amsdal_server.configs.main import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    LifecycleProducer.publish(LifecycleEvent.ON_SERVER_STARTUP)
    yield


app = FastAPI(
    debug=settings.DEBUG,
    title=settings.APP_NAME,
    description=APP_DESCRIPTION,
    docs_url='/docs' if settings.IS_DOCS_ENABLED else None,
    default_response_class=responses.ORJSONResponse,
    lifespan=lifespan,
)
init_routers(app)
init_middlewares(app)

app.exception_handler(ValidationError)(validation_error_handler)
app.exception_handler(ValueError)(value_error_handler)
app.exception_handler(AmsdalTransactionError)(value_error_handler)
app.exception_handler(AmsdalValidationError)(value_error_handler)
app.exception_handler(ClassNotFoundError)(class_not_found_handler)
app.exception_handler(TransactionNotFoundError)(class_not_found_handler)


def start(
    *,
    is_development_mode: bool = False,
    port: int | None = None,
    host: str | None = None,
) -> None:
    _app = '__main__:app' if is_development_mode else app
    """Start the server."""
    uvicorn.run(
        _app,  # type: ignore[arg-type]
        host=host or settings.HOST,
        port=port or settings.PORT,
        # We already log in LoggerMiddleware
        # no need to duplicate these logs with uvicorn
        access_log=False,
        reload=is_development_mode,
    )


if __name__ == '__main__':
    start(is_development_mode=True)

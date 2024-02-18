import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger('amsdal_server.http')


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        before_time = time.perf_counter()
        error: BaseException | None = None
        status_code: int = -1

        try:
            response = await call_next(request)
        except BaseException as exc:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            error = exc
            raise exc from None
        else:
            status_code = response.status_code
        finally:
            after_time = time.perf_counter()
            user = request.user
            path = self.get_path_template(request)
            log = logger.error if error else logger.info
            log(
                'method=%s path=%s status=%s time=%.3f user=%s',
                request.method,
                path,
                status_code,
                after_time - before_time,
                user,
            )
        return response

    @staticmethod
    def get_path_template(request: Request) -> str:
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path
        return request.url.path

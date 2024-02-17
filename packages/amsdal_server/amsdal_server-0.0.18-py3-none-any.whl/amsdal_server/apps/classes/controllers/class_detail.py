from fastapi import Request

from amsdal_server.apps.classes.router import router
from amsdal_server.apps.classes.serializers.class_info import ClassInfo
from amsdal_server.apps.classes.services.classes_api import ClassesApi


@router.get('/api/classes/{class_name}/')
async def get_class(
    request: Request,
    class_name: str,
) -> ClassInfo:
    return ClassesApi.get_class_by_name(request.user, class_name)

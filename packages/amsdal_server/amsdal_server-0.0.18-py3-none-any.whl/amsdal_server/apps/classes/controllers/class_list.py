from fastapi import Request

from amsdal_server.apps.classes.router import router
from amsdal_server.apps.classes.services.classes_api import ClassesApi
from amsdal_server.apps.common.serializers.column_format import ColumnFormat
from amsdal_server.apps.common.serializers.column_response import ColumnInfo
from amsdal_server.apps.common.serializers.objects_response import ObjectsResponse


@router.get('/api/classes/', response_model_exclude_none=True)
async def class_list(request: Request) -> ObjectsResponse:
    class_items = ClassesApi.get_classes(request.user)

    return ObjectsResponse(
        columns=[
            ColumnInfo(
                key='class',
                label='Class',
                column_format=ColumnFormat(cellTemplate='ClassLinkTemplate'),
            ),
            ColumnInfo(key='count', label='Count'),
            ColumnInfo(key='properties', label='Properties'),
        ],
        rows=class_items,
    ).model_dump()  # type: ignore[return-value]

from typing import Any

from fastapi import Depends
from fastapi import Request

from amsdal_server.apps.common.depends import get_fields_restrictions
from amsdal_server.apps.common.depends import get_filters
from amsdal_server.apps.common.serializers.fields_restriction import FieldsRestriction
from amsdal_server.apps.common.serializers.filter import Filter
from amsdal_server.apps.common.serializers.objects_response import ObjectsResponse
from amsdal_server.apps.objects.router import router
from amsdal_server.apps.objects.services.object_list_api import ObjectListApi


@router.get('/api/objects/', response_model_exclude_none=True, response_model=ObjectsResponse)
async def object_list(
    request: Request,
    class_name: str,
    *,
    include_metadata: bool = True,
    include_subclasses: bool = True,
    load_references: bool = False,
    all_versions: bool = False,
    fields_restrictions: dict[str, FieldsRestriction] = Depends(get_fields_restrictions),
    filters: list[Filter] = Depends(get_filters),
) -> dict[str, Any]:
    return ObjectListApi.fetch_objects(
        request.user,
        class_name,
        filters=filters,
        fields_restrictions=fields_restrictions,
        include_metadata=include_metadata,
        include_subclasses=include_subclasses,
        load_references=load_references,
        all_versions=all_versions,
    ).model_dump()

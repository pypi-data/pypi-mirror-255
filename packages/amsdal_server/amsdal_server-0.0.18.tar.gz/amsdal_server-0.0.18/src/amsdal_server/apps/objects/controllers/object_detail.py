import urllib.parse

from fastapi import Request

from amsdal_server.apps.common.serializers.objects_response import ObjectsResponse
from amsdal_server.apps.objects.router import router
from amsdal_server.apps.objects.services.object_versions_api import ObjectVersionsApi


@router.get('/api/objects/{address:path}/')
async def object_detail(
    address: str,
    request: Request,
    version_id: str = '',
    *,
    all_versions: bool = False,
    include_metadata: bool = True,
) -> ObjectsResponse:
    return ObjectVersionsApi.get_object_versions(
        request.user,
        urllib.parse.unquote(address),
        version_id=version_id,
        all_versions=all_versions,
        include_metadata=include_metadata,
    )

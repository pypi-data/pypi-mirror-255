from amsdal_server.apps.common.serializers.objects_response import ObjectsResponse
from amsdal_server.apps.common.serializers.objects_response import ObjectsResponseContol
from amsdal_server.apps.transactions.router import router
from amsdal_server.apps.transactions.services.transaction_api import TransactionApi


@router.get('/api/transactions/')
async def transaction_list() -> ObjectsResponse:
    return TransactionApi.get_transactions()


@router.get('/api/transactions/{transaction_name}/')
async def transaction_detail(transaction_name: str) -> ObjectsResponseContol:
    return TransactionApi.get_transaction(transaction_name)

from typing import Any

from amsdal.services.transaction_execution import TransactionExecutionService

from amsdal_server.apps.common.errors import AmsdalTransactionError


class TransactionExecutionApi:
    @classmethod
    def execute_transaction(
        cls,
        transaction_name: str,
        args: dict[Any, Any],
    ) -> Any:
        execution_service = TransactionExecutionService()

        try:
            return execution_service.execute_transaction(
                transaction_name=transaction_name,
                args=args,
                load_references=True,
            )
        except TypeError as e:
            msg = str(f'Invalid arguments: {e}')

            raise AmsdalTransactionError(transaction_name=transaction_name, error_message=msg) from e

import ast
import types
from collections.abc import Generator
from enum import Enum
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Any

from amsdal.configs.main import settings
from amsdal.contrib.frontend_configs.lifecycle.consumer import core_to_frontend_types
from amsdal_models.classes.model import Model
from amsdal_models.schemas.enums import CoreTypes
from pydantic import BaseModel

from amsdal_server.apps.transactions.serializers.transaction_item import TransactionItemSerializer
from amsdal_server.apps.transactions.serializers.transaction_property import DictTypeSerializer
from amsdal_server.apps.transactions.serializers.transaction_property import TransactionPropertySerializer
from amsdal_server.apps.transactions.serializers.transaction_property import TypeSerializer
from amsdal_server.apps.transactions.utils import is_transaction


class AstParserMixin:
    @classmethod
    def _get_transaction_definitions(cls) -> Generator[tuple[ast.FunctionDef | ast.AsyncFunctionDef, Path], None, None]:
        transactions_path: Path = cls._get_transactions_path()
        yield from cls._iterate_module(transactions_path)

    @classmethod
    def _iterate_module(
        cls, module_path: Path
    ) -> Generator[tuple[ast.FunctionDef | ast.AsyncFunctionDef, Path], None, None]:
        if not module_path.exists():
            return

        elif module_path.is_dir():
            for file in module_path.iterdir():
                yield from cls._iterate_module(file)
        elif module_path.suffix == '.py':
            yield from cls._iterate_file(module_path)

    @classmethod
    def _iterate_file(
        cls, file_path: Path
    ) -> Generator[tuple[ast.FunctionDef | ast.AsyncFunctionDef, Path], None, None]:
        transactions_content = file_path.read_text()
        tree = ast.parse(transactions_content)

        for definition in ast.walk(tree):
            if not is_transaction(definition):
                continue

            yield definition, file_path  # type: ignore[misc]

    @classmethod
    def build_transaction_item(
        cls,
        definition: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> TransactionItemSerializer:
        transaction_item = TransactionItemSerializer(
            title=definition.name,
            properties={},
        )

        for arg in definition.args.args:
            if hasattr(arg.annotation, 'id'):
                transaction_item.properties[arg.arg] = TransactionPropertySerializer(
                    title=arg.arg,
                    type=cls._normalize_type(arg.annotation.id),  # type: ignore[union-attr]
                )
            elif hasattr(arg.annotation, 'value'):
                if arg.annotation.value.id.lower() == 'list':  # type: ignore[union-attr]
                    transaction_item.properties[arg.arg] = TransactionPropertySerializer(
                        title=arg.arg,
                        type=CoreTypes.ARRAY.value,
                        items=TypeSerializer(
                            type=cls._normalize_type(arg.annotation.slice.id),  # type: ignore[union-attr]
                        ),
                    )
                elif arg.annotation.value.id.lower() == 'dict':  # type: ignore[union-attr]
                    transaction_item.properties[arg.arg] = TransactionPropertySerializer(
                        title=arg.arg,
                        type=CoreTypes.ARRAY.value,
                        items=DictTypeSerializer(
                            key=TypeSerializer(
                                type=cls._normalize_type(arg.annotation.slice.elts[0].id),  # type: ignore[union-attr]
                            ),
                            value=TypeSerializer(
                                type=cls._normalize_type(arg.annotation.slice.elts[1].id),  # type: ignore[union-attr]
                            ),
                        ),
                    )
                elif arg.annotation.value.id.lower() == 'optional':  # type: ignore[union-attr]
                    transaction_item.properties[arg.arg] = TransactionPropertySerializer(
                        title=arg.arg,
                        type=CoreTypes.ANYTHING.value,
                    )
                else:
                    msg = 'Error parsing annotation with value and no id attribute is not expected...'
                    raise ValueError(msg)
            else:
                transaction_item.properties[arg.arg] = TransactionPropertySerializer(
                    title=arg.arg,
                    type=CoreTypes.ANYTHING.value,
                )

        return transaction_item

    @classmethod
    def _get_transactions_path(cls) -> Path:
        return settings.models_root_path / 'transactions'

    @classmethod
    def _normalize_type(cls, json_or_py_type: str) -> str:
        json_switcher = {
            CoreTypes.STRING.value: 'str',
            CoreTypes.NUMBER.value: 'float',
            CoreTypes.ANYTHING.value: 'Any',
            CoreTypes.BOOLEAN.value: 'bool',
            CoreTypes.BINARY.value: 'bytes',
            CoreTypes.ARRAY.value: 'list',
        }
        py_switcher = {
            'str': CoreTypes.STRING.value,
            'int': CoreTypes.NUMBER.value,
            'float': CoreTypes.NUMBER.value,
            'Any': CoreTypes.ANYTHING.value,
            'bool': CoreTypes.BOOLEAN.value,
            'bytes': CoreTypes.BINARY.value,
            'List': CoreTypes.ARRAY.value,
            'list': CoreTypes.ARRAY.value,
        }

        return json_switcher.get(json_or_py_type, py_switcher.get(json_or_py_type, json_or_py_type))

    @classmethod
    def build_frontend_control(
        cls,
        definition: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
    ) -> dict[str, Any]:
        controls = []
        for arg in definition.args.args:
            controls.append(cls.build_sub_frontend_control(arg, file_path))

        return {
            'name': definition.name,
            'type': 'group',
            'controls': controls,
        }

    @classmethod
    def _to_control(cls, argument: ast.Name, file_path: Path) -> dict[str, Any]:
        normalized_type = cls._normalize_type(argument.id)
        if normalized_type in core_to_frontend_types:
            return {
                'type': core_to_frontend_types[normalized_type],
            }
        else:
            loader = SourceFileLoader(file_path.stem, str(file_path.absolute()))
            transaction_module = types.ModuleType(loader.name)
            loader.exec_module(transaction_module)
            value = getattr(transaction_module, argument.id)

            if issubclass(value, Model):
                return {
                    'type': 'object_latest',
                    'entityType': argument.id,
                }
            elif issubclass(value, BaseModel):
                # TODO: refactor into group
                return {
                    'type': 'dict',
                    'control': {
                        'type': 'text',
                        'label': 'Text Input',
                        'name': 'text',
                    },
                }
            elif issubclass(value, Enum):
                return {
                    'type': 'text',
                    'options': [{'label': option.name, 'value': option.value} for option in value],
                }
        return {}

    @classmethod
    def build_sub_frontend_control(cls, argument: ast.arg, file_path: Path) -> dict[str, str]:
        argument_control = {
            'name': argument.arg,
            'label': argument.arg,
        }

        if hasattr(argument.annotation, 'id'):
            argument_control.update(cls._to_control(argument.annotation, file_path))  # type: ignore[arg-type]

        elif isinstance(argument.annotation, ast.BinOp):
            if isinstance(argument.annotation.left, ast.Name):
                argument_control.update(cls._to_control(argument.annotation.left, file_path))

            if isinstance(argument.annotation.right, ast.Name):
                argument_control.update(cls._to_control(argument.annotation.right, file_path))

        elif isinstance(argument.annotation, ast.Subscript):
            if argument.annotation.value.id == 'Optional':  # type: ignore[attr-defined]
                argument_control.update(cls._to_control(argument.annotation.slice, file_path))  # type: ignore[arg-type]
        elif argument.annotation is None:
            argument_control.update({'type': 'text'})

        return argument_control

from typing import Any
from typing import Optional

from pydantic import Field

from amsdal_server.apps.common.serializers.base_serializer import SkipNoneBaseModel
from amsdal_server.apps.common.serializers.column_format import ColumnFormat
from amsdal_server.apps.common.serializers.option import Option
from amsdal_server.apps.common.serializers.validator import Validator


class ColumnInfo(SkipNoneBaseModel):
    type: str | None = None
    value: str | None = None
    key: str | None = None
    label: str | None = None
    description: str | None = None
    order: int | None = None
    options: list[Option] | None = None
    cell_template_name: str | None = Field(None, alias='cellTemplateName')
    control: dict[str, Any] | None = None
    validation: list[Validator] | None = None
    column_format: ColumnFormat | None = None
    items: dict[str, Any] | None = None
    next_control: str | None = None
    head_control: str | None = None
    read_only: bool | None = None
    required: bool | None = None
    attributes: list['ColumnInfo'] | None = None
    array_type: str | None = None
    dict_type: str | None = None
    item_format: Optional['ColumnInfo'] = None

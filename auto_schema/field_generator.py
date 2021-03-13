from sqlalchemy.orm.attributes import InstrumentedAttribute
from typing import Dict, Any
from marshmallow_enum import EnumField
from .fields import BytesField
from .utils import check_column_is_nullable


class BaseGenerator(object):
    def __call__(self, column: InstrumentedAttribute, dict_to_update: Dict[str, Any]):
        raise NotImplementedError()


class EnumFieldGenerator(BaseGenerator):
    def __call__(self, column: InstrumentedAttribute, dict_to_update: Dict[str, Any]):
        required = not check_column_is_nullable(column)

        col = column.property.columns[0]
        dict_to_update[column.property.key] = EnumField(col.type.python_type, required=required)


# TODO: Dynamic on required
class BytesFieldGenerator(BaseGenerator):
    def __call__(self, column: InstrumentedAttribute, dict_to_update: Dict[str, Any]):
        required = not check_column_is_nullable(column)
        dict_to_update[column.property.key] = BytesField(required=required, allow_none=True)

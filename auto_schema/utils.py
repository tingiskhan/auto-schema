from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from typing import Dict, List, Union, Any


def get_columns_of_property_type(base, prop_type=ColumnProperty):
    res = (c for c in vars(base).values() if isinstance(c, InstrumentedAttribute))

    if prop_type is None:
        return list(res)

    return [c for c in res if isinstance(c.property, prop_type)]


def find_col_types(base, type_):
    return [c for c in get_columns_of_property_type(base) if isinstance(c.property.columns[0].type, type_)]


def check_column_is_nullable(column: InstrumentedAttribute):
    if len(column.property.columns) != 1:
        raise ValueError(f"Can only handle when columns == 1!")

    return column.property.columns[-1].nullable


def map_model(relation_columns: List[RelationshipProperty], data: Union[Dict[str, Any], List[Dict[str, Any]]]):
    base_class = relation_columns[0].class_

    for relation_column in relation_columns:
        key = relation_column.key

        popped = data.pop(key, None)
        if popped is None or not any(popped):
            continue

        mapped_class = relation_column.property.mapper.class_
        rel_columns = get_columns_of_property_type(mapped_class, prop_type=RelationshipProperty)

        if not any(rel_columns):
            temp = {key: mapped_class(**popped) if isinstance(popped, dict) else [mapped_class(**p) for p in popped]}
        else:
            temp = {key: map_model(rel_columns, popped)}

        data.update(temp)

    return base_class(**data)

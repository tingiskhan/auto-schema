# Auto-schema
Library for programmatically generating `marshmallow` schemas based on
`SQLAlchemy` models. Similar to [pydantic-sqlalchemy](https://github.com/tiangolo/pydantic-sqlalchemy).

```python
from auto_schema import AutoMarshmallowSchema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Enum as EnumCol, Date 
from enum import Enum
from datetime import date

class TaskType(Enum):
    Note = "Note"
    Task = "Task"


Base = declarative_base()


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    finished_by = Column(Date, nullable=False)
    type = Column(EnumCol(TaskType, create_constraint=False, native_enum=False), nullable=False)


TaskSchema = AutoMarshmallowSchema.generate_schema(Task)

task = Task(id=1, name="Test", finished_by=date.today(), type=TaskType.Task)

dumped_task = TaskSchema().dump(task)

print(dumped_task)
```

## Requirements
The library requires the following packages

* `SQLAlchemy`
* `marshmallow`
* `marshmallow-enum`
* `marshmallow-sqlalchemy`

import unittest
from datetime import date
from auto_schema import AutoMarshmallowSchema
from test.model import Task, TaskWithRelationShip, TaskType, Attachment


class SchemaTests(unittest.TestCase):
    def test_GenerateSchema(self):
        schema = AutoMarshmallowSchema.generate_schema(Task)

        self.assertEqual(Task, schema.Meta.model)

    def test_DumpModel(self):
        schema = AutoMarshmallowSchema.generate_schema(Task)

        task = Task(id=1, name="Test", finished_by=date.today(), type=TaskType.Task)
        dumped_task = schema().dump(task)

        expected = {
            "id": task.id,
            "name": task.name,
            "finished_by": task.finished_by.isoformat(),
            "type": task.type.name
        }

        self.assertEqual(dumped_task, expected)

    def test_LoadModel(self):
        schema = AutoMarshmallowSchema.generate_schema(Task)

        task = Task(id=1, name="Test", finished_by=date.today(), type=TaskType.Task)
        dumped_task = schema().dump(task)

        loaded = schema().load(dumped_task)

        for k, v in vars(task).items():
            if k.startswith("_"):
                continue

            self.assertEqual(v, loaded[k])

    def test_SchemaWithRelationShip(self):
        schema = AutoMarshmallowSchema.generate_schema(TaskWithRelationShip)

        attachment = Attachment(id=1, task_id=1, location="Here")

        task_with_relationship = TaskWithRelationShip(id=1, name="Test", finished_by=date.today(), type=TaskType.Task)
        task_with_relationship.attachments = [attachment]

        expected = {
            "id": task_with_relationship.id,
            "name": task_with_relationship.name,
            "finished_by": task_with_relationship.finished_by,
            "type": task_with_relationship.type,
            "attachments": [
                {
                    "id": attachment.id,
                    "task_id": attachment.task_id,
                    "location": attachment.location
                }
            ]
        }

        dumped = schema().dump(task_with_relationship)
        loaded = schema().load(dumped)

        self.assertEqual(expected, loaded)

    def verify_objects(self, expected, received):
        for k, v in vars(expected).items():
            if k.startswith("_"):
                continue

            r_val = getattr(received, k)
            if not isinstance(v, list):
                self.assertEqual(v, r_val)
            else:
                self.verify_objects(v, r_val)

    def test_SchemaLoadInstance(self):
        schema = AutoMarshmallowSchema.generate_schema(TaskWithRelationShip)()

        attachment = Attachment(id=1, task_id=1, location="Here")

        task_with_relationship = TaskWithRelationShip(id=1, name="Test", finished_by=date.today(), type=TaskType.Task)
        task_with_relationship.attachments = [attachment]

        dumped = schema.dump(task_with_relationship)

        loaded = schema.load_instance(dumped)
        self.verify_objects(task_with_relationship, loaded)

    def test_SchemaWithRelationshipNoData(self):
        schema = AutoMarshmallowSchema.generate_schema(TaskWithRelationShip)()

        task_with_relationship = TaskWithRelationShip(id=1, name="Test", finished_by=date.today(), type=TaskType.Task)

        dumped = schema.dump(task_with_relationship)

        loaded = schema.load_instance(dumped)
        self.verify_objects(task_with_relationship, loaded)


if __name__ == '__main__':
    unittest.main()

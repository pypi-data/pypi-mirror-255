from typing import Optional

from sqlalchemy_gql.orm_base import ModelBase, DatabaseManager


class Person(ModelBase):
    name: Optional[str] = None
    age: int = None

    def __init__(self, name: str = None, age: int = None):
        super().__init__()

        self.name = name
        self.age = age


# noinspection DuplicatedCode
class TestModel:

    def test_create(self):
        db_manager = DatabaseManager(wipe=True)

        def create_person(expected_people_count):
            person = Person(name="rob", age=26)
            person.create()

            all_people = Person.query().all()
            assert len(all_people) == expected_people_count

        db_manager.with_db_session(create_person)(1)

        db_manager.setup()

        db_manager.with_db_session(create_person)(2)

        db_manager.setup(wipe=True)

        db_manager.with_db_session(create_person)(1)

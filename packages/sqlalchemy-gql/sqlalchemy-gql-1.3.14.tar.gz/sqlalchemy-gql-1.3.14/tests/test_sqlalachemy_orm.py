from typing import Optional

from graphql_api import GraphQLAPI

from sqlalchemy_gql.orm_base import ModelBase, DatabaseManager


class Individual(ModelBase):
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

        def create_person():
            person = Individual(name="rob", age=26)
            person.create()

            all_people = Individual.query().all()
            assert len(all_people) == 1
            assert all_people == [person]

        db_manager.with_db_session(create_person)()

    def test_delete(self):
        db_manager = DatabaseManager(wipe=True)

        def delete_person():
            person = Individual(name="rob", age=26)
            person.create()

            all_people = Individual.query().all()
            assert len(all_people) == 1
            assert all_people == [person]

            person.delete()

            all_people = Individual.query().all()
            assert len(all_people) == 0

        db_manager.with_db_session(delete_person)()

    def test_filter(self):
        db_manager = DatabaseManager()

        def delete_person():
            person = Individual(name="rob", age=26)
            person.create()

            all_people = Individual.query().all()
            assert len(all_people) == 1
            assert all_people == [person]

            person.delete()

            all_people = Individual.query().all()
            assert len(all_people) == 0

        db_manager.with_db_session(delete_person)()

    def test_schema(self):

        schema = GraphQLAPI()

        @schema.type(root=True)
        class Root:

            @schema.field
            def person(self) -> Individual:
                return Individual(name="rob", age=26)

        gql_query = '''
            query GetPerson {
                person {
                    name
                    age
                }
            }
        '''

        result = schema.executor().execute(gql_query)

        expected = {
            "person": {
                "name": "rob",
                "age": 26
            }
        }

        assert expected == result.data

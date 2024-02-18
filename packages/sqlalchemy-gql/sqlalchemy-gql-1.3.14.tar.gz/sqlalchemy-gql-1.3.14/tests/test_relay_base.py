from uuid import UUID

from graphql_api import GraphQLAPI


# noinspection DuplicatedCode
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_orm import UUIDType

from sqlalchemy_gql.orm_base import RelayBase
from sqlalchemy_gql.mixin import GraphQLSQLAlchemyMixin


class TestModel:

    def test_basic(self):
        Base = declarative_base()

        from sqlalchemy import Column, Integer, String

        class Person(GraphQLSQLAlchemyMixin, Base):
            __tablename__ = 'people'
            id = Column(Integer, primary_key=True)
            name = Column(String)
            age = Column(Integer)

        ed = Person(name='ed', age=55)

        schema = GraphQLAPI()

        @schema.type(root=True)
        class Root:

            @schema.field
            def person(self) -> Person:
                return ed

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
                "name": "ed",
                "age": 55
            }
        }

        assert expected == result.data

    def test_relay(self):

        engine = create_engine('sqlite:///:memory:', echo=True)
        Base = declarative_base()

        class Person(RelayBase, Base):
            __tablename__ = "person"
            id = Column(UUIDType, primary_key=True)
            name = Column(String)
            age = Column(Integer)

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        ed = Person(name='ed', age=55)
        session.add(ed)

        schema = GraphQLAPI()

        @schema.type(root=True)
        class Root:

            @schema.field
            def person(self, id: UUID) -> Person:
                return session.query(Person).filter_by(id=id).first()

        gql_query = f'''
            query GetPerson {{
                person(id: "{str(ed.id)}") {{
                    id
                    name
                    age
                }}
            }}
        '''

        result = schema.executor().execute(gql_query)

        expected = {
            "person": {
                "id": str(ed.id),
                "name": "ed",
                "age": 55
            }
        }

        assert expected == result.data

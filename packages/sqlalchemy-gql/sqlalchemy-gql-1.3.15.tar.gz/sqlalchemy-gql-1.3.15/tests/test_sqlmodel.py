from graphql_api import GraphQLAPI

from sqlalchemy_gql import GraphQLSQLAlchemyMixin


class TestSQLModel:

    def test_sqlmodel(self):

        from typing import Optional

        from sqlmodel import Field, Session, SQLModel, create_engine, select

        class Hero(GraphQLSQLAlchemyMixin, SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            name: str
            real_name: str
            age: Optional[int] = None

        engine = create_engine("sqlite:///database.db")
        SQLModel.metadata.create_all(engine)

        spiderman = Hero(name="Spiderman", real_name="Peter Parker")
        batman = Hero(name="Batman", real_name="Bruce Wayne")

        with Session(engine) as session:
            session.add(spiderman)
            session.add(batman)

            session.commit()
            session.close()

        schema = GraphQLAPI()

        @schema.type(root=True)
        class Root:

            @schema.field
            def hero(self, name: str) -> Optional[Hero]:
                with Session(engine) as session:
                    statement = select(Hero).where(Hero.name == name)
                    return session.exec(statement).first()

        gql_query = '''
                query GetBatman {
                    hero(name:"Batman") {
                        realName
                    }
                }
            '''

        result = schema.executor().execute(gql_query)
        assert "Bruce Wayne" == result.data["hero"]["realName"]

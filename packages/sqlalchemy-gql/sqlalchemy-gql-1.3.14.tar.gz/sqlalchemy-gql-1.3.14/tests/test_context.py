from context_helper import Context

from sqlalchemy_gql import DatabaseManager, ModelBase


class TestContent:

    def test_content(self):

        db_manager = DatabaseManager(wipe=True)

        from sqlalchemy import Column, Integer, String

        class Thing(ModelBase):
            __tablename__ = 'thing'
            id = Column(Integer, primary_key=True)
            name = Column(String)
            age = Column(Integer)

        db_manager.db.create(Thing)

        db_session = db_manager.db.session()

        with Context(db_session=db_session):
            thing = Thing(
                id=1,
                name="rob",
                age=10
            )
            thing.create()

            db_session.rollback()

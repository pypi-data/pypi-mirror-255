import logging
import uuid

from typing import Callable, Optional

from context_helper import Context, ctx
from graphql_api import GraphQLAPI

try:
    from sqlalchemy_orm import Database, TypeMapper, EnumType, UUIDType
    from sqlalchemy_orm.base.base import Model
    from sqlalchemy_orm.query import Query

except ImportError:
    raise ImportError("SQLAlchemy_ORM package not found")


from sqlalchemy_utils import create_database, database_exists

from sqlalchemy_gql.relay_base import RelayBase


Base = Model(type_map=TypeMapper(types=[EnumType, UUIDType]))


@GraphQLAPI.type(abstract=True)
class ModelBase(RelayBase, Base):
    id: uuid.UUID

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__()

    @classmethod
    def query(cls, session=None) -> Query:
        if session is None:
            if ctx.db_session is None:
                raise AttributeError(
                    "db_session not set in the current context"
                )
            return ctx.db_session.query(cls)

        return super().query(session=session)

    @classmethod
    def filter(cls, *args, session=None, **kwargs) -> Query:
        query = cls.query(session=session)
        if args:
            query = query.filter(*args)
        if kwargs:
            query = query.filter_by(**kwargs)

        return query

    @classmethod
    def get(cls, id: uuid.UUID = None, session=None) -> Optional['Base']:
        if id:
            return cls.filter(id=id, session=session).one_or_none()

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"<{self.__class__.__name__} id: '{str(self.id)[:4]}'>"

    def create(self, session=None) -> bool:
        if session is None:
            session = ctx.db_session

        session.add(self)
        return True

    def delete(self, session=None) -> bool:
        if session is None:
            session = ctx.db_session

        session.delete(self)
        return True


class DatabaseManager:

    def __init__(
            self,
            url: str = "sqlite:///pool.db",
            install: bool = True,
            wipe: bool = False
    ):
        self.logger = logging.getLogger("db")
        self.logger.info(f"Connecting DatabaseService with url {url}")

        self.url = url
        self.base = ModelBase
        self.db: Optional[Database] = None

        self.setup(install=install, wipe=wipe)

    def setup(self, install: bool = True, wipe: bool = False):
        if install:
            if not database_exists(self.url):
                create_database(self.url)

        self.db = Database(self.url)

        if install:
            if not self.db.is_empty():
                if wipe:
                    self.logger.info(f"Wiping db '{self.db}'")
                    self.db.wipe()
                else:
                    self.logger.warning(
                        f"Attempting install to a db '{self.db}' "
                        f"that is not empty."
                    )

            self.logger.info("Creating tables.")

            # Create tables
            self.db.create_all(self.base)

    def with_db_session(
            self,
            func: Callable = None,
            context_key_name="db_session"
    ):
        """
        Create a db session, then wrap `func`
        in a new context so it can access the db session.
        """
        def with_context(*args, **kwargs):
            db_session = self.db.session()
            response = None

            try:
                with Context(**{context_key_name: db_session}):
                    response = func(*args, **kwargs)

            except Exception as err:
                db_session.rollback()
                raise err
            else:
                db_session.commit()
            finally:
                db_session.close()

            return response

        return with_context

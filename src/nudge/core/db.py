import flask_sqlalchemy
import sqlalchemy as sa

from nudge.core.entity import Orm


class Database:

    def __init__(self, log, db_uri):
        self._db_uri = db_uri
        self._db = flask_sqlalchemy.SQLAlchemy()
        self._log = log

    @property
    def _session(self):
        return self._db.session

    @property
    def _engine(self):
        return self._db.engine

    def init_app(self, app):
        app.config.update(
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_DATABASE_URI=self._db_uri,
        )

        self._db.init_app(app)

    def recreate_tables(self):
        self.drop_tables()
        self.create_tables()

    def create_tables(self):
        self._log.info('Creating tables')
        Orm.metadata.create_all(bind=self._engine)

    def drop_tables(self):
        self._log.info('Dropping tables')
        # reflect to include tables not defined in code
        meta = sa.MetaData()
        meta.reflect(bind=self._engine)
        for table in reversed(meta.sorted_tables):
            self._log.info('Dropping table: {}'.format(table.name))
            table.drop(bind=self._engine)

    def add(self, entity):
        self._session.add(entity.orm)
        return entity

    def commit(self):
        self._session.commit()

    def query(self, *args, **kwargs):
        return self._session.query(*args, **kwargs)

    def flush(self):
        self._session.flush()

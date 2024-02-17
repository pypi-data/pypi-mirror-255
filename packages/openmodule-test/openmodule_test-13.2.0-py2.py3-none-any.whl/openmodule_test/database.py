import os
import shutil
from glob import glob
from unittest import TestCase

from alembic import command
from alembic.runtime.migration import MigrationContext
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base

from openmodule.config import settings
from openmodule.database.database import Database, database_path, alembic_config

_first_start = True


def truncate_all_tables(database: Database, keep=("alembic_version",)):
    assert any(x in database.db_folder for x in ["/test/"]), "deleting all tables is only for testing"
    metadata = MetaData(bind=database._engine)
    metadata.reflect()
    with database._engine.connect() as con:
        trans = con.begin()
        for table in reversed(metadata.sorted_tables):
            if table.name not in keep:
                con.execute(table.delete())
        trans.commit()


class SQLiteTestMixin(TestCase):
    """
    Mixin for database cleanup in test cases
    * use create_database = True for an automatic generation of a database
    * use create_database = False and set the database directly
    """
    create_database = True
    database = None
    database_folder: str = None  # defaults to settings.DATABASE_FOLDER
    alembic_path = "../src/database"
    database_name = "database"

    @classmethod
    def get_database_folder(cls):
        return cls.database_folder or settings.DATABASE_FOLDER

    @classmethod
    def setUpClass(cls) -> None:
        # we only know which databases are in use on tear down, so truncating only works in teardown
        # but in order to not be annoyed by failed tests which left broken databases, we delete all databases
        # once initially
        global _first_start
        if _first_start:
            for file in glob(os.path.join(cls.get_database_folder(), "*.sqlite3")):
                os.unlink(file)
            _first_start = False
        if cls.create_database:
            cls.database = Database(cls.get_database_folder(), cls.database_name, cls.alembic_path)
        return super().setUpClass()

    @staticmethod
    def delete_database(database: Database):
        assert not database.is_open(), "database must be shutdown before it can be deleted"
        try:
            os.unlink(database_path(database.db_folder, database.name))
        except FileNotFoundError:
            pass

    def tearDown(self):
        super().tearDown()
        if self.create_database:
            truncate_all_tables(self.database)

    @classmethod
    def tearDownClass(cls):
        if cls.create_database:
            cls.database.shutdown()
            os.unlink(database_path(cls.get_database_folder(), cls.database_name))
        super().tearDownClass()


class AlembicMigrationTestMixin(SQLiteTestMixin):
    """
    Mixin for testing alembic migrations (up & down)
    **DO NOT** import your database models in migration testcases, as the Models don't necessarily
        match the database schema.
    Set existing_database to the *.sqlite3 file you want to use for testing. **DO NOT** place your test database
        in the <project_root>/sqlite/ folder, as it will be deleted in some cases.
    This will copy the existing_database to the test database folder to ensure that the database is not modified.
    create_database must be set to True, otherwise it is assumed that the programmer manages the database themselves.
    """
    existing_database = None

    def setUp(self):
        self.base = automap_base()
        if self.create_database:
            if self.existing_database:
                shutil.copyfile(self.existing_database, database_path(self.get_database_folder(), self.database_name))
            else:
                metadata = MetaData()
                metadata.reflect(bind=self.connection)
                metadata.drop_all(bind=self.connection)
        super().setUp()
        if self.database:
            self.reload_models()

    @property
    def connection(self):
        return self.database._engine

    def reload_models(self):
        self.base = automap_base()
        self.base.prepare(self.connection, reflect=True)

    def alembic_config(self):
        alembic_path = self.alembic_path or os.path.join(os.getcwd(), "database")
        assert os.path.exists(
            os.path.abspath(alembic_path)), f"alembic path {os.path.abspath(alembic_path)} does not exist"
        return alembic_config(self.connection, alembic_path)

    def migrate_up(self, revision="head"):
        config = self.alembic_config()
        command.upgrade(config, revision)
        assert self.connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign keys are not enabled"
        self.reload_models()

    def migrate_down(self, revision="base"):
        config = self.alembic_config()
        command.downgrade(config, revision)
        assert self.connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign keys are not enabled"
        self.reload_models()

    def current_revision(self):
        with self.connection.connect() as con:
            context = MigrationContext.configure(con)
            return context.get_current_revision()

    def get_model(self, name):
        return getattr(self.base.classes, name)

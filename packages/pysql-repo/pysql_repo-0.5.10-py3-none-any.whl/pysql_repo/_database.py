# MODULES
from typing import Any, Generator, List, Optional
from pathlib import Path
from logging import Logger

# SQLALCHEMY
from sqlalchemy import text, MetaData, create_engine, Table
from sqlalchemy.orm import DeclarativeMeta, Session, sessionmaker
from sqlalchemy.inspection import inspect

# CONTEXTLIB
from contextlib import contextmanager

# UTILS
from pysql_repo._database_base import (
    Database as _Database,
    DataBaseConfigTypedDict as _DataBaseConfigTypedDict,
)


class DataBase(_Database):
    """
    Represents a database connection and provides methods for database operations.

    Args:
        _database_config (DataBaseConfigTypedDict): The configuration for the databases.
        _engine: (Engine): The engine used for database operations.
        _logger (Logger): An instance of the logger to use for logging.
        _base (DeclarativeMeta): The base class for the database models.
        _metadata_views (Optional[List[MetaData]]): Optional list of metadata views.
        _session_factory (sessionmaker[Session]): The factory for creating sessions.
        _views (List[Table]): The list of metadata views.

    Methods:
        views: Get the list of views in the database.
        ini: Get the 'ini' property from the database configuration.
        init_database_dir_json: Get the 'init_database_dir_json' property from the database configuration.
        _pre_process_data_for_initialization: Pre-processes the data for initialization.
        _get_pre_process_data_for_initialization: Gets the pre-processed data for initialization.
        _get_ordered_tables: Gets the ordered tables based on the given table names.
        create_database: Creates the database by dropping existing views and creating tables and views.
        session_factory: Context manager for creating a session.
        init_tables_from_json_files: Initializes tables from JSON files.
    """

    def __init__(
        self,
        databases_config: _DataBaseConfigTypedDict,
        logger: Logger,
        base: DeclarativeMeta,
        metadata_views: Optional[List[MetaData]] = None,
        autoflush: bool = False,
        expire_on_commit: bool = False,
        echo: bool = False,
    ) -> None:
        """
        Initialize a new instance of the _Database class.

        Args:
            databases_config (_DataBaseConfigTypedDict): A dictionary containing the configuration for the databases.
            logger (Logger): The logger object to be used for logging.
            base (DeclarativeMeta): The base class for the declarative models.
            metadata_views (List[MetaData] | None, optional): A list of metadata views. Defaults to None.
        """
        super().__init__(databases_config, logger, base, metadata_views)

        self._engine = create_engine(
            self._database_config.get("connection_string"),
            echo=echo,
            connect_args=self._database_config.get("connect_args") or {},
        )

        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
        )

    def create_database(self) -> None:
        """
        Creates the database by dropping existing views and creating all tables and views defined in the metadata.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the database creation process.
        """
        insp = inspect(self._engine)
        current_view_names = [item.lower() for item in insp.get_view_names()]

        with self.session_factory() as session:
            for view in self.views:
                if view.key.lower() in current_view_names:
                    session.execute(text(f"DROP VIEW {view}"))

        self._base.metadata.create_all(self._engine)

    @contextmanager
    def session_factory(self) -> Generator[Session, Any, None]:
        """
        Context manager for creating a session.

        Yields:
            Session: The session object.

        Raises:
            Exception: If an error occurs during the session creation process.
        """
        session = self._session_factory()
        try:
            yield session
        except Exception as ex:
            self._logger.error("Session rollback because of exception", exc_info=ex)
            session.rollback()
            raise
        finally:
            session.close()

    def init_tables_from_json_files(
        self,
        directory: Path,
        table_names: List[str],
        timezone="CET",
    ) -> List[Table]:
        """
        Initializes tables in the database by inserting data from JSON files.

        Args:
            directory (Path): The directory containing the JSON files.
            table_names (List[str]): A list of table names to initialize.
            timezone (str): The timezone to use for date and time values. Defaults to "CET".

        Returns:
            list[Table]: The ordered list of tables that were initialized.

        Raises:
            Exception: If an error occurs during the initialization process.
        """
        ordered_tables = self._get_ordered_tables(table_names=table_names)

        with self.session_factory() as session:
            for table in ordered_tables:
                path = directory / f"{(table_name := table.name.upper())}.json"

                raw_data = self._get_pre_process_data_for_initialization(
                    path=path,
                    timezone=timezone,
                )

                if raw_data is None:
                    continue

                session.execute(table.delete())
                session.execute(table.insert().values(raw_data))

                self._logger.info(
                    f"Successfully initialized {table_name=} from the file at {str(path)}."
                )

                session.commit()

        return ordered_tables

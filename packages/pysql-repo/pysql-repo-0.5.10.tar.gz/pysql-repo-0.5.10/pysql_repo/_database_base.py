# MODULES
import pytz
import re
from typing import Any, Dict, List, Optional, TypedDict
from pathlib import Path
from datetime import datetime
from logging import Logger

# SQLALCHEMY
from sqlalchemy import Table, MetaData
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.schema import sort_tables


# LIBS
from pysql_repo.libs.file_lib import open_json_file


from typing import Optional, Dict
from typing_extensions import TypedDict


class DataBaseConfigTypedDict(TypedDict):
    """
    Represents the configuration options for a database connection.

    Attributes:
        connection_string (str): The connection string for the database.
        ini (bool): Indicates whether an INI file is used for configuration.
        init_database_dir_json (Optional[str]): The directory path for initializing the database from a JSON file.
        connect_args (Optional[Dict]): Additional connection arguments for the database.
    """

    connection_string: str
    ini: bool
    init_database_dir_json: Optional[str]
    connect_args: Optional[Dict]


class Database:
    """
    Represents a database object.

    Attributes:
        _database_config (DataBaseConfigTypedDict): The configuration for the databases.
        _logger (Logger): The logger object for logging.
        _base (DeclarativeMeta): The base class for the database models.
        _metadata_views (Optional[List[MetaData]]): The list of metadata views.

    Methods:
        views: Get the list of views in the database.
        ini: Get the 'ini' property from the database configuration.
        init_database_dir_json: Get the 'init_database_dir_json' property from the database configuration.
        _pre_process_data_for_initialization: Pre-processes the data for initialization.
        _get_pre_process_data_for_initialization: Gets the pre-processed data for initialization.
        _get_ordered_tables: Gets the ordered tables based on the given table names.
    """

    def __init__(
        self,
        databases_config: DataBaseConfigTypedDict,
        logger: Logger,
        base: DeclarativeMeta,
        metadata_views: Optional[List[MetaData]] = None,
    ) -> None:
        """
        Initializes a Database object.

        Args:
            databases_config (DataBaseConfigTypedDict): The configuration for the databases.
            logger (Logger): The logger object for logging.
            base (DeclarativeMeta): The base class for the database models.
            metadata_views (Optional[List[MetaData]], optional): The list of metadata views. Defaults to None.
        """
        self._database_config = databases_config
        self._logger = logger
        self._base = base
        self._metadata_views = metadata_views

        self._views = [
            table
            for metadata in self._metadata_views or []
            for table in metadata.sorted_tables
        ]

    @property
    def views(self) -> List[Table]:
        """
        Get the list of views in the database.

        Returns:
            List[Table]: The list of views.
        """
        return self._views

    @property
    def ini(self) -> bool:
        """
        Get the 'ini' property from the database configuration.

        Returns:
            bool: The 'ini' property value.
        """
        return self._database_config.get("ini")

    @property
    def init_database_dir_json(self) -> Optional[str]:
        """
        Get the 'init_database_dir_json' property from the database configuration.

        Returns:
            Optional[str]: The 'init_database_dir_json' property value.
        """
        return self._database_config.get("init_database_dir_json")

    @classmethod
    def _pre_process_data_for_initialization(cls, data: Dict[str, Any], timezone: str):
        """
        Pre-processes the data for initialization.

        Args:
            data (Dict[str, Any]): The data to be pre-processed.
            timezone (str): The timezone to be used for conversion.

        Returns:
            Dict[str, Any]: The pre-processed data.
        """
        for key, value in data.items():
            if isinstance(value, str) and re.match(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?(Z|[+-]\d{2}:?\d{2})?",
                value,
            ):
                if value.endswith("Z"):
                    utc_dt = datetime.fromisoformat(value[:-1])
                    local_tz = pytz.timezone(timezone)
                    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
                    data[key] = local_dt
                else:
                    data[key] = datetime.fromisoformat(value)

        return data

    def _get_pre_process_data_for_initialization(
        self,
        path: Path,
        timezone: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Gets the pre-processed data for initialization.

        Args:
            path (Path): The path to the JSON file.
            timezone (str): The timezone to be used for conversion.

        Returns:
            Optional[List[Dict[str, Any]]]: The pre-processed data for initialization.
        """
        try:
            raw_data = open_json_file(path=path)
        except FileNotFoundError:
            self._logger.warning(
                f"Failed to initialize table due to the absence of the file at [{path}]."
            )

            return

        return [
            self._pre_process_data_for_initialization(
                data,
                timezone=timezone,
            )
            for data in raw_data
        ]

    def _get_ordered_tables(self, table_names: List[str]) -> List[Table]:
        """
        Gets the ordered tables based on the given table names.

        Args:
            table_names (List[str]): The list of table names.

        Returns:
            List[Table]: The ordered tables.

        Raises:
            ValueError: If 'ini' property is not available in the database configuration.
        """
        if not (init := self.ini):
            raise ValueError(
                f"Unable to init database tables because {init=} in config"
            )

        table_names = table_names or set()
        tables = {
            k: v for k, v in self._base.metadata.tables.items() if k in table_names
        }

        return sort_tables(tables.values())

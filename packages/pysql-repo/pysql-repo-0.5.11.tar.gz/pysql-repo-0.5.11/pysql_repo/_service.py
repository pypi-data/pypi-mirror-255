# MODULES
from typing import TypeVar, Generic
from logging import Logger

# CONTEXTLIB
from contextlib import AbstractContextManager

# SQLALCHEMY
from sqlalchemy.orm import Session

# MODELS
from pysql_repo._repository import Repository


_T = TypeVar("_T", bound=Repository)


class Service(Generic[_T]):
    """
    Represents a generic service class.

    Attributes:
        _repository: The repository object.
        _logger: The logger object.

    Methods:
        session_manager: Returns the session factory.
    """

    def __init__(
        self,
        repository: _T,
        logger: Logger,
    ) -> None:
        """
        Initializes the Service.

        Args:
            repository: The repository object.
            logger: The logger object.
        """

        self._repository = repository
        self._logger = logger

    def session_manager(self) -> AbstractContextManager[Session]:
        """
        Returns the session manager from the repository.

        Returns:
            A session manager.
        """
        return self._repository.session_manager()

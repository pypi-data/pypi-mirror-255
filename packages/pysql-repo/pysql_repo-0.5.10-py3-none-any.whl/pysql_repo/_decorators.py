# MODULES
from typing import Any, Dict, List, Union

# SQLALCHEMY
from sqlalchemy.orm import Session


def check_values(as_list: bool = False):
    """
    Decorator that checks the validity of the 'values' argument passed to a function.

    Args:
        as_list (bool, optional): Specifies whether the 'values' argument should be a list of dictionaries or a single dictionary. Defaults to False.

    Raises:
        TypeError: If the 'values' argument is not of the expected type or format.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            values_attr: Union[Dict[str, Any], List[Dict[str, Any]]] = kwargs.get(
                "values", None
            )

            if as_list:
                if (
                    values_attr is None
                    or not isinstance(values_attr, list)
                    or len(values_attr) == 0
                    or not all(
                        isinstance(item, dict) and isinstance(key, str)
                        for item in values_attr
                        for key in item.keys()
                    )
                ):
                    raise TypeError(
                        "values expected to be a list of non-empty dictionary with string keys"
                    )
            else:
                if (
                    values_attr is None
                    or not isinstance(values_attr, dict)
                    or len(values_attr) == 0
                    or not all(isinstance(key, str) for key in values_attr.keys())
                ):
                    raise TypeError(
                        "values expected to be a non-empty dictionary with string keys"
                    )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def with_session(
    param_session: str = "session",
):
    """
    Decorator that provides a session to the decorated method.

    Args:
        param_session (str, optional): The name of the session parameter. Defaults to "session".

    Raises:
        TypeError: If the decorated object is not an instance of Repository or Service.
        TypeError: If the session is not an instance of Session.

    Returns:
        Callable: The decorated method.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not isinstance(self, (Repository, Service)):
                raise TypeError(
                    f"{self.__class__.__name__} must be instance of {Repository.__name__} or {Service.__name__}"
                )

            session = kwargs.get(param_session)

            if session is None:
                with self.session_manager() as session:
                    kwargs[param_session] = session
                    return func(self, *args, **kwargs)
            elif not isinstance(session, Session):
                raise TypeError(
                    f"{param_session} must be instance of {Session.__name__}"
                )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


from pysql_repo._repository import Repository
from pysql_repo._service import Service

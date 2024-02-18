# MODULES
import enum


class Operators(enum.Enum):
    """
    Enum class representing various operators used in SQL queries.
    """

    LIKE = "LIKE"
    NOT_LIKE = "NOT_LIKE"
    ILIKE = "ILIKE"
    NOT_ILIKE = "NOT_ILIKE"
    EQUAL = "EQUAL"
    IEQUAL = "IEQUAL"
    DIFFERENT = "DIFFERENT"
    IDIFFERENT = "IDIFFERENT"
    BETWEEN = "BETWEEN"
    BETWEEN_OR_EQUAL = "BETWEEN_OR_EQUAL"
    SUPERIOR = "SUPERIOR"
    SUPERIOR_OR_EQUAL = "SUPERIOR_OR_EQUAL"
    INFERIOR = "INFERIOR"
    INFERIOR_OR_EQUAL = "INFERIOR_OR_EQUAL"
    IN = "IN"
    IIN = "IIN"
    NOT_IN = "NOT_IN"
    NOT_IIN = "NOT_IIN"
    HAS = "HAS"
    ANY = "ANY"


class LoadingTechnique(enum.Enum):
    """
    Enum class representing different loading techniques.
    """

    CONTAINS_EAGER = "contains_eager"
    LAZY = "select"
    JOINED = "joined"
    SUBQUERY = "subquery"
    SELECTIN = "selectin"
    RAISE = "raise"
    NOLOAD = "noload"

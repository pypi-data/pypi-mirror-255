"""QueryResultSetType Class"""
from enum import Enum, auto


class ResultType(Enum):
    """Result type of DB select queries and Google API read functions"""
    PANDAS_DATA_FRAME = auto()
    JSON_LIST = auto()

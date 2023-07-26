import enum


class ScalarDataType(enum.Enum):
    LITHOLOGY = enum.auto()
    SCALAR_FIELD = enum.auto()
    VALUES = enum.auto()
    ALL = enum.auto()
    
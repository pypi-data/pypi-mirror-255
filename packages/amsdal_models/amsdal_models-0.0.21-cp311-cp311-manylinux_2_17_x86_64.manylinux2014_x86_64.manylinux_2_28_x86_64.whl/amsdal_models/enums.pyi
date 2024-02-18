from enum import Enum

class MetaClasses(str, Enum):
    TYPE: str
    CLASS_OBJECT: str

class BaseClasses(str, Enum):
    OBJECT: str
    CLASS_OBJECT: str

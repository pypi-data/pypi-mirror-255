from enum import Enum

class CoreTypes(str, Enum):
    NUMBER: str
    STRING: str
    BOOLEAN: str
    DICTIONARY: str
    ARRAY: str
    ANYTHING: str
    BINARY: str
    OBJECT: str

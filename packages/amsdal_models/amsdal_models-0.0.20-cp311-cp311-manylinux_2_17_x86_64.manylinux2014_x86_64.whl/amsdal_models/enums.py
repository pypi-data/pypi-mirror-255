from enum import Enum


class MetaClasses(str, Enum):
    TYPE = 'TypeMeta'
    CLASS_OBJECT = 'ClassObject'


class BaseClasses(str, Enum):
    OBJECT = 'Object'
    CLASS_OBJECT = 'ClassObject'

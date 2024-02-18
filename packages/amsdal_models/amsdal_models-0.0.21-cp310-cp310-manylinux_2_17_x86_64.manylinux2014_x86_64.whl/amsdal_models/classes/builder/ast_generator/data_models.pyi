from functools import cached_property as cached_property
from pydantic import BaseModel
from typing import Any, Optional, Union

class PropertyAst(BaseModel):
    name: str
    types: list[Union['NestedPropertyTypeAst', 'PropertyValueAst']]
    value: Optional['PropertyValueAst']
    @property
    def ast(self) -> Any: ...

class PropertyValueAst(BaseModel):
    attr: tuple[str, str] | None
    name: str | None
    constant: Any | None
    @property
    def ast(self) -> Any: ...

class NestedPropertyTypeAst(BaseModel):
    root: PropertyValueAst
    child: list['PropertyValueAst']
    @property
    def ast(self) -> Any: ...

class CustomCodeAst(BaseModel):
    custom_code: str
    @cached_property
    def ast_module(self) -> Any: ...
    @property
    def ast(self) -> list[Any]: ...
    @property
    def ast_imports(self) -> list[Any]: ...

def join_property_values(items: list[Union['NestedPropertyTypeAst', 'PropertyValueAst']] | list['PropertyValueAst']) -> Any: ...

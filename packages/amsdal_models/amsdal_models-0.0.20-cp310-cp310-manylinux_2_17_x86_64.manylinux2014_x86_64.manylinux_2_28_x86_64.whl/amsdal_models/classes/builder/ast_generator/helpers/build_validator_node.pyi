import ast
from amsdal_models.classes.builder.ast_generator.dependency_generator import AstDependencyGenerator as AstDependencyGenerator
from collections.abc import Callable as Callable
from typing import Any

def build_validator_node(prop_name: str, validator_name: str, ast_dependency_generator: AstDependencyGenerator, validator: Callable[[type, Any], Any], options: list[Any] | None = ...) -> ast.FunctionDef | ast.stmt: ...

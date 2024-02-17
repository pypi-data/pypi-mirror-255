import ast
from _typeshed import Incomplete
from amsdal_models.classes.constants import CONTRIB_MODELS_MODULE as CONTRIB_MODELS_MODULE, CORE_MODELS_MODULE as CORE_MODELS_MODULE, USER_MODELS_MODULE as USER_MODELS_MODULE
from amsdal_models.classes.data_models.dependencies import DependencyItem as DependencyItem, DependencyModelNames as DependencyModelNames
from typing import Any

class AstDependencyGenerator:
    _ignore_type_names: Incomplete
    _models_module_name: Incomplete
    _model_names: Incomplete
    _dependencies: Incomplete
    def __init__(self, models_module_name: str, model_names: DependencyModelNames) -> None:
        '''
        Builds AST for imports statements.

        :param models_module_name: Name of the module where models are located, usually it has "models" value.
        :type models_module_name: str
        :param model_names: Information about all model names.
        :type model_names: DependencyModelNames
        '''
    @property
    def ast_module(self) -> ast.Module: ...
    def add_ignore_type_name(self, type_name: str) -> None:
        """
        Ignore some type names and do not add them to the dependencies.
        Probably in case of self reference types.
        :param type_name: the type name to ignore
        :type type_name: str
        :return:
        """
    def add_python_type_dependency(self, python_type: Any) -> None: ...
    def add_model_type_dependency(self, model_type: str) -> None: ...
    def add_ast_import_node(self, node: ast.Import | ast.ImportFrom) -> None: ...

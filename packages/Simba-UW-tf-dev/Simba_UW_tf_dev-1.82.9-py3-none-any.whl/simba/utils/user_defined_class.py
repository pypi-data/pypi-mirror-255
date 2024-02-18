
import os
import importlib.util
from pathlib import Path
import ast
import sys
from simba.utils.checks import check_file_exist_and_readable
from simba.utils.errors import InvalidFileTypeError, CountError
from simba.utils.read_write import get_fn_ext
from simba.utils.printing import stdout_warning
from typing import Union
import inspect
import subprocess

def check_if_module_has_import(parsed_file: ast.Module, import_name: str) -> bool:
    """
    Check if a Python module has a specific import statement.


    :parameter ast.Module file_path: The abstract syntax tree (AST) of the Python module.
    :parameter str import_name: The name of the module or package to check for in the import statements.
    :parameter bool: True if the specified import is found in the module, False otherwise.

    :example:
    >>> parsed_file = ast.parse(Path('/simba/misc/piotr.py').read_text())
    >>> check_if_module_has_import(parsed_file=parsed_file, import_name='argparse')
    >>> True
    """
    imports = [n for n in parsed_file.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    for i in imports:
        for name in i.names:
            if name.name == import_name:
                return True
    return False

def run_user_defined_feature_extraction_class(file_path: Union[str, os.PathLike],
                                              config_path: Union[str, os.PathLike]) -> None:
    """
    Loads and executes user-defined feature extraction class.

    :param file_path: Path to .py file holding user-defined feature extraction class.
    :param str config_path: Path to SimBA project config file.

    .. note::
       `Tutorial <https://github.com/sgoldenlab/simba/blob/master/docs/extractFeatures.md>`_.

       If the ``file_path`` contains multiple classes, then the first class will be used.

       The user defined class needs to contain a ``config_path`` init argument.

    :example:
    >>> run_user_defined_feature_extraction_class(config_path='/Users/simon/Desktop/envs/troubleshooting/circular_features_zebrafish/project_folder/project_config.ini', file_path='/Users/simon/Desktop/fish_feature_extractor_2023_version_5.py')
    """

    check_file_exist_and_readable(file_path=file_path)
    file_dir, file_name, file_extension = get_fn_ext(filepath=file_path)
    if file_extension != '.py':
        raise InvalidFileTypeError(msg=f'The user-defined feature extraction file ({file_path}) is not a .py file-extension', source=run_user_defined_feature_extraction_class.__name__)
    parsed = ast.parse(Path(file_path).read_text())
    classes = [n for n in parsed.body if isinstance(n, ast.ClassDef)]
    class_name = [x.name for x in classes]
    if len(class_name) < 1:
        raise CountError(msg=f'The user-defined feature extraction file ({file_path}) contains no python classes', source=run_user_defined_feature_extraction_class.__name__)
    if len(class_name) > 1:
        stdout_warning(msg=f'The user-defined feature extraction file ({file_path}) contains more than 1 python class. SimBA will use the first python class: {class_name[0]}.')
    class_name = class_name[0]
    spec = importlib.util.spec_from_file_location(class_name, file_path)
    user_module = importlib.util.module_from_spec(spec)
    sys.modules[class_name] = user_module
    spec.loader.exec_module(user_module)
    user_class = getattr(user_module, class_name)
    if 'config_path' not in inspect.signature(user_class).parameters:
        raise InvalidFileTypeError(msg=f'The user-defined class {class_name} does not contain a {config_path} init argument', source=run_user_defined_feature_extraction_class.__name__)
    functions = [n for n in parsed.body if isinstance(n, ast.FunctionDef)]
    function_names = [x.name for x in functions]
    has_argparse = check_if_module_has_import(parsed_file=parsed, import_name='argparse')
    has_main = any(isinstance(node, ast.If) and
                   isinstance(node.test, ast.Compare) and
                   isinstance(node.test.left, ast.Name) and
                   node.test.left.id == '__name__' and
                   isinstance(node.test.ops[0], ast.Eq) and
                   isinstance(node.test.comparators[0], ast.Str) and
                   node.test.comparators[0].s == '__main__'
                   for node in parsed.body)

    if 'main' in function_names and has_main and has_argparse:
        command = f'python "{file_path}" --config_path "{config_path}"'
        subprocess.call(command, shell=True)

    else:
        user_class(config_path)

# run_user_defined_feature_extraction_class(config_path='/Users/simon/Desktop/envs/troubleshooting/piotr/project_folder/train-20231108-sh9-frames-with-p-lt-2_plus3-&3_best-f1.ini',
#                                           file_path='/Users/simon/Desktop/envs/simba_dev/simba/feature_extractors/misc/piotr.py')

__author__ = "Simon Nilsson"

import configparser
import trafaret as t
import os
import pandas as pd
from simba.enums import ReadConfig, Dtypes, Formats
from configparser import ConfigParser
from simba.utils.warnings import NoFileFoundWarning
from simba.utils.errors import (NoFilesFoundError,
                                IntegerError,
                                InvalidInputError,
                                StringError,
                                FloatError,
                                NotDirectoryError,
                                MissingProjectConfigEntryError,
                                CorruptedFileError,
                                ColumnNotFoundError,
                                CountError)

def check_int(name: str,
              value: None,
              max_value=None,
              min_value=None,
              raise_error: bool=True):
    msg = ''
    try:
        t.Int().check(value)
    except t.DataError as e:
        msg=f'{name} should be an integer number in SimBA, but is set to {str(value)}'
        if raise_error:
            raise IntegerError(msg=msg)
        else:
            return False, msg
    if (min_value != None):
        if int(value) < min_value:
            msg = f'{name} should be MORE THAN OR EQUAL to {str(min_value)}. It is set to {str(value)}'
            if raise_error:
                raise IntegerError(msg=msg)
            else:
                return False, msg
    if (max_value != None):
        if int(value) > max_value:
            msg = f'{name} should be LESS THAN OR EQUAL to {str(max_value)}. It is set to {str(value)}'
            if raise_error:
                raise IntegerError(msg=msg)
            else:
                return False, msg
    return True, msg


def check_if_valid_input(name: str,
                         input: str,
                         options: list,
                         raise_error: bool=True):
    msg = ''
    if input not in options:
        msg = f'{name} is set to {str(input)}, which is an invalid setting. OPTIONS {options}'
        if raise_error:
            raise InvalidInputError(msg=msg)
        else:
            return False, msg
    else:
        return True, msg

def check_str(name: str,
              value: None,
              options=(),
              allow_blank=False,
              raise_error: bool = True):
    msg = ''
    try:
        t.String(allow_blank=allow_blank).check(value)
    except t.DataError as e:
        msg = f'{name} should be an string in SimBA, but is set to {str(value)}'
        if raise_error:
            raise StringError(msg=msg)
        else:
            return False, msg
    if len(options) > 0:
        if value not in options:
            msg = f'{name} is set to {str(value)} in SimBA, but this is not a valid option: {options}'
            if raise_error:
                raise StringError(msg=msg)
            else:
                return False, msg
        else:
            return True, msg
    else:
        return True, msg


def check_float(name: str,
                value=None,
                max_value=None,
                min_value=None,
                raise_error: bool=True):
    msg = ''
    try:
        t.Float().check(value)
    except t.DataError as e:
        msg = f'{name} should be a float number in SimBA, but is set to {str(value)}'
        if raise_error:
            raise FloatError(msg=msg)
        else:
            return False, msg
    if (min_value != None):
        if float(value) < min_value:
            msg = f'{name} should be MORE THAN OR EQUAL to {str(min_value)}. It is set to {str(value)}'
            if raise_error:
                raise FloatError(msg=msg)
            else:
                return False, msg
    if (max_value != None):
        if float(value) > max_value:
            msg = f'{name} should be LESS THAN OR EQUAL to {str(max_value)}. It is set to {str(value)}'
            if raise_error:
                raise FloatError(msg=msg)
            else:
                return False, msg
    return True, msg


def read_config_entry(config: ConfigParser,
                      section: str,
                      option: str,
                      data_type: str,
                      default_value=None,
                      options=None):
    try:
        if config.has_option(section, option):
            if data_type == 'float':
                value = config.getfloat(section, option)
            elif data_type == 'int':
                value = config.getint(section, option)
            elif data_type == 'str':
                value = config.get(section, option).strip()
            elif data_type == 'folder_path':
                value = config.get(section, option).strip()
                if not os.path.isdir(value):
                    raise NotDirectoryError(msg=f'The SimBA config file includes paths to a folder ({value}) that does not exist.')
            if options != None:
                if value not in options:
                    raise InvalidInputError(msg=f'{option} is set to {str(value)} in SimBA, but this is not among the valid options: ({options})')
                else:
                    return value
            return value
        elif default_value != None:
            return default_value
        else:
            raise MissingProjectConfigEntryError(msg=f'SimBA could not find an entry for option {option} under section {section} in the project_config.ini. Please specify the settings in the settings menu.')
    except ValueError:
        if default_value != None:
            return default_value
        else:
            raise MissingProjectConfigEntryError(msg=f'SimBA could not find an entry for option {option} under section {section} in the project_config.ini. Please specify the settings in the settings menu.')


def read_simba_meta_files(folder_path: str):
    from simba.utils.read_write import find_files_of_filetypes_in_directory
    file_paths = find_files_of_filetypes_in_directory(directory=folder_path, extensions=['.csv'])
    meta_file_lst = []
    for i in file_paths:
        if i.__contains__("meta"):
            meta_file_lst.append(os.path.join(folder_path, i))
    if len(meta_file_lst) == 0:
        NoFileFoundWarning(msg=f'The training meta-files folder in your project ({folder_path}) does not have any meta files inside it (no files in this folder has the "meta" substring in the filename)')
    return meta_file_lst


def read_meta_file(meta_file_path):
    return pd.read_csv(meta_file_path, index_col=False).to_dict(orient='records')[0]


def check_file_exist_and_readable(file_path: str):
    if not os.path.isfile(file_path):
        raise NoFilesFoundError(msg=f'{file_path} is not a valid file path')
    elif not os.access(file_path, os.R_OK):
        raise CorruptedFileError(f'{file_path} is not readable')
    else:
        pass

def read_config_file(ini_path: str):
    config = ConfigParser()
    try:
        config.read(str(ini_path))
    except Exception as e:
        print(e.args)
        raise MissingProjectConfigEntryError(msg=f'{ini_path} is not a valid project_config file. Please check the project_config.ini path.')
    return config

def check_if_dir_exists(in_dir: str):
    if not os.path.isdir(in_dir):
        raise NotDirectoryError(msg=f'{in_dir} is not a valid directory')

def insert_default_headers_for_feature_extraction(df: pd.DataFrame,
                                                  headers: list,
                                                  pose_config: str,
                                                  filename: str):
    if len(headers) != len(df.columns):
        raise CountError(f'Your SimBA project is set to using the default {pose_config} pose-configuration. '
                         f'SimBA therefore expects {str(len(headers))} columns of data inside the files within the project_folder. However, '
                         f'within file {filename} file, SimBA found {str(len(df.columns))} columns.')
    else:
        df.columns = headers
        return df


def check_that_column_exist(df: pd.DataFrame,
                            column_name: str,
                            file_name: str):
    if column_name not in df.columns:
        raise ColumnNotFoundError(column_name=column_name, file_name=file_name)

def check_if_filepath_list_is_empty(filepaths: list,
                                    error_msg: str):
    if len(filepaths) == 0:
        raise NoFilesFoundError(msg=error_msg)
    else:
        pass


def read_project_path_and_file_type(config: configparser.ConfigParser):
    project_path = read_config_entry(config=config,
                                     section=ReadConfig.GENERAL_SETTINGS.value,
                                     option=ReadConfig.PROJECT_PATH.value,
                                     data_type=ReadConfig.FOLDER_PATH.value)
    file_type = read_config_entry(config=config,
                                  section=ReadConfig.GENERAL_SETTINGS.value,
                                  option=ReadConfig.FILE_TYPE.value,
                                  data_type=Dtypes.STR.value,
                                  default_value=Formats.CSV.value)

    return project_path, file_type
import requests
from tb_rest_client.rest import ApiException


class TBWrapperException(Exception):
    pass


def handle_tb_wrapper_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError as conn_error:
            raise TBWrapperException(
                f"Error connecting to ThingsBoard: {conn_error}")
        except ApiException as api_error:
            raise TBWrapperException(f"ThingsBoard API exception: {api_error}")
        except FileNotFoundError as file_error:
            raise TBWrapperException(
                f"Error, file might not exist: {file_error}")
        except PermissionError as perm_error:
            raise TBWrapperException(
                f"Permission error while reading file: {perm_error}")
        except OSError as os_error:
            raise TBWrapperException(
                f"OS error while reading file: {os_error}")
        except ValueError as value_error:
            raise TBWrapperException(f"Invalid value found: {value_error}")
        except TypeError as type_error:
            raise TBWrapperException(f"Invalid type found: {type_error}")
        except Exception as e:
            raise TBWrapperException(
                f"Unknown error while executing the function: {e}")
    return wrapper

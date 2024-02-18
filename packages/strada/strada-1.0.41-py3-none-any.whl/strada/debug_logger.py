import functools
import json
import time
from enum import Enum

from .common import original_print
from .custom_types import HttpObjectType, LogType, StradaResponse

class StradaResponseStatus(Enum):
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'

class DebugLogger:
    @staticmethod
    def log_http_object(request_log_entry, response_log_entry):
        # log_entry must be a dictionary
        log_entry = {}
        log_entry.update(request_log_entry)
        log_entry.update(response_log_entry)

        try:
            log_entry['log_type'] = LogType.HTTP_OBJECT.name
            log_entry['timestamp'] = time.time()
            log_entry['request'] = request_log_entry
            log_entry['response'] = response_log_entry
            
            # Convert log entry to JSON
            formatted_entry = json.dumps(log_entry)

            # Print the log entry
            original_print(f'<HTTP>{formatted_entry}</HTTP>', flush=True)

        except Exception as e:
            pass
        
    @staticmethod
    def log_function_call(log_entry, function_name=None, app_name=None):
        # log_entry must be a dictionary
        try:
            # Add the function name to the log information
            log_entry['function_name'] = function_name
            log_entry['app_name'] = app_name
            log_entry['log_type'] = LogType.FUNCTION_CALL.name
            log_entry['timestamp'] = time.time()
            
            # Convert log entry to JSON
            formatted_entry = json.dumps(log_entry)
            
            original_print(f'<DEBUG>{formatted_entry}</DEBUG>', flush=True)
            
        except Exception as e:
            pass

    @staticmethod
    def from_strada_response(input: dict, response: StradaResponse, function_name=None, app_name=None):
        try:
            log_entry = {}
            # Log HTTP Request before sending
            log_entry['function_name'] = function_name
            log_entry['app_name'] = app_name
            log_entry['log_type'] = LogType.FUNCTION_CALL.name
            log_entry['status'] = StradaResponseStatus.SUCCESS.name if response.success else StradaResponseStatus.ERROR.name
            log_entry['input'] = input
            log_entry['output'] = response.model_dump_json()

            # Convert log entry to JSON
            formatted_entry = json.dumps(log_entry)
            original_print(f'<DEBUG>{formatted_entry}</DEBUG>', flush=True)

        except Exception as e:
            pass


def with_debug_logs(app_name):
    def inner_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Track execution time
            start_time = time.time()
            # Execute the function
            result = func(self, *args, **kwargs)
            DebugLogger.from_strada_response(input=kwargs, response=result, function_name=self.function_name, app_name=app_name)
            
            # Track execution time
            end_time = time.time()
            return result
        return wrapper
    return inner_decorator


def debug_logger_http(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        DebugLogger.log_http_object(HttpObjectType.REQUEST.name, req_log_entry)
        
        # Execute the function
        result = func(self, *args, **kwargs)
        
        DebugLogger.log_http_object(HttpObjectType.RESPONSE.name, res_log_entry)
        return result
    return wrapper
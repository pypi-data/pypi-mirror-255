from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel

class HttpObjectType(Enum):
    REQUEST = 'REQUEST'
    RESPONSE = 'RESPONSE'
    
class LogType(Enum):
    FUNCTION_CALL = 'FUNCTION_CALL'
    HTTP_OBJECT = 'HTTP_OBJECT'

class StradaError(BaseModel):
    errorCode: int
    statusCode: int
    message: str

class StradaResponse(BaseModel):
    error: Optional[StradaError] = None
    success: bool
    data: Optional[Any] = None

class StradaFunction():
    def __init__(self, function_name: str):
        self.function_name = function_name

    def execute(self, **kwargs):
        raise NotImplementedError
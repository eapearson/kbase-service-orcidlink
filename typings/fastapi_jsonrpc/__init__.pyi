"""
This type stub file was generated by pyright.
"""

import asyncio
import contextvars
import inspect
import logging
import typing
import fastapi.params
import aiojobs
import sentry_sdk
import uvicorn
from collections import ChainMap
from collections.abc import Coroutine
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager, contextmanager
from types import FunctionType
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Type, Union
from fastapi.openapi.constants import REF_PREFIX
from fastapi._compat import ModelField, Undefined, _normalize_errors
from fastapi.dependencies.models import Dependant
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from fastapi import Body, FastAPI
from fastapi.dependencies.utils import get_dependant, get_flat_dependant, get_parameterless_sub_dependant, solve_dependencies
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.routing import APIRoute, APIRouter, serialize_response
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, create_model
from starlette.background import BackgroundTasks
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Match, compile_path, request_response
from functools import cached_property
from sentry_sdk.utils import transaction_from_function as sentry_transaction_from_function

logger = ...
class Params(fastapi.params.Body):
    def __init__(self, default: Any, *, media_type: str = ..., title: str = ..., description: str = ..., gt: float = ..., ge: float = ..., lt: float = ..., le: float = ..., min_length: int = ..., max_length: int = ..., regex: str = ..., example: Any = ..., examples: Optional[Dict[str, Any]] = ..., **extra: Any) -> None:
        ...
    


components = ...
def component_name(name: str, module: str = ...): # -> (obj: Unknown) -> (Unknown | type[BaseModel]):
    """OpenAPI components must be unique by name"""
    ...

def is_scope_child(owner: type, child: type): # -> bool:
    ...

def rename_if_scope_child_component(owner: type, child, postfix: str): # -> type[BaseModel]:
    ...

class BaseError(Exception):
    CODE = ...
    MESSAGE = ...
    ErrorModel = ...
    DataModel = ...
    data_required = ...
    errors_required = ...
    error_model = ...
    data_model = ...
    resp_model = ...
    _component_name = ...
    def __init__(self, data=...) -> None:
        ...
    
    @classmethod
    def validate_data(cls, data): # -> BaseModel:
        ...
    
    def __str__(self) -> str:
        ...
    
    def get_resp_data(self): # -> dict[Unknown, Unknown]:
        ...
    
    @classmethod
    def get_description(cls): # -> str:
        ...
    
    @classmethod
    def get_default_description(cls): # -> str:
        ...
    
    def get_resp(self) -> dict:
        ...
    
    @classmethod
    def get_error_model(cls): # -> type[BaseModel] | None:
        ...
    
    @classmethod
    def build_error_model(cls): # -> type[BaseModel] | None:
        ...
    
    @classmethod
    def get_data_model(cls): # -> type[BaseModel] | None:
        ...
    
    @classmethod
    def build_data_model(cls): # -> type[BaseModel] | None:
        ...
    
    @classmethod
    def get_resp_model(cls): # -> type[_ErrorResponseModel] | None:
        ...
    
    @classmethod
    def build_resp_model(cls): # -> type[_ErrorResponseModel]:
        @component_name(<Expression>, cls.__module__)
        class _ErrorResponseModel(BaseModel):
            ...
        
        
    


@component_name('_Error')
class ErrorModel(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str
    ctx: Optional[Dict[str, Any]] = ...


class ParseError(BaseError):
    """Invalid JSON was received by the server"""
    CODE = ...
    MESSAGE = ...


class InvalidRequest(BaseError):
    """The JSON sent is not a valid Request object"""
    CODE = ...
    MESSAGE = ...
    error_model = ErrorModel


class MethodNotFound(BaseError):
    """The method does not exist / is not available"""
    CODE = ...
    MESSAGE = ...


class InvalidParams(BaseError):
    """Invalid method parameter(s)"""
    CODE = ...
    MESSAGE = ...
    error_model = ErrorModel


class InternalError(BaseError):
    """Internal JSON-RPC error"""
    CODE = ...
    MESSAGE = ...


class NoContent(Exception):
    ...


async def call_sync_async(call, *args, **kwargs):
    ...

def errors_responses(errors: Sequence[Type[BaseError]] = ...): # -> dict[str, dict[Unknown, Unknown]]:
    ...

@component_name(<Expression>)
class JsonRpcRequest(BaseModel):
    jsonrpc: Literal['2.0'] = ...
    id: Union[StrictStr, int] = ...
    method: StrictStr
    params: dict = ...
    model_config = ...


@component_name(<Expression>)
class JsonRpcResponse(BaseModel):
    jsonrpc: Literal['2.0'] = ...
    id: Union[StrictStr, int] = ...
    result: dict
    model_config = ...


def invalid_request_from_validation_error(exc: ValidationError) -> InvalidRequest:
    ...

def invalid_params_from_validation_error(exc: typing.Union[ValidationError, RequestValidationError]) -> InvalidParams:
    ...

def fix_query_dependencies(dependant: Dependant): # -> None:
    ...

def clone_dependant(dependant: Dependant) -> Dependant:
    ...

def insert_dependencies(target: Dependant, dependencies: Sequence[Depends] = ...): # -> None:
    ...

def make_request_model(name, module, body_params: List[ModelField]): # -> type[BaseModel]:
    ...

def make_response_model(name, module, result_model): # -> type[_Response]:
    @component_name(<Expression>, module)
    class _Response(BaseModel):
        ...
    
    

class JsonRpcContext:
    def __init__(self, entrypoint: Entrypoint, raw_request: Any, http_request: Request, background_tasks: BackgroundTasks, http_response: Response, json_rpc_request_class: Type[JsonRpcRequest] = ..., method_route: typing.Optional[MethodRoute] = ...) -> None:
        ...
    
    def on_raw_response(self, raw_response: Union[dict, Exception]): # -> None:
        ...
    
    @property
    def raw_response(self) -> dict:
        ...
    
    @raw_response.setter
    def raw_response(self, value: dict): # -> None:
        ...
    
    @cached_property
    def request(self) -> JsonRpcRequest:
        ...
    
    async def __aenter__(self): # -> Self@JsonRpcContext:
        ...
    
    async def __aexit__(self, *exc_details): # -> bool:
        ...
    
    async def enter_middlewares(self, middlewares: Sequence[JsonRpcMiddleware]): # -> None:
        ...
    


JsonRpcMiddleware = Callable[[JsonRpcContext], AbstractAsyncContextManager]
_jsonrpc_context = ...
def get_jsonrpc_context() -> JsonRpcContext:
    ...

def get_jsonrpc_request_id() -> Optional[Union[str, int]]:
    ...

def get_jsonrpc_method() -> Optional[str]:
    ...

class MethodRoute(APIRoute):
    def __init__(self, entrypoint: Entrypoint, path: str, func: Union[FunctionType, Coroutine], *, result_model: Type[Any] = ..., name: str = ..., errors: List[Type[BaseError]] = ..., dependencies: Sequence[Depends] = ..., response_class: Type[Response] = ..., request_class: Type[JsonRpcRequest] = ..., middlewares: Sequence[JsonRpcMiddleware] = ..., **kwargs) -> None:
        ...
    
    def __hash__(self) -> int:
        ...
    
    def __eq__(self, other) -> bool:
        ...
    
    async def parse_body(self, http_request) -> Any:
        ...
    
    async def handle_http_request(self, http_request: Request): # -> Response:
        ...
    
    async def handle_body(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response, body: Any) -> dict:
        ...
    
    async def handle_req_to_resp(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response, req: Any, dependency_cache: dict = ..., shared_dependencies_error: BaseError = ...) -> dict:
        ...
    
    async def handle_req(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response, ctx: JsonRpcContext, dependency_cache: dict = ..., shared_dependencies_error: BaseError = ...): # -> Any:
        ...
    


class RequestShadow(Request):
    def __init__(self, request: Request) -> None:
        ...
    
    async def stream(self): # -> Generator[bytes, Any, None]:
        ...
    
    async def body(self): # -> bytes:
        ...
    
    async def json(self): # -> Any:
        ...
    
    async def form(self, **kw): # -> FormData:
        ...
    
    async def close(self):
        ...
    
    async def is_disconnected(self): # -> bool:
        ...
    


class EntrypointRoute(APIRoute):
    def __init__(self, entrypoint: Entrypoint, path: str, *, name: str = ..., errors: List[Type[BaseError]] = ..., common_dependencies: Sequence[Depends] = ..., response_class: Type[Response] = ..., request_class: Type[JsonRpcRequest] = ..., **kwargs) -> None:
        ...
    
    def __hash__(self) -> int:
        ...
    
    def __eq__(self, other) -> bool:
        ...
    
    async def solve_shared_dependencies(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response) -> dict:
        ...
    
    async def parse_body(self, http_request) -> Any:
        ...
    
    async def handle_http_request(self, http_request: Request): # -> Response:
        ...
    
    async def handle_body(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response, body: Any) -> dict:
        ...
    
    async def handle_req_to_resp(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response, req: Any, dependency_cache: dict = ..., shared_dependencies_error: BaseError = ...) -> dict:
        ...
    
    async def handle_req(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response, ctx: JsonRpcContext, dependency_cache: dict = ..., shared_dependencies_error: BaseError = ...):
        ...
    


class Entrypoint(APIRouter):
    method_route_class = MethodRoute
    entrypoint_route_class = EntrypointRoute
    default_errors: List[Type[BaseError]] = ...
    def __init__(self, path: str, *, name: str = ..., errors: List[Type[BaseError]] = ..., dependencies: Sequence[Depends] = ..., common_dependencies: Sequence[Depends] = ..., middlewares: Sequence[JsonRpcMiddleware] = ..., scheduler_factory: Callable[..., aiojobs.Scheduler] = ..., scheduler_kwargs: dict = ..., request_class: Type[JsonRpcRequest] = ..., **kwargs) -> None:
        ...
    
    def __hash__(self) -> int:
        ...
    
    def __eq__(self, other) -> bool:
        ...
    
    @property
    def common_dependencies(self): # -> Sequence[Depends]:
        ...
    
    async def shutdown(self): # -> None:
        ...
    
    async def get_scheduler(self): # -> Scheduler:
        ...
    
    async def handle_exception(self, exc) -> dict:
        ...
    
    async def handle_exception_to_resp(self, exc) -> dict:
        ...
    
    def bind_dependency_overrides_provider(self, value): # -> None:
        ...
    
    async def solve_shared_dependencies(self, http_request: Request, background_tasks: BackgroundTasks, sub_response: Response) -> dict:
        ...
    
    def add_method_route(self, func: Union[FunctionType, Coroutine], *, name: str = ..., **kwargs) -> None:
        ...
    
    def method(self, **kwargs) -> Callable:
        ...
    


class API(FastAPI):
    def __init__(self, fastapi_jsonrpc_components_fine_names: bool = ..., **kwargs) -> None:
        ...
    
    def openapi(self): # -> Dict[str, Any]:
        ...
    
    def bind_entrypoint(self, ep: Entrypoint): # -> None:
        ...
    


if __name__ == '__main__':
    app = ...
    api_v1 = ...
    class MyError(BaseError):
        CODE = ...
        MESSAGE = ...
        class DataModel(BaseModel):
            details: str
            ...
        
        
    
    
    @api_v1.method(errors=[MyError])
    def echo(data: str = ...) -> str:
        ...
    

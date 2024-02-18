from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
)

from fastapi import routing, FastAPI, Request, Response
from fastapi.datastructures import Default
from fastapi.params import Depends
from fastapi.utils import generate_unique_id
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute
from starlette.types import Lifespan, AppType

from fastapi_identity.services.service_collection import ServiceCollection


class FastApiBuilder:
    def __init__(
            self: AppType,
            *,
            debug: bool = False,
            routes: Optional[List[BaseRoute]] = None,
            title: str = "FastAPI",
            summary: Optional[str] = None,
            description: str = "",
            version: str = "0.1.0",
            openapi_url: Optional[str] = "/openapi.json",
            openapi_tags: Optional[List[Dict[str, Any]]] = None,
            servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
            dependencies: Optional[Sequence[Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            redirect_slashes: bool = True,
            docs_url: Optional[str] = "/docs",
            redoc_url: Optional[str] = "/redoc",
            swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect",
            swagger_ui_init_oauth: Optional[Dict[str, Any]] = None,
            middleware: Optional[Sequence[Middleware]] = None,
            exception_handlers: Optional[
                Dict[
                    Union[int, Type[Exception]],
                    Callable[[Request, Any], Coroutine[Any, Any, Response]],
                ]
            ] = None,
            on_startup: Optional[Sequence[Callable[[], Any]]] = None,
            on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
            lifespan: Optional[Lifespan[AppType]] = None,
            terms_of_service: Optional[str] = None,
            contact: Optional[Dict[str, Union[str, Any]]] = None,
            license_info: Optional[Dict[str, Union[str, Any]]] = None,
            openapi_prefix: str = "",
            root_path: str = "",
            root_path_in_servers: bool = True,
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            webhooks: Optional[routing.APIRouter] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            swagger_ui_parameters: Optional[Dict[str, Any]] = None,
            generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(generate_unique_id),
            separate_input_output_schemas: bool = True,
            **extra: Any
    ):
        self.app = FastAPI(
            debug=debug,
            routes=routes,
            title=title,
            summary=summary,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=openapi_tags,
            servers=servers,
            dependencies=dependencies,
            default_response_class=default_response_class,
            redirect_slashes=redirect_slashes,
            docs_url=docs_url,
            redoc_url=redoc_url,
            swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
            swagger_ui_init_oauth=swagger_ui_init_oauth,
            middleware=middleware,
            exception_handlers=exception_handlers,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            terms_of_service=terms_of_service,
            contact=contact,
            license_info=license_info,
            openapi_prefix=openapi_prefix,
            root_path=root_path,
            root_path_in_servers=root_path_in_servers,
            responses=responses,
            callbacks=callbacks,
            webhooks=webhooks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            swagger_ui_parameters=swagger_ui_parameters,
            generate_unique_id_function=generate_unique_id_function,
            separate_input_output_schemas=separate_input_output_schemas,
            extra=extra
        )
        self.services = ServiceCollection(self.app)

    def build(self) -> FastAPI:
        self.app.dependency_overrides.update(getattr(self.services, '_dependencies'))

        for k, v in getattr(self.services, '_middlewares').items():
            self.app.add_middleware(k, **v)

        return self.app

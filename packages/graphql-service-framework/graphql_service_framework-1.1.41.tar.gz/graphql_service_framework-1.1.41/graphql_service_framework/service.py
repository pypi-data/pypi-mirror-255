import asyncio
import inspect
import os
from functools import partial

from typing import Dict, Callable, Any

from graphql_api import GraphQLAPI
from graphql_api.remote import GraphQLRemoteObject, GraphQLRemoteExecutor
from graphql_api.utils import to_snake_case
from graphql_http_server import GraphQLHTTPServer

from hypercorn import Config
from hypercorn.asyncio import serve
from hypercorn.middleware import DispatcherMiddleware

# noinspection PyProtectedMember
from hypercorn.middleware.wsgi import _WSGIMiddleware
from hypercorn.typing import ASGIFramework, Scope, ASGIReceiveCallable, ASGISendCallable


class BaseService:
    def __init__(self, config: Dict = None):
        if not config:
            config = {}

        self.config = config

    def create_asgi_app(self) -> ASGIFramework:
        async def base_app(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        (b"content-type", b"text/plain"),
                        (b"content-length", b"5"),
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"Default response for BaseService",
                }
            )

        return base_app

    def run(self, config: Dict = None):
        asyncio_config = Config.from_mapping({**(self.config or {}), **(config or {})})

        return asyncio.run(serve(self.create_asgi_app(), asyncio_config))

    def client(self):
        from starlette.testclient import TestClient

        # noinspection PyTypeChecker
        return TestClient(self.create_asgi_app())


class DispatcherService(BaseService):
    def __init__(self, service_map: Dict, config: Dict = None):
        super().__init__(config=config)
        self.service_map = service_map

    def create_asgi_app(self):
        mounts: Dict[str, ASGIFramework] = {}

        for path, service in self.service_map.items():
            if hasattr(service, "create_service"):
                service = service.create_service()

            if hasattr(service, "create_asgi_app"):
                service = service.create_asgi_app()

            mounts[path] = service

        return DispatcherMiddleware(mounts)


class WSGIMiddleware(_WSGIMiddleware):
    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        loop = asyncio.get_event_loop()

        def _call_soon(func: Callable, *args: Any) -> Any:
            future = asyncio.run_coroutine_threadsafe(func(*args), loop)
            return future.result()

        await self.wsgi_app(
            scope, receive, send, partial(loop.run_in_executor, None), _call_soon
        )


class GraphQLService(BaseService):
    def __init__(self, root, config: Dict = None):
        super().__init__(config=config)
        from graphql_service_framework import ServiceConnection, ServiceManager

        graphiql_default = self.config.get("graphiql_default", "")
        relative_path = self.config.get("http_relative_path", "")

        if self.config.get("service_type") is None:
            self.config["service_type"] = "asgi"

        if self.config.get("allow_cors") is None:
            self.config["allow_cors"] = True

        if self.config.get("service_name") is None:
            self.config["service_name"] = to_snake_case(root.__class__.__name__)

        if self.config.get("schema_version") is None and root:
            if hasattr(root, "schema_version"):
                self.config["schema_version"] = root.schema_version
            elif hasattr(root.__class__, "schema_version"):
                self.config["schema_version"] = root.__class__.schema_version

        if self.config.get("http_health_path") is None:
            self.config["http_health_path"] = f"{relative_path}/health"

        health_path = self.config.get("http_health_path")

        auth_domain = None
        auth_audience = None
        auth_enabled = False
        if self.config.get("auth"):
            auth_domain = self.config["auth"]["domain"]
            auth_audience = self.config["auth"]["audience"]
            enabled = self.config["auth"].get("enabled").lower()
            if enabled == "true":
                auth_enabled = True

        if not graphiql_default:
            dirs = [os.path.dirname(inspect.getfile(root.__class__)), os.getcwd()]
            file_names = [
                "./.graphql",
                "../.graphql",
            ]

            for _dir in dirs:
                if not graphiql_default:
                    for _file_name in file_names:
                        # noinspection PyBroadException
                        try:
                            graphiql_default = open(
                                os.path.join(_dir, _file_name), mode="r"
                            ).read()
                            break
                        # noinspection PyBroadException
                        except Exception:
                            pass
        if root:
            self.graphql_api = GraphQLAPI(root=root.__class__)
            self.graphql_http_server = GraphQLHTTPServer.from_api(
                api=self.graphql_api,
                root_value=root,
                graphiql_default_query=graphiql_default,
                health_path=health_path,
                allow_cors=self.config.get("allow_cors"),
                auth_domain=auth_domain,
                auth_audience=auth_audience,
                auth_enabled=auth_enabled,
            )

        self.service_manager_path = self.config.get("service_manager_path", "/service")

        connections = []

        for key, service in self.config.get("services", {}).items():
            from graphql_service_framework.schema import Schema

            valid_service = False

            if inspect.isclass(service) and issubclass(service, Schema):
                service = service.client()

            if isinstance(service, GraphQLRemoteObject):
                if issubclass(service.python_type, Schema):
                    version = service.python_type.schema_version.split(".")

                    if isinstance(service.executor, GraphQLRemoteExecutor):
                        if version[-1].lower() == "dev":
                            version_specifier = f">={'.'.join(version)}"
                        else:
                            version_specifier = f"~={version[0]}.{version[1]}"

                        url = service.executor.url + self.service_manager_path
                        connection = ServiceConnection(
                            name=key,
                            schema=service.python_type,
                            schema_version_specifier=version_specifier,
                            service_url=service.executor.url,
                            service_manager_url=url,
                        )

                        connections.append(connection)
                        valid_service = True

            if not valid_service:
                raise TypeError(f"Invalid service {key} {service}.")

        self.service_manager = ServiceManager(
            name=self.config.get("service_name"),
            schema_version=self.config.get("schema_version"),
            connections=connections,
        )

    def create_asgi_app(self) -> ASGIFramework:
        from graphql_service_framework import ServiceMeshMiddleware

        wsgi_app = ServiceMeshMiddleware(
            wsgi_app=self.graphql_http_server.app(main=self.config.get("main")),
            service_manager=self.service_manager,
            service_manager_path=self.service_manager_path,
        )
        return WSGIMiddleware(wsgi_app=wsgi_app, max_body_size=2**32)


Service = GraphQLService

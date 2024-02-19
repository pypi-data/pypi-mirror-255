from graphql_service_framework import Service, DispatcherService
from tests.utils import BasicService


class TestDispatcher:
    # noinspection DuplicatedCode,PyUnusedLocal
    def test_dispatcher(self):
        service_a = Service(root=BasicService(hello_response="service_a"))
        service_b = Service(root=BasicService(hello_response="service_b"))
        service_c = Service(root=BasicService(hello_response="service_c"))

        simple_dispatcher = DispatcherService({"/": service_a})

        client = simple_dispatcher.client()

        service_response = client.get("/?query={hello}")

        assert service_response.text == '{"data":{"hello":"service_a"}}'

        dispatcher = DispatcherService(
            {"/b": service_b, "/c": service_c, "/": service_a}
        )

        client = dispatcher.client()

        service_a_response = client.get("/?query={hello}")
        service_b_response = client.get("/b?query={hello}")
        service_c_response = client.get("/c?query={hello}")
        service_default_response = client.get("/invalid_path?query={hello}")

        assert service_a_response.text == '{"data":{"hello":"service_a"}}'
        assert service_b_response.text == '{"data":{"hello":"service_b"}}'
        assert service_c_response.text == '{"data":{"hello":"service_c"}}'
        assert service_default_response.text == '{"data":{"hello":"service_a"}}'

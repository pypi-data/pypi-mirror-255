from graphql_api import field

from requests import request, ConnectTimeout, ReadTimeout


class BasicService:
    def __init__(self, hello_response: str):
        self.hello_response = hello_response

    @field
    def hello(self) -> str:
        return self.hello_response


def available(url, method="GET"):
    try:
        response = request(
            method,
            url,
            timeout=5,
            verify=False,
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            },
        )
    except (ConnectionError, ConnectTimeout, ReadTimeout):
        return False

    if response.status_code == 400 or response.status_code == 200:
        return True

    return False

import os

import pytest

import httpcore
import respx

from pygraphql import BaseClientAsync, BaseAuth
from pygraphql.client.utils import ExecutionResult, RetryError


@respx.mock
@pytest.mark.trio
async def test_BaseClientAsync_trio():
    os.environ["GRAPHQL_AUTH_TOKEN"] = "blibli"
    request = respx.post(
        "https://foo.bar/", content={"data": {"id": 123}, "errors": {"error": 401}}
    )
    async with BaseClientAsync(endpoint="https://foo.bar/") as client:
        response = await client.execute("""test""", {"a": "b"})

    assert request.called
    assert isinstance(response, ExecutionResult)
    assert response.data == {"id": 123}
    assert response.errors == {"error": 401}


@respx.mock
@pytest.mark.trio
async def test_BaseClientAsync_trio_with_auth():
    os.environ = {}
    auth = BaseAuth(token="blibli")
    request = respx.post(
        "https://foo.bar/", content={"data": {"id": 123}, "errors": {"error": 401}}
    )
    async with BaseClientAsync(endpoint="https://foo.bar/", auth=auth) as client:
        response = await client.execute("""test""", {"a": "b"})

    assert request.called
    assert isinstance(response, ExecutionResult)
    assert response.data == {"id": 123}
    assert response.errors == {"error": 401}


@respx.mock
@pytest.mark.asyncio
async def test_BaseClientAsync_asyncio():
    os.environ["GRAPHQL_AUTH_TOKEN"] = "blibli"
    request = respx.post(
        "https://foo.bar/", content={"data": {"id": 123}, "errors": {"error": 401}}
    )
    async with BaseClientAsync(
        endpoint="https://foo.bar/", backend="asyncio"
    ) as client:
        response = await client.execute("""test""", {"a": "b"})

    assert request.called
    assert isinstance(response, ExecutionResult)
    assert response.data == {"id": 123}
    assert response.errors == {"error": 401}


@respx.mock
@pytest.mark.trio
async def test_BaseClientAsync_trio_read_timeout_error():
    os.environ["GRAPHQL_AUTH_TOKEN"] = "blibli"
    request = respx.post("https://foo.bar/", content=httpcore.ConnectTimeout())
    with pytest.raises(RetryError):
        async with BaseClientAsync(endpoint="https://foo.bar/") as client:
            await client.execute(
                """test""",
                {"a": "b"},
                max_tries=1,
                random_exponential_sleep_max_sleep=2,
            )

    assert request.called


@pytest.mark.trio
async def test_BaseClientAsync_trio_auth_assertion_error():
    os.environ = {}
    with pytest.raises(AssertionError):
        BaseClientAsync(endpoint="https://foo.bar/")

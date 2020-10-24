import httpcore
import pytest
import respx

from pygraphql.client import BaseClientAsync
from pygraphql.client.utils import ExecutionResult, RetryError


@respx.mock
@pytest.mark.trio
async def test_BaseClientAsync_trio():
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
@pytest.mark.asyncio
async def test_BaseClientAsync_asyncio():
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

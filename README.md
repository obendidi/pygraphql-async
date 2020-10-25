# Pygraphql-Async

A simple and pure async client for graphql in python:

- light-weight
- easy to use
- simple interface

Pygrapql-async uses [httpx](https://www.python-httpx.org/) internally to execute queries and mutations.

**HTTPX** is a high performance asynchronous HTTP client that builds on the well-established usability of requests, and gives you:

- A broadly requests-compatible API.
- Asynchronous interface.
- HTTP/1.1 and HTTP/2 support.
- Strict timeouts everywhere.
- Fully type annotated.
- 100% test coverage.

## Requiremennts

- python>=3.6

## Installation

- from pypi: `pip install pygraphql-async`
- from source: `pip install https://github.com/bendidi/pygraphql-async`

## Usage

### Authentification

pygraphql-async offers a simple basic interface for authentification that extends `httpx.Auth`, you can either use an existing one or create and use your own.

#### BaseAuth

Basic auth interface that eiher takes a JWT token as input or can find throught the env variable `GRAPHQL_AUTH_TOKEN`, the interface basically adds to the request header a new key `Authorization` with value `bearer YOUR_TOKEN_HERE`

- Using a token as input (not recommended):

```py
from pygraphql import BaseAuth

token = "xxxxx"
auth = BaseAuth(token=token)
```

- Using an env variable:

```sh
export GRAPHQL_AUTH_TOKEN=xxxxxx
```

```py
from pygraphql import BaseAuth

auth = BaseAuth()
```

#### Custom Auth

you can also create your own customised auth class following the same guidlines as httpx: https://www.python-httpx.org/advanced/#customizing-authentication

an example can be found in `pygraphql/auth/hasura_admin.py`:

```py
from pygraphql import BaseAuth


class HasuraAdminAuth(BaseAuth):
    # inherits __init__ from BaseAuth, and uses same env variable: GRAPHQL_AUTH_TOKEN
    def auth_flow(self, request):
        # Send the request, with a custom `x-hasura-admin-Secret` header.
        request.headers["x-hasura-admin-Secret"] = self._token
        yield request

# this will create a custom header for hasura admin, from the same env var GRAPHQL_AUTH_TOKEN
auth = HasuraAdminAuth()
```

### BaseClientAsync

Pygrapql-async offers a basic async client for executing queries, the clients inherits all methods nd properties from `hhtpx.AsyncClient`. It takes as input an endpoint (can be an env variable) and all the parameters of https://www.python-httpx.org/api/#asyncclient.

The client by default uses:

- BaseAuth class for authentification
- read/write timeout of 5 seconds

exemple:

```py
from pygraphql import BaseClientAsync

endpoint = "https://api.github.com/graphql"

query = """query($repo_owner:String!, $repo_name:String!, $num_last_issues: Int!) {
        repository(owner:$repo_owner, name:$repo_name) {
            issues(last:$num_last_issues, states:CLOSED) {
                edges {
                    node {
                        title
                        url
                        }
                    }
                }
            }
        }"""

variables = {
    "repo_owner": "encode",
    "repo_name": "httpx",
    "num_last_issues": 3,
}

async with BaseClientAsync(endpoint=endpoint) as client:
    result = await client.execute(
        query,
        variables,
    )
```

or with a custom auth:

```py
from pygraphql import BaseClientAsync, BaseAuth

class CustomAuth(BaseAuth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        # Send the request, with a custom `X-Authentication` header.
        request.headers['X-Authentication'] = self.token
        yield request

endpoint = "https://api.github.com/graphql"

query = """query($repo_owner:String!, $repo_name:String!, $num_last_issues: Int!) {
        repository(owner:$repo_owner, name:$repo_name) {
            issues(last:$num_last_issues, states:CLOSED) {
                edges {
                    node {
                        title
                        url
                        }
                    }
                }
            }
        }"""

variables = {
    "repo_owner": "encode",
    "repo_name": "httpx",
    "num_last_issues": 3,
}

auth = CustomAuth(token="xxxx")

async with BaseClientAsync(endpoint=endpoint, auth=auth) as client:
    result = await client.execute(
        query,
        variables,
    )
```

#### BaseClientAsync.execute

#### ExecutionResult

### Query

In some case we need to run a query over and over in multiple places and with different variables, the `Query` class offers a solution by transforming your query into a callable that you can use everywhere with different variables:

```py
from pygraphql import Query

endpoint = "https://api.github.com/graphql"

get_repo_issues = Query(
    """query($repo_owner:String!, $repo_name:String!, $num_last_issues: Int!) {
            repository(owner:$repo_owner, name:$repo_name) {
                issues(last:$num_last_issues, states:CLOSED) {
                    edges {
                        node {
                            title
                            url
                            }
                        }
                    }
                }
        }""",
    endpoint=endpoint,
)

variables_1 = {...}
results1 = await get_repo_issues(variables_1)

variables_2 = {...}
results2 = await get_repo_issues(variables_2)
```

## Examples

concrete example scripts can be found in [scripts](./scripts)

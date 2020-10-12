import os
import logging
import json
import coloredlogs
import trio

from pygraphql.auth import BaseAuth
from pygraphql.client import BaseClientAsync

coloredlogs.install(level="DEBUG")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)


async def main():
    logger = logging.getLogger(__name__)
    endpoint = "https://api.github.com/graphql"
    token = os.environ["GITHUB_GRAPH_AUTH_TOKEN"]
    auth = BaseAuth(token=token)

    query_str = """query($number_of_repos:Int!) {
                        viewer {
                            name
                            repositories(last: $number_of_repos) {
                            nodes {
                                name
                            }
                            }
                        }
                        }"""
    variables = {"number_of_repos": 2}

    async with BaseClientAsync(endpoint=endpoint, auth=auth) as client:
        result = await client.execute(
            query_str,
            variables,
        )
    logger.info(f"Data:\n{json.dumps(result.data, indent=2)}")
    logger.error(f"Errors: {result.errors}")


if __name__ == "__main__":
    trio.run(main)

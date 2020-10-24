import asyncio
import json
import logging

import coloredlogs

try:
    import trio

    BACKEND = "trio"
except ImportError:
    BACKEND = "asyncio"

from pygraphql import BaseClientAsync

coloredlogs.install(level="DEBUG")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)


async def main():
    logger = logging.getLogger(__name__)
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
        "repo_owner": "bendidi",
        "repo_name": "Tracking-with-darkflow",
        "num_last_issues": 3,
    }

    async with BaseClientAsync(endpoint=endpoint) as client:
        result = await client.execute(
            query,
            variables,
        )
    logger.info(f"Data:\n{json.dumps(result.data, indent=2)}")
    logger.error(f"Errors: {result.errors}")


if __name__ == "__main__":
    if BACKEND == "trio":
        trio.run(main)
    else:
        asyncio.run(main())

import asyncio
import json
import logging
from collections import defaultdict

import coloredlogs

try:
    import trio

    BACKEND = "trio"
except ImportError:
    BACKEND = "asyncio"

from pygraphql import Query

coloredlogs.install(level="DEBUG")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)


async def main():
    logger = logging.getLogger(__name__)
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

    repositories = ["encode/httpx", "python-trio/trio", "graphql/graphql.github.io"]
    num_last_issues = 2
    results = defaultdict(list)
    for repo in repositories:
        repo_owner, repo_name = repo.split("/")
        variables = {
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "num_last_issues": num_last_issues,
        }

        result = await get_repo_issues(variables)
        if result.errors:
            logger.error(f"Errors: {result.errors}")
        else:
            results[repo].extend(
                [edge["node"] for edge in result.data["repository"]["issues"]["edges"]]
            )

    logger.info(f"Data:\n{json.dumps(results, indent=2)}")


if __name__ == "__main__":
    if BACKEND == "trio":
        trio.run(main)
    else:
        asyncio.run(main())

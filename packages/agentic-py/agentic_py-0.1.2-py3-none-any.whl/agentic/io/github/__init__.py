from typing import Union, Dict

import aiohttp

from agentic.core import action, Config, require_config

from ..base.graphql_api import make_graphql_api_query, get_introspect_query


LINK = "Link"
GRAPHQL_BASE_URL = "https://api.github.com/graphql"
API_KEY_CONFIG = Config(
    name="GITHUB_API_KEY",
    description="API key for Github.",
)


@action()
async def graphql_api_query(query: str, variables: Dict[str, str] = {}):
    """Query the Github GraphQL API.

    Useful guidance:
    - Use the GitTimestamp type for datetime values.

    Example queries:

    # Get the last 20 closed issues for a repository
    query ($owner: String!, $repo_name: String!) {
        repository(owner: $owner, name: $repo_name) {
            issues(last: 20, states: CLOSED) {
                edges {
                    node {
                        title
                        url
                        labels(first: 5) {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    # Get the ID for an organization
    query ($org: String!) { organization(login: $org) { id } }
    """
    return await make_graphql_api_query(
        GRAPHQL_BASE_URL, query, _headers(), variables=variables
    )


@action()
async def get_pr_diff(owner: str, repo: str, pull_request_number: Union[str, int]):
    """Get the diff for a pull request."""
    url = f"https://github.com/{owner}/{repo}/pull/{pull_request_number}.diff"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_headers()) as resp:
            resp.raise_for_status()
            return await resp.text()


@action()
async def get_commit_diff(owner: str, repo: str, commit: str):
    """Get the diff for a commit or a branch (commit value can be a branch name)."""
    url = f"https://github.com/{owner}/{repo}/commit/{commit}.diff"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_headers()) as resp:
            resp.raise_for_status()
            return await resp.text()


@action()
async def introspect_schema():
    """Get the Github GraphQL API schema"""
    return await graphql_api_query(get_introspect_query())


def _headers():
    github_api_key = require_config(API_KEY_CONFIG)
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_api_key}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

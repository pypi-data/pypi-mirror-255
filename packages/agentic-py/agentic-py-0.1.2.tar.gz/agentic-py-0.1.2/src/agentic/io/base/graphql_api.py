import os
from typing import Dict, Any
import json

import aiohttp


async def make_graphql_api_query(
    url: str, query: str, headers: Dict[str, str], variables: Dict[str, str] = {}
):
    body: Dict[str, Any] = {"query": query}
    if vars:
        body["variables"] = variables
    req_body = json.dumps(body)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=req_body) as resp:
            resp_body = ""
            try:
                resp_body = await resp.text()
                resp.raise_for_status()
            except Exception as e:
                raise Exception(
                    f"Error while making request to {url}: {resp.status} - {str(e)} \n\n\t response: {resp_body}"
                )
            ret = await resp.json()
            if "errors" in ret:
                raise Exception(
                    f"Error while making request to {url}: \n\n\t request: {req_body} \n\n\t response: {ret}"
                )
            return ret


def get_introspect_query():
    file_name = "introspect.graphql"
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, "r") as f:
        return f.read()

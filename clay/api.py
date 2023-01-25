import textwrap

import requests


API_HOST = "https://api.clay3d.io"


def request(api_key, method, path, files=None, body=None):
    url = f"{API_HOST}{path}"

    headers = {"authorization": "Bearer " + api_key}

    r = requests.request(
        method=method,
        url=url,
        headers=headers,
        files=files,
        json=body,
    )

    json = r.json()
    if 200 <= r.status_code <= 299:
        return json
    else:
        raise Exception(json.get("message", ""))


def graphql(api_key, query, variables={}):
    return request(
        api_key=api_key,
        method="POST",
        path="/graphql",
        body={"query": textwrap.dedent(query), "variables": variables},
    )

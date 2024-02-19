# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from urllib.parse import urljoin, urlparse
from quart import g


def path_from_request(request) -> str:
    """Given a request (from quart) determines the url it is coming from.
    Main goal is to abstract away http vs https"""

    url = request.url
    if request.headers.get("X-Forwarded-Proto") == "https":
        url = url.replace("http://", "https://")

    return urljoin(url, urlparse(url).path)


def get_requester():
    return g.get("retriever")

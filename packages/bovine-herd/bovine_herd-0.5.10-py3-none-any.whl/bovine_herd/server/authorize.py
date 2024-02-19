# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging

from urllib.parse import urlparse
from quart import g, current_app, request

from bovine.crypto import validate_moo_auth_signature, content_digest_sha256

logger = logging.getLogger(__name__)


async def compute_moo_auth_result():
    # FIXME: Should use a cache and allow for remote lookup

    domain = urlparse(request.url).netloc
    didkey, remote_domain = await validate_moo_auth_signature(request, domain)

    if remote_domain:
        logger.warning(
            "Lookup with did:key %s from remote domain %s", didkey, remote_domain
        )

    _, actor_id = await current_app.config["bovine_store"].get_account_url_for_identity(
        didkey
    )

    return actor_id


async def add_authorization():
    """Adds the retriever to g.retriever based on the HTTP Signature"""
    if request.path.startswith("/activitypub"):
        g.retriever = None
        return

    if not g.get("retriever"):
        if "authorization" in request.headers and request.headers[
            "authorization"
        ].startswith("Moo-Auth-1"):
            g.retriever = await compute_moo_auth_result()
        else:
            g.retriever = await current_app.config["validate_http_signature"](request)


async def add_authorization_with_cattle_grid():
    """Adds authorization according to the `X-Cattle-Grid-Requester`
    header from [cattle_grid](https://codeberg.org/bovine/cattle_grid/).
    """
    requester = request.headers.get("x-cattle-grid-requester")

    if requester:
        if request.method.lower() == "post":
            request_digest = request.headers.get("digest")
            if not request_digest:
                return "unauthorized", 401

            digest = content_digest_sha256(await request.get_data())
            request_digest = request_digest[:4].lower() + request_digest[4:]
            if digest != request_digest:
                return "unauthorized", 401

        g.retriever = requester
    else:
        return await add_authorization()

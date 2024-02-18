# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging

from quart import Blueprint, g, request, current_app, render_template, redirect

from bovine_store.utils import determine_summary, add_sub_collections
from bovine_herd.server.utils import path_from_request
import bovine_herd.server.utils
from bovine.jsonld import with_external_context

from .collection import collection_response

logger = logging.getLogger(__name__)

objects_blueprint = Blueprint("objects", __name__, template_folder="templates")


@objects_blueprint.get("/<uuid>")
async def retrieve_from_store(uuid):
    """Returns the object identified by `uuid` as an ActivityPub object"""
    requester = bovine_herd.server.utils.get_requester()
    logger.info("Request for uuid %s at %s for %s", uuid, request.url, requester)

    object_path = path_from_request(request)

    if (
        requester is None
        or requester == "NONE"
        or "json" not in request.headers.get("accept", "").lower()
    ):
        if "text" not in request.headers.get("accept", ""):
            return {"status": "unauthorized"}, 401

        return await fallback_handler(object_path)

    store = current_app.config["bovine_store"]
    obj = await store.retrieve_for_get(requester, object_path)

    if obj:
        obj = with_external_context(obj)
        obj = add_sub_collections(obj)
        if obj["type"] == "Tombstone":
            return obj, 410, {"content-type": "application/activity+json"}

        return obj, 200, {"content-type": "application/activity+json"}

    return (
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Tombstone",
            "id": object_path,
            "name": "Ceci n'est pas un object",
        },
        404,
        {"content-type": "application/activity+json"},
    )


async def fallback_handler(object_path):
    """Returns a fallback page for the ActivityPub object"""
    object_type = None
    object_summary = None
    store = current_app.config["bovine_store"]
    obj = await store.retrieve("Public", object_path)

    if obj:
        if obj.get("url"):
            return redirect(obj.get("url"))
        object_type = obj.get("type")
        object_summary = determine_summary(obj)

    return (
        await render_template(
            "fallback.html",
            object_path=object_path,
            object_type=object_type,
            object_summary=object_summary,
        ),
        415,
    )


@objects_blueprint.get("/<uuid>/<collection>")
async def retrieve_collection_from_store(uuid, collection):
    """Returns the paginated collection identified by uuid and collection"""

    endpoint_path = path_from_request(request)
    object_path = endpoint_path.removesuffix(f"/{collection}")
    if (
        g.retriever is None
        or g.retriever == "NONE"
        or "json" not in request.headers.get("accept", "").lower()
    ):
        return {"status": "unauthorized"}, 401

    store = current_app.config["bovine_store"]
    obj = await store.retrieve_for_get(g.retriever, object_path)

    if not obj:
        return {"status": "unauthorized"}, 401

    return await collection_response(endpoint_path)

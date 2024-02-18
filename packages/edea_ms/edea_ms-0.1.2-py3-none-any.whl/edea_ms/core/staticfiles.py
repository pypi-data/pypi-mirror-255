import os
from importlib import resources
from mimetypes import guess_type
from urllib.parse import quote

from fastapi import Response
from fastapi.responses import FileResponse
from starlette.config import Config

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

static_dir = config.get("STATIC_DIR", default="./static")
has_static_dir = os.path.isdir(static_dir)


def get_asset(path: str) -> FileResponse | Response:
    """
    get_asset tries to retrieve a file from the static directory and failing that, tries
    to serve it from the bundled assets.
    """
    filename = os.path.basename(path)
    if has_static_dir:
        return FileResponse(os.path.join(static_dir, path))

    try:
        return _resource_static_file(path, filename)
    except Exception:
        return Response(status_code=404)


def _resource_static_file(path: str, filename: str) -> FileResponse | Response:
    f = resources.files("edea_ms.static").joinpath(path)

    content = f.read_bytes()
    media_type = guess_type(path)[0] or "text/plain"
    content_disposition_type = "inline"

    content_disposition_filename = quote(filename)
    content_disposition = (
        f"{content_disposition_type}; filename*=utf-8''{content_disposition_filename}"
        if content_disposition_filename != filename
        else f'{content_disposition_type}; filename="{filename}"'
    )
    return Response(
        content,
        headers={"content-disposition": content_disposition},
        media_type=media_type,
    )

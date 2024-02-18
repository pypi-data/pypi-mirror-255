import contextlib
import os
import shutil
import socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer, test
from pathlib import Path
from typing import Optional

import yaml
from minicli import cli, run

from . import ROOT_DIR
from .chapters import generate_chapters
from .indexes import generate_indexes
from .statics import bundle_statics, init_statics, sync_statics


@cli
@cli("collection", choices=["pum", "sp"])
def init(repository_path: Path = Path(), collection: str = ""):
    """Initialize a new book to `repository_path` or current directory.

    :repository_path: Absolute or relative path to book’s sources (default: current).
    :collection: Name of the collection (Presses Universitaires or Sens-Public).
    """
    print(f"Initializing a new book: `{repository_path}` for `{collection}`.")

    is_new_book = not repository_path.exists() or "textes" not in os.listdir(
        repository_path
    )
    if is_new_book:
        shutil.copytree(ROOT_DIR / "init" / "coquille", repository_path)

    init_statics(repository_path, collection)
    shutil.copyfile(
        ROOT_DIR / "init" / collection / "book.toml",
        repository_path / "pressoir" / "book.toml",
    )


@cli
def build(
    repository_path: Path = Path(),
    target_path: Optional[Path] = None,
    chapter: str = "",
):
    """Build a book from `repository_path` or current directory.

    :repository_path: Absolute or relative path to book’s sources (default: current).
    :target_path: Where the book will be built (default: `repository_path`/public).
    :chapter: Specify a given chapter id (e.g. `chapter1`).
    """
    if target_path is None:
        target_path = repository_path / "public"
    target_path.mkdir(parents=True, exist_ok=True)
    print(f"Building a book from {repository_path} to {target_path}.")
    sync_statics(repository_path, target_path)
    css_filename, js_filename = bundle_statics(repository_path, target_path)
    configuration = next(
        yaml.load_all(
            (repository_path / "textes" / "garde" / "livre.yaml").read_text(),
            Loader=yaml.Loader,
        )
    )
    generate_chapters(
        repository_path, target_path, configuration, css_filename, js_filename, chapter
    )
    generate_indexes(repository_path, target_path, configuration)


@cli
def serve(repository_path: Path = Path(), port: int = 8000):
    """Serve an HTML book from `repository_path`/public or current directory/public.

    :repository_path: Absolute or relative path to book’s sources (default: current).
    :port: Port to serve the book from (default=8000)
    """
    print(
        f"Serving HTML book from `{repository_path}/public` to http://127.0.0.1:{port}"
    )

    # From https://github.com/python/cpython/blob/main/Lib/http/server.py#L1307-L1326
    class DirectoryServer(ThreadingHTTPServer):
        def server_bind(self):
            # suppress exception when protocol is IPv4
            with contextlib.suppress(Exception):
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            return super().server_bind()

        def finish_request(self, request, client_address):
            self.RequestHandlerClass(
                request, client_address, self, directory=str(repository_path / "public")
            )

    test(HandlerClass=SimpleHTTPRequestHandler, ServerClass=DirectoryServer, port=port)


def main():
    run()

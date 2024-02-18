import shutil

from . import ROOT_DIR
from .utils import each_file_from, generate_md5

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def init_statics(repository_path, collection):
    shutil.copytree(
        ROOT_DIR / "init" / collection / "static",
        repository_path / "pressoir" / "static",
        dirs_exist_ok=True,
    )


def sync_statics(repository_path, target_path):
    shutil.copytree(
        repository_path / "textes" / "media", target_path / "media", dirs_exist_ok=True
    )
    shutil.copytree(
        repository_path / "pressoir" / "static" / "fonts",
        target_path / "static" / "fonts",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        ROOT_DIR / "static" / "svg",
        target_path / "static" / "svg",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        repository_path / "pressoir" / "static" / "svg",
        target_path / "static" / "svg",
        dirs_exist_ok=True,
    )

    book_settings = tomllib.loads(
        (repository_path / "pressoir" / "book.toml").read_text()
    )
    for svg_file in each_file_from(target_path / "static" / "svg", pattern="*.svg"):
        svg_content = svg_file.read_text()
        for key, [initial, replacement] in book_settings["theme"].items():
            # We do not take the initial `#` because it's escaped in svg.
            svg_content = svg_content.replace(initial[1:], replacement[1:])
        svg_file.write_text(svg_content)


def bundle_statics(repository_path, target_path):
    pressoir_settings = tomllib.loads((ROOT_DIR / "project.toml").read_text())
    book_settings = tomllib.loads(
        (repository_path / "pressoir" / "book.toml").read_text()
    )

    css_parts = []
    for css_file in pressoir_settings["statics"]["css_files"]:
        css_parts.append(f"/* {css_file} */")
        css_parts.append((ROOT_DIR / css_file).read_text())
    for css_file in book_settings["statics"]["css_files"]:
        css_parts.append(f"/* {css_file} */")
        css_content = (repository_path / "pressoir" / css_file).read_text()
        if css_file.endswith("vars.css"):
            for key, [initial, replacement] in book_settings["theme"].items():
                # We do not take the initial `#` because it's escaped in svg.
                css_content = css_content.replace(initial[1:], replacement[1:])
        css_parts.append(css_content)

    js_parts = []
    for js_file in pressoir_settings["statics"]["js_files"]:
        js_parts.append(f"/* {js_file} */")
        js_parts.append((ROOT_DIR / js_file).read_text())
    for js_file in book_settings["statics"].get("js_files", []):
        js_parts.append(f"/* {js_file} */")
        js_parts.append((repository_path / "pressoir" / js_file).read_text())

    css_content = "\n".join(css_parts)
    css_filename = f"bundle.{generate_md5(css_content)}.css"
    (target_path / "static" / css_filename).write_text(css_content)

    js_content = "\n".join(js_parts)
    js_filename = f"bundle.{generate_md5(js_content)}.js"
    (target_path / "static" / js_filename).write_text(js_content)

    return css_filename, js_filename

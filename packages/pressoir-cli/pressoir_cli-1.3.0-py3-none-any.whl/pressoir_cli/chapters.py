from collections import namedtuple

import pypandoc

from . import ROOT_DIR
from .additionals import include_additional_contents
from .sidenotes import convert_sidenotes, rewrite_global_sidenotes
from .utils import get_template_path, neighborhood

try:
    print(f"Pandoc version: {pypandoc.get_pandoc_version()}")
except OSError:
    pypandoc.download_pandoc()
    print(f"Pandoc version: {pypandoc.get_pandoc_version()}")

Chapter = namedtuple("Chapter", "id, title, title_h, index, display_infochapitre")


def compute_nb_of_chapters(tocbook):
    counter = 1
    for chapter in tocbook:
        if "content" in chapter:
            for subchapter in chapter["content"]:
                counter += 1
        else:
            counter += 1
    return counter


def generate_chapters(
    repository_path, target_path, configuration, css_filename, js_filename, chapter_id
):
    print(f"Rendering {target_path}:")
    nb_of_chapters = compute_nb_of_chapters(configuration["tocbook"])
    print("  Generating chapters:")
    book_title = configuration["title"]
    tocbook = configuration["tocbook"]
    # Pandoc requires included files to be where the command is launched.
    local_css_file = ROOT_DIR / "css_head.html"
    local_css_file.write_text(f'<link rel="stylesheet" href="static/{css_filename}" />')
    local_js_file = ROOT_DIR / "js_footer.html"
    local_js_file.write_text(f'<script src="static/{js_filename}"></script>')
    for index, previous_chapter, current_chapter, next_chapter in neighborhood(
        tocbook, recursive_on="content"
    ):
        if not chapter_id or chapter_id == current_chapter["id"]:
            generate_chapter(
                repository_path,
                target_path,
                book_title,
                tocbook,
                nb_of_chapters,
                index,
                previous_chapter,
                current_chapter,
                next_chapter,
                local_css_file,
                local_js_file,
            )
    local_css_file.unlink()
    local_js_file.unlink()


def generate_chapter(
    repository_path,
    target_path,
    book_title,
    tocbook,
    nb_of_chapters,
    index,
    previous_chapter,
    current_chapter,
    next_chapter,
    local_css_file,
    local_js_file,
):
    if previous_chapter is not None:
        previous_chapter = Chapter(
            **{
                "id": previous_chapter["id"],
                "title": previous_chapter["title"],
                "title_h": previous_chapter["title_h"],
                "index": index - 1 if index is not None else None,
                "display_infochapitre": previous_chapter.get("styloArticle", "") or "",
            }
        )
    current_chapter = Chapter(
        **{
            "id": current_chapter["id"],
            "title": current_chapter["title"],
            "title_h": current_chapter["title_h"],
            "index": index,
            "display_infochapitre": current_chapter.get("styloArticle", "") or "",
        }
    )
    if next_chapter is not None:
        next_chapter = Chapter(
            **{
                "id": next_chapter["id"],
                "title": next_chapter["title"],
                "title_h": next_chapter["title_h"],
                "index": index + 1 if index is not None else None,
                "display_infochapitre": next_chapter.get("styloArticle", "") or "",
            }
        )
    print(
        f"    {current_chapter.id}: {current_chapter.title[:60]} "
        + f"({current_chapter.index}/{nb_of_chapters})"
    )
    header_content = generate_header_content(
        repository_path,
        target_path,
        book_title,
        current_chapter,
        previous_chapter,
        next_chapter,
    )
    footer_content = generate_footer_content(
        repository_path,
        target_path,
        book_title,
        current_chapter,
        previous_chapter,
        next_chapter,
        nb_of_chapters,
    )
    html_content = generate_html_content(
        repository_path,
        target_path,
        current_chapter,
        header_content,
        footer_content,
        local_css_file,
        local_js_file,
    )
    html_content = rewrite_global_sidenotes(html_content)
    html_content = include_additional_contents(
        repository_path, current_chapter, html_content
    )
    html_content = convert_sidenotes(html_content)
    (target_path / f"{current_chapter.id}.html").write_text(html_content)


def generate_header_content(
    repository_path,
    target_path,
    book_title,
    current_chapter,
    previous_chapter,
    next_chapter,
):
    template_path = get_template_path(repository_path, "header.html")
    metadata_file = repository_path / "textes" / "garde" / "livre.yaml"
    extra_args = [
        "--ascii",
        f"--template={template_path}",
        f"--metadata-file={metadata_file}",
        f"--variable=title:{book_title}",
        f"--variable=title_h:{current_chapter.title_h}",
        f"--variable=current_chapter_link:{current_chapter.id}.html",
    ]
    if previous_chapter is not None:
        extra_args += [
            f"--variable=previous_chapter_link:{previous_chapter.id}.html",
            f"--variable=previous_chapter_title:{previous_chapter.title_h}",
        ]
    if next_chapter is not None:
        extra_args += [
            f"--variable=next_chapter_link:{next_chapter.id}.html",
            f"--variable=next_chapter_title:{next_chapter.title_h}",
        ]
    header_content = pypandoc.convert_text(
        "",
        "html",
        format="md",
        extra_args=extra_args,
    )
    return header_content


def generate_footer_content(
    repository_path,
    target_path,
    book_title,
    current_chapter,
    previous_chapter,
    next_chapter,
    nb_of_chapters,
):
    template_path = get_template_path(repository_path, "footer.html")
    extra_args = [
        "--ascii",
        f"--template={template_path}",
        f"--metadata=title:{book_title}",
        f"--variable=current_chapter_index:{current_chapter.index}",
        f"--variable=current_chapter_link:{current_chapter.id}.html",
        f"--variable=nb_of_chapters:{nb_of_chapters}",
    ]
    if previous_chapter is not None:
        extra_args += [
            f"--variable=previous_chapter_link:{previous_chapter.id}.html",
            f"--variable=previous_chapter_title_h:{previous_chapter.title_h}",
        ]
    if next_chapter is not None:
        extra_args += [
            f"--variable=next_chapter_link:{next_chapter.id}.html",
            f"--variable=next_chapter_title_h:{next_chapter.title_h}",
        ]
    footer_content = pypandoc.convert_text(
        "",
        "html",
        format="md",
        extra_args=extra_args,
    )
    return footer_content


def generate_html_content(
    repository_path,
    target_path,
    current_chapter,
    header_content,
    footer_content,
    local_css_file,
    local_js_file,
):
    textes_path = repository_path / "textes"
    chapter_id = current_chapter.id
    yaml_content = (textes_path / chapter_id / f"{chapter_id}.yaml").read_text()
    md_content = (textes_path / chapter_id / f"{chapter_id}.md").read_text()
    bib_file = textes_path / chapter_id / f"{chapter_id}.bib"

    yaml_content = yaml_content.replace("nocite: ''", "nocite: '[@*]'")
    md_content = md_content.replace(
        "## Références",
        """
<section>
<details class="references" open>
<summary id="references">Références</summary>

:::{#refs}
:::

</details>
</section>""",
    )

    template_path = get_template_path(repository_path, "chapitre.html")
    extra_args = [
        "--ascii",
        "--citeproc",
        f"--bibliography={bib_file}",
        f"--template={template_path}",
        f"--variable=title:{current_chapter.title}",
        f"--variable=display_infochapitre:{current_chapter.display_infochapitre}",
    ]
    # Pandoc requires included files to be where the command is launched.
    local_header_file = ROOT_DIR / f"{chapter_id}_header.html"
    local_header_file.write_text(header_content)
    local_footer_file = ROOT_DIR / f"{chapter_id}_footer.html"
    local_footer_file.write_text(footer_content)
    extra_args += [
        f"--include-in-header={local_css_file}",
        f"--include-before-body={local_header_file}",
        f"--include-after-body={local_footer_file}",
        f"--include-after-body={local_js_file}",
    ]
    html_content = pypandoc.convert_text(
        yaml_content + md_content,
        "html",
        format="md",
        extra_args=extra_args,
    )
    local_header_file.unlink()
    local_footer_file.unlink()
    return html_content

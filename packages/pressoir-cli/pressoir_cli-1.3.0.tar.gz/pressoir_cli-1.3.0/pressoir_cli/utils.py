import fnmatch
import hashlib
import os

from . import ROOT_DIR


def get_template_path(repository_path, name):
    """Try to find it within the book folder, fallback on pressoir one."""
    template_path = repository_path / "templates" / name
    if not template_path.exists():
        template_path = ROOT_DIR / "templates" / name
    return template_path


def each_file_from(source_dir, pattern="*.html"):
    """Walk across the `source_dir` and return file paths matching `pattern`."""
    for filename in fnmatch.filter(os.listdir(source_dir), pattern):
        yield source_dir / filename


def generate_md5(content):
    return hashlib.md5(content.encode()).hexdigest()


def neighborhood(iterable, first=None, last=None, recursive_on=None):
    """
    Yield the (index, previous, current, next) items given an iterable.

    You can specify a `first` and/or `last` item for bounds.
    With `recursive_on` you set a sub-item string key to dig into.
    """
    index = 1
    iterator = iter(iterable)
    previous = first
    current = next(iterator)  # Throws StopIteration if empty.
    for next_ in iterator:
        if recursive_on not in current:
            yield (index, previous, current, next_)
            previous = current
            index += 1
        else:
            yield (index, previous, current, current[recursive_on][1])
            index += 1
            for index2, previous2, current2, next2 in neighborhood(
                current[recursive_on], first=previous, last=next_
            ):
                yield (index, previous2, current2, next2)
                previous = current2
                index += 1
        current = next_
    if recursive_on not in current:
        yield (index, previous, current, last)
    else:
        yield (index, previous, current, current[recursive_on][1])
        index += 1
        for index2, previous2, current2, next2 in neighborhood(
            current[recursive_on],
            first=previous,  # Intentional no last.
        ):
            yield (index, previous2, current2, next2)
            previous = current2
            index += 1

"""Cleaning of DDP paths, for the ingest pipeline (scripts/0_ingest/0.06_rnv_clean_paths.py).

Donations of the same platform produce paths that differ in ways that have nothing to do with the data:

- wrapper folders around the export (`ig/`, `instagram_takeout_dutch/`, `meta-2025-Dec-05-01-59-38/instagram-<name>-…/`,
  `takeout-20251118T144647Z-3-001/`),
- part numbers of one file (`posts_1.json`, `posts_2.json`).

`clean_path` removes exactly these two things and nothing else, so it never merges two different data fields:
it does not translate, lower-case or touch any other folder, file or field name. `final_path` stays as it is in the
data; `clean_path` is stored next to it.

`match_key` is the comparison form of a clean path (lower case, one kind of separator). It is only used to compare
paths, never stored as the path.

Both rules come from the paths in 005_merged_structures; add a pattern here when a new wrapper shows up, and the
tests in tests/test_clean_paths.py describe what each rule may and may not change.
"""

import re

# Wrapper folders at the start of a path. Applied repeatedly, anchored at the start.
WRAPPERS = [
    re.compile(r"^ig/"),                                                  # ig/<export>
    re.compile(r"^[A-Za-z]+_takeout[^/]*/"),                              # instagram_takeout_dutch/, youtube_takeout/
    re.compile(r"^takeout-\d{8}T\d{6}Z[^/]*/"),                           # takeout-20251118T144647Z-3-001/
    re.compile(r"^meta-[^/]+/(?:instagram|facebook)-[^/]+/"),             # meta-2025-Dec-05-01-59-38/instagram-<name>-<date>-<id>/
]

FILE_EXTENSIONS = r"json|js|csv|txt|html|xml"
# `_1`, `_12` before the extension of a file: part number of a file that was split. Not four digits (a year).
PART_NUMBER = re.compile(rf"_(\d{{1,3}})(?=\.(?:{FILE_EXTENSIONS})(?:/|$))", re.IGNORECASE)
FILE_SEGMENT = re.compile(rf"\.(?:{FILE_EXTENSIONS})$", re.IGNORECASE)


def strip_wrappers(path: str) -> str:
    path = path.strip()
    changed = True
    while changed:
        changed = False
        for pattern in WRAPPERS:
            stripped = pattern.sub("", path, count=1)
            if stripped != path and stripped:
                path, changed = stripped, True
    return path


def drop_part_number(path: str) -> str:
    return PART_NUMBER.sub("", path, count=1)


def clean_path(path: str) -> str:
    """Path without wrapper folders and without the part number of its file."""
    return drop_part_number(strip_wrappers(path))


def match_key(path: str) -> str:
    """Form in which two (clean) paths are compared: lower case, spaces, underscores and hyphens count as one."""
    return re.sub(r"[\s_\-]+", "_", path.strip().lower())


def split_unit(path: str):
    """Split a path into (unit, field).

    The unit is the file the field belongs to: the path up to and including the first segment with a file extension.
    Paths without a file segment (TikTok: Activity/Login History/LoginHistoryList/Date) have the parent record as the
    unit and the last segment as the field. If the file is the first segment of the path (one big export file, such as
    user_data_tiktok.json) the unit also takes the next two segments, so that a unit stays a manageable group.
    """
    segs = path.split("/")
    for i, seg in enumerate(segs):
        if FILE_SEGMENT.search(seg):
            end = i + 1
            if i == 0:   # one big export file: two more segments belong to the unit, but keep a field
                end = max(1, min(len(segs) - 1, 3))
            return "/".join(segs[:end]), "/".join(segs[end:])
    if len(segs) == 1:
        return path, ""
    return "/".join(segs[:-1]), segs[-1]

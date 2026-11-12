"""The path cleaning of the ingest pipeline (src/ingest/cleanPaths.py): what each rule changes, and what it must not."""
import pytest

from src.ingest.cleanPaths import clean_path, drop_part_number, is_metadata_path, match_key, split_unit, strip_wrappers


@pytest.mark.parametrize("raw,expected", [
    ("ig/your_instagram_activity/likes/liked_posts.json/likes_media_likes/title",
     "your_instagram_activity/likes/liked_posts.json/likes_media_likes/title"),
    ("instagram_takeout_dutch/preferences/settings/use_cross-app_messaging.json/x",
     "preferences/settings/use_cross-app_messaging.json/x"),
    ("meta-2025-Dec-05-01-59-38/instagram-this_dutch_home-2025-12-05-ePQDb50C/your_instagram_activity/story_interactions/polls.json/x",
     "your_instagram_activity/story_interactions/polls.json/x"),
    ("takeout-20251118T144647Z-3-001/Takeout/YouTube i YouTube Music/historial/h.json/title",
     "Takeout/YouTube i YouTube Music/historial/h.json/title"),
    ("youtube_takeout/Takeout/YouTube/h.json/title", "Takeout/YouTube/h.json/title"),
])
def test_wrappers_are_stripped(raw, expected):
    assert strip_wrappers(raw) == expected


def test_takeout_folder_itself_is_not_a_wrapper():
    # "Takeout/" is part of the YouTube paths in the catalogue
    p = "Takeout/YouTube y YouTube Music/historial/h.json/title"
    assert strip_wrappers(p) == p


def test_nested_wrappers_are_all_removed():
    assert strip_wrappers("ig/instagram_takeout_dutch/a/b.json/c") == "a/b.json/c"


@pytest.mark.parametrize("raw,expected", [
    ("your_facebook_activity/posts/your_posts_1.json/attachments/data", "your_facebook_activity/posts/your_posts.json/attachments/data"),
    ("posts_12.json/x", "posts.json/x"),
    ("posts_2.json", "posts.json"),
    ("comments_and_reactions/comments_1.json", "comments_and_reactions/comments.json"),
])
def test_part_numbers_are_dropped(raw, expected):
    assert drop_part_number(raw) == expected


@pytest.mark.parametrize("unchanged", [
    "ads/ads_viewed_2024.json/x",            # a year is not a part number
    "a/b_1/c.json/x",                         # a number in a folder name
    "a/b.json/field_1",                       # a number in a field name
    "a/story_2fa.json/x",
])
def test_things_that_are_not_part_numbers_stay(unchanged):
    assert drop_part_number(unchanged) == unchanged


def test_clean_path_does_nothing_else():
    p = "Takeout/YouTube en YouTube Music/geschiedenis/zoekgeschiedenis.json/header"
    assert clean_path(p) == p                 # no translation, no case change
    assert clean_path("ig/Preferences/Settings_2.json/Time Upgraded") == "Preferences/Settings.json/Time Upgraded"


def test_match_key_compares_loosely_but_clean_path_stays_readable():
    assert match_key("Your Posts/Check-ins_1") == match_key("your_posts/check_ins_1")
    assert match_key("a b") == match_key("a_b") == match_key("a-b")
    assert clean_path("Your Posts/a.json") == "Your Posts/a.json"


@pytest.mark.parametrize("path,unit,field", [
    ("a/b/c.json/x/y", "a/b/c.json", "x/y"),
    ("a/b/c.json", "a/b/c.json", ""),
    ("data/account.js/account/createdAt", "data/account.js", "account/createdAt"),
    ("Activity/Login History/LoginHistoryList/Date", "Activity/Login History/LoginHistoryList", "Date"),   # no file segment
    ("Profile", "Profile", ""),
    # one big export file: the unit takes two more segments, a field is kept
    ("user_data_tiktok.json/Tiktok Live/Go Live Settings/SettingsMap/Allow hosts/Value",
     "user_data_tiktok.json/Tiktok Live/Go Live Settings", "SettingsMap/Allow hosts/Value"),
    ("user_data_tiktok.json/Profile", "user_data_tiktok.json", "Profile"),
])
def test_split_unit(path, unit, field):
    assert split_unit(path) == (unit, field)
    assert "/".join(x for x in (unit, field) if x) == path    # nothing lost


@pytest.mark.parametrize("plat,path,expected", [
    ("x", "data/manifest.js/userInfo/accountId", True),
    ("x", "data/manifest.js", True),
    ("x", "x-archive/data/Manifest.js/dataTypes/tweets/files/count", True),
    ("x", "data/tweets.js/tweet/full_text", False),
    ("x", "data/manifest.json/x", False),            # a different file
    ("x", "data/my_manifest.js/x", False),           # only the file called manifest.js
    ("facebook", "data/manifest.js/userInfo/accountId", False),   # the rule is per platform
])
def test_metadata_paths(plat, path, expected):
    assert is_metadata_path(plat, path) is expected

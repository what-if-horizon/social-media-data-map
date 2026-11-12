def kmetty2026():

    return """

Reasoning: medium

# Role
You are an expert annotator of Digital Data Packages (DDPs): the raw data exports that platforms give users on request. The DDPs you will see come from X, Facebook, Instagram, YouTube and TikTok. Your task is to classify the path to a data entry into the DDP topology below and give the three most likely labels with confidence scores.

# Steps
1. Read carefully the definition of the DDP topology below.
2. Read the path to a data entry.
3. Choose the three best-fitting labels for the path and give each a confidence score.
4. Return the result in the output format.

# DDP topology
Only the 15 numbered labels below are valid answers. Use the label string exactly as written. The parent categories are given to help you understand the structure; never use them as a label.

## Service-provider-related data
Definition: represents the foundational technical and analytical infrastructure that platforms automatically record during every-day system use.

1. "Login data"
   Definition: contain the core variables necessary for user authentication, secure system operations, and identity protection, including usernames, email addresses, and account entry timestamps.

2. "Connection / device telemetry"
   Definition: represents the automated telemetry captured by platforms during system transactions. In raw digital data packages, this category contains technical variables such as device types, operating systems, hardware configurations, camera models, synced devices, browser headers, and IP addresses.

3. "Application / third-party links"
   Definition: It includes technical logs and system permissions generated when third-party services integrate with an observed platform. In raw digital data packages, this information appears in specific files tracking external app connections, such as Facebook's "Third party application access," and TikTok's "User Third Platform Information" registries.

4. "Algorithmic and inferred profiles, usage and screen-time metrics"
   Definition: Platform-generated interest categories; screen-time logs and platform usage metrics, such as time spent on Facebook or TikTok.

## User-related data: Semantically specified
Definition: Contains user-centric digital trace data with fixed database definitions and clear schema declarations; this data category is separated from semantically unspecified files, such as open-ended texts and raw media streams, because its fields contain pre-structured data definitions.

5. "Mandatory profile fields"
   Definition: data comprises the foundational identity attributes that digital platforms require of an individual during account creation, typically including legal names, account identifiers, registration timestamps, biological birthdates, and declared genders.

6. "Extended profile (settings)"
   Definition: contains optional settings and selections with fixed database definitions. This includes structured data fields such as explicit account configurations, notification preferences, listed education histories, and personal asset registries.

7. "Network (ego ties)"
   Definition: Captures the relational connections that an individual establishes across online social platforms, appearing in DDPs as friend lists, follower registries, and connection tables.

8. "Ratings and interests"
   Definition: Captures content curation and media consumption properties: traces that function primarily as clear statements of lifestyle, consumer habits, and cultural tastes, such as following an organization or subscribing to a specific YouTube channel.

9. "Contextual tags and mentions"
   Definition: Distinct layer of digital traces that specifies the properties or relationships of existing items. In raw DDPs, this category includes different user tags and text-based references that contacts attach to content. Common examples include photo and post tags on Facebook and Instagram, user mentions within professional comments on LinkedIn, and direct username mentions inside tweets.

10. "Location and GPS traces"
    Definition: Continuous geospatial telemetry, such as background smartphone tracking records.

11. "Passive consumption and exposure"
    Definition: Capture the exact digital content that appears on a user's screen during daily device use. This category includes highly detailed trace datasets such as YouTube watch history and TikTok video recommendation feeds.

## User-related data: Semantically unspecified
Definition: refers to those digital traces where the platform fixes the container, a JSON string, an HTML block, or a plain-text field, but leaves the content entirely to the user; this category is set apart precisely because its content cannot be read by machines without language processing or human contextual interpretation; hold not only text but also media: photographs, video, and voice notes.

12. "Profile free text / bio"
    Definition: Alongside its structured fields, it includes free-text elements such as the "bio" a user writes to narrate their identity in their own words, which belong on the unspecified side and are therefore treated here as well. Because these boxes impose no constraints on content, they routinely record highly personal disclosures, including religious affiliation, political orientation, occupational status, and private life circumstances, often interleaved with direct or relational identifiers in a single string.

13. "Private communication"
    Definition: It covers direct one-to-one messages, group chat logs, voice notes, and shared media across platforms such as Facebook Messenger, Instagram, X, TikTok, LinkedIn, and WhatsApp.

14. "One-to-many communication"
    Definition: Covers the unstructured text and media a user shares with a broad audience: public status updates, posts, shared links, stories, and above all, the comments left across platforms.

15. "Human-machine dialogue"
    Definition: Covers search query histories and dialogue logs with generative AI such as ChatGPT and Meta AI. The type differs from the passive-consumption logs in a basic way. Those logs record what a user was exposed to; these record what a user actively asks, formulates, and works through in their own words.

# Decision rules (apply when categories seem to overlap)
- Network (ego ties) vs. Ratings and interests: the boundary between network data and interest data is blurry. When a user follows an organization or subscribes to a specific YouTube channel, the action generates a database trace that can technically be interpreted as a network connection. However, from an analytical standpoint, these traces function primarily as clear statements of lifestyle, consumer habits, and cultural tastes. Therefore:
  - Use "Network (ego ties)" strictly for bidirectional or unidirectional interpersonal connections.
  - Use "Ratings and interests" for content curation and media consumption properties, including following organizations and subscribing to channels.
  - If a file can contain both (e.g., a following list with both people and organizations), choose the label that fits what the file mainly records and give the other as the second option with a substantial confidence score.
- Passive consumption and exposure vs. Human-machine dialogue: passive consumption records what a user was exposed to; human-machine dialogue records what a user actively asks or formulates.
- Semantically specified vs. semantically unspecified: fields with pre-structured data definitions belong to the specified side; free text and media whose content is left entirely to the user belong to the unspecified side.

# Confidence scoring
- Give exactly three different labels, ranked from most to least likely.
- Each label gets a score from 0 to 100. The three scores must sum to 100.
- Scores must be in descending order (first ≥ second ≥ third).
- Clear cases: put most weight on the first label (e.g., 85 / 10 / 5).
- Ambiguous cases: spread the weight to reflect real uncertainty (e.g., 50 / 40 / 10).
- The second and third labels must be the most plausible alternatives, not random labels.

# Output format
Return only valid JSON, with no text before or after it:
{"path": "<the input path>", "predictions": [{"label": "<label>", "confidence": <score>}, {"label": "<label>", "confidence": <score>}, {"label": "<label>", "confidence": <score>}], "rationale": "<one or two sentences explaining the top choice with reference to its definition, and why the alternatives are less likely>"}

# Examples
Input: Instagram/connections/followers_and_following/following.json
Output: {"path": "Instagram/connections/followers_and_following/following.json", "predictions": [{"label": "Network (ego ties)", "confidence": 65}, {"label": "Ratings and interests", "confidence": 30}, {"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 5}], "rationale": "A following list is a follower registry, which fits Network (ego ties); because followed accounts can be organizations, Ratings and interests is a strong alternative."}

Input: YouTube/history/watch-history.json
Output: {"path": "YouTube/history/watch-history.json", "predictions": [{"label": "Passive consumption and exposure", "confidence": 90}, {"label": "Ratings and interests", "confidence": 7}, {"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 3}], "rationale": "YouTube watch history is named in the definition of Passive consumption and exposure as content that appeared on the user's screen."}

Input: TikTok/Activity/Search History/SearchList
Output: {"path": "TikTok/Activity/Search History/SearchList", "predictions": [{"label": "Human-machine dialogue", "confidence": 88}, {"label": "Passive consumption and exposure", "confidence": 8}, {"label": "Ratings and interests", "confidence": 4}], "rationale": "Search query histories fall under Human-machine dialogue because they record what the user actively formulated, not what they were exposed to."}

Input: Facebook/ads_information/other_categories_used_to_reach_you.json
Output: {"path": "Facebook/ads_information/other_categories_used_to_reach_you.json", "predictions": [{"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 90}, {"label": "Ratings and interests", "confidence": 7}, {"label": "Passive consumption and exposure", "confidence": 3}], "rationale": "These are platform-generated interest categories, not interests the user stated."}

Input: X/data/ip-audit.js
Output: {"path": "X/data/ip-audit.js", "predictions": [{"label": "Login data", "confidence": 55}, {"label": "Connection / device telemetry", "confidence": 40}, {"label": "Location and GPS traces", "confidence": 5}], "rationale": "The file logs account entry timestamps, which fits Login data, but IP addresses are listed under Connection / device telemetry; it is not continuous geospatial telemetry."}

# Path to classify
{PATH}

"""


# ---------------------------------------------------------------------------------------------
# kmetty2026_simple: the same prompt with the simplified definitions of the annotation
# instructions (annotation/12112026_annotation_instructions_DDP_topology.md). Only the topology
# (the parent and label definitions) and the decision rules differ; role, steps, confidence scoring,
# output format and examples are those of kmetty2026, except that it asks for five ranked labels
# (scoring, output format and examples are rewritten for five).
# ---------------------------------------------------------------------------------------------

_TOPOLOGY_SIMPLE = """# DDP topology
Only the 15 numbered labels below are valid answers. Use the label string exactly as written. The parent categories are given to help you understand the structure; never use them as a label.

## Service-provider-related data
Definition: Data the platform records automatically about how its systems are used. These are technical and analytical records, not things the user chose to share.

1. "Login data"
   Definition: Data the platform needs to recognise the user, let them into their account securely and protect their identity. Examples: usernames, email addresses and timestamps of when the account was accessed.

2. "Connection / device telemetry"
   Definition: Technical details the platform records automatically about the devices and connections used to reach it. Examples: device type, operating system, hardware, camera model, synced devices, browser information and IP addresses.

3. "Application / third-party links"
   Definition: Records of outside apps or services that are connected to the user's account, and the permissions they were given. Examples: Facebook's "Third party application access" file and TikTok's "User Third Platform Information" file.

4. "Algorithmic and inferred profiles, usage and screen-time metrics"
   Definition: What the platform itself concludes or measures about the user, rather than what the user stated. Examples: interest categories the platform assigned to the user, screen-time logs and usage metrics such as time spent on Facebook or TikTok.

## User-related data: Semantically specified
Definition: Data about the user stored in fixed, predefined fields, so each value has a set meaning (for example a birthdate field or a list of followers). This sets it apart from free text and media, where the user decides what the content is.

5. "Mandatory profile fields"
   Definition: Basic identity details the platform requires when someone creates an account. Examples: legal name, account ID, registration date, date of birth and gender.

6. "Extended profile (settings)"
   Definition: Optional settings and choices the user made in predefined fields. Examples: account settings, notification preferences, education history the user listed and registries of personal assets.

7. "Network (ego ties)"
   Definition: Connections between the user and other people on the platform. Examples: friend lists, follower and following lists, and connection tables. See the decision rules for the boundary with Ratings and interests.

8. "Ratings and interests"
   Definition: Traces that show what content the user chooses and what they like, and so mainly express their lifestyle, consumer habits and cultural taste. Examples: following an organization or subscribing to a YouTube channel. See the decision rules for the boundary with Network (ego ties).

9. "Contextual tags and mentions"
   Definition: Tags and mentions attached to existing content that say who or what it relates to. Examples: photo and post tags on Facebook and Instagram, user mentions in comments on LinkedIn and @username mentions in tweets.

10. "Location and GPS traces"
    Definition: Ongoing records of where the user's device was located, such as location tracking a smartphone records in the background.

11. "Passive consumption and exposure"
    Definition: Records of the content the platform showed the user on their screen. The user saw this content; they did not create it. Examples: YouTube watch history and TikTok recommended video feeds.

## User-related data: Semantically unspecified
Definition: Data where the platform only provides an empty container (a text field, a JSON string or an HTML block) and the user decides what goes in it. You need to read, watch or listen to it to know what it means. It covers both text and media: photos, videos and voice notes.

12. "Profile free text / bio"
    Definition: Free text the user wrote about themselves on their profile, such as a bio. The structured profile fields belong under Mandatory profile fields or Extended profile; only the free text belongs here. Because these fields have no limits, they often hold personal details such as religion, political views, job or private circumstances, often mixed with names or details that identify the user or people close to them.

13. "Private communication"
    Definition: Messages and media sent to one person or to a closed group. Examples: direct messages, group chats, voice notes and shared media on Facebook Messenger, Instagram, X, TikTok, LinkedIn and WhatsApp.

14. "One-to-many communication"
    Definition: Free text and media the user shares with a broad audience. Examples: public status updates, posts, shared links, stories and, most of all, comments.

15. "Human-machine dialogue"
    Definition: What the user typed to a system in their own words: search queries and conversations with AI chatbots such as ChatGPT and Meta AI. Unlike Passive consumption and exposure, which records what the user was shown, this records what the user actively asked or wrote.

"""


_DECISION_RULES_SIMPLE = """# Decision rules (apply when categories seem to overlap)
- Network (ego ties) vs. Ratings and interests: the boundary between network data and interest data is blurry. When a user follows an organization or subscribes to a specific YouTube channel, the action generates a database trace that can technically be interpreted as a network connection. However, from an analytical standpoint, these traces function primarily as clear statements of lifestyle, consumer habits, and cultural tastes. Therefore:
  - Use Network (ego ties) strictly for bidirectional or unidirectional interpersonal connections.
  - Use Ratings and interests for content curation and media consumption properties, including following organizations and subscribing to channels.
  - If a file can contain both (e.g., a following list with both people and organizations), choose the label that fits what the file mainly records and mention the other option in your rationale.
- Passive consumption and exposure vs. Human-machine dialogue: passive consumption records what a user was exposed to; human-machine dialogue records what a user actively asks or formulates.
- Semantically specified vs. semantically unspecified: fields with pre-structured data definitions belong to the specified side; free text and media whose content is left entirely to the user belong to the unspecified side.

"""


_SCORING_TOP5 = """# Confidence scoring
- Give exactly five different labels, ranked from most to least likely.
- Each label gets a score from 0 to 100. The five scores must sum to 100.
- Scores must be in descending order (first ≥ second ≥ third ≥ fourth ≥ fifth).
- Clear cases: put most weight on the first label (e.g., 80 / 10 / 5 / 3 / 2).
- Ambiguous cases: spread the weight to reflect real uncertainty (e.g., 40 / 30 / 15 / 10 / 5).
- The second to fifth labels must be the most plausible alternatives, not random labels.

# Output format
Return only valid JSON, with no text before or after it:
{"path": "<the input path>", "predictions": [{"label": "<label>", "confidence": <score>}, {"label": "<label>", "confidence": <score>}, {"label": "<label>", "confidence": <score>}, {"label": "<label>", "confidence": <score>}, {"label": "<label>", "confidence": <score>}], "rationale": "<one or two sentences explaining the top choice with reference to its definition, and why the alternatives are less likely>"}

# Examples
Input: Instagram/connections/followers_and_following/following.json
Output: {"path": "Instagram/connections/followers_and_following/following.json", "predictions": [{"label": "Network (ego ties)", "confidence": 60}, {"label": "Ratings and interests", "confidence": 28}, {"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 6}, {"label": "Passive consumption and exposure", "confidence": 4}, {"label": "Extended profile (settings)", "confidence": 2}], "rationale": "A following list is a follower registry, which fits Network (ego ties); because followed accounts can be organizations, Ratings and interests is a strong alternative."}

Input: YouTube/history/watch-history.json
Output: {"path": "YouTube/history/watch-history.json", "predictions": [{"label": "Passive consumption and exposure", "confidence": 85}, {"label": "Ratings and interests", "confidence": 7}, {"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 4}, {"label": "Human-machine dialogue", "confidence": 2}, {"label": "One-to-many communication", "confidence": 2}], "rationale": "YouTube watch history is named in the definition of Passive consumption and exposure as content that appeared on the user's screen."}

Input: TikTok/Activity/Search History/SearchList
Output: {"path": "TikTok/Activity/Search History/SearchList", "predictions": [{"label": "Human-machine dialogue", "confidence": 85}, {"label": "Passive consumption and exposure", "confidence": 7}, {"label": "Ratings and interests", "confidence": 4}, {"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 2}, {"label": "One-to-many communication", "confidence": 2}], "rationale": "Search query histories fall under Human-machine dialogue because they record what the user actively formulated, not what they were exposed to."}

Input: Facebook/ads_information/other_categories_used_to_reach_you.json
Output: {"path": "Facebook/ads_information/other_categories_used_to_reach_you.json", "predictions": [{"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 85}, {"label": "Ratings and interests", "confidence": 7}, {"label": "Passive consumption and exposure", "confidence": 4}, {"label": "Extended profile (settings)", "confidence": 2}, {"label": "Application / third-party links", "confidence": 2}], "rationale": "These are platform-generated interest categories, not interests the user stated."}

Input: X/data/ip-audit.js
Output: {"path": "X/data/ip-audit.js", "predictions": [{"label": "Login data", "confidence": 50}, {"label": "Connection / device telemetry", "confidence": 38}, {"label": "Location and GPS traces", "confidence": 6}, {"label": "Algorithmic and inferred profiles, usage and screen-time metrics", "confidence": 4}, {"label": "Application / third-party links", "confidence": 2}], "rationale": "The file logs account entry timestamps, which fits Login data, but IP addresses are listed under Connection / device telemetry; it is not continuous geospatial telemetry."}

"""


def kmetty2026_simple():
    """Simplified definitions of the annotation instructions, and five ranked labels instead of three."""
    base = kmetty2026()
    start = base.index("# DDP topology")
    scoring = base.index("# Confidence scoring")
    path = base.index("# Path to classify")
    out = base[:start] + _TOPOLOGY_SIMPLE + _DECISION_RULES_SIMPLE + _SCORING_TOP5 + base[path:]
    for a, b in (("give the three most likely labels", "give the five most likely labels"),
                 ("Choose the three best-fitting labels", "Choose the five best-fitting labels")):
        assert a in out, a
        out = out.replace(a, b)
    return out



# ---------------------------------------------------------------------------------------------
# path_std2026: does a path point to the same data as a path in the catalogue (the largest
# donation of the platform)? Placeholders {CATALOGUE} and {PATH} are filled with str.replace
# (the prompt contains JSON braces). {PATH} is last on purpose: everything before it is identical
# for all paths of a platform, so vLLM can reuse the processed catalogue (prefix caching).
# ---------------------------------------------------------------------------------------------

def path_std2026():

    return """

Reasoning: medium

# Role
You are an expert on Digital Data Packages (DDPs): the raw data exports that platforms give users on request. The DDPs you will see come from X, Facebook, Instagram, YouTube and TikTok. An export is a set of files with fields, and a path such as "folder/file.json/field/subfield" points to one field of one file.

The export of one platform is built differently for different people. Your task is to decide whether a given path points to the same data as one of the paths in a catalogue of known paths of that platform, and if so, which one.

# What "the same data" means
Two paths hold the same data when they point to the same field of the same kind of file: the platform wrote the same information in both exports and only the path to it looks different. Paths can look different because of:
- Language. Folder, file and field names are translated in the exports of people with another language setting (for example English, Spanish, Dutch, Catalan). "history/search-history.json", "historial/historial de búsquedas.json" and "geschiedenis/zoekgeschiedenis.json" are the same file.
- Extra folders around the export. A download can be wrapped in folders such as "takeout-20251118T144647Z-3-001/", "meta-2025-Dec-05-01-59-38/instagram-<name>-2025-12-05-<code>/" or a user name. Ignore them.
- Folders or files that are renamed or reorganised between versions of the platform's export.
- Numbered parts of one file: "posts_1.json" and "posts_2.json" hold the same kind of data. Placeholders such as $NUMBER and $USERNAME stand for variable parts.
- Differences in separators, capital letters or spaces.

Two paths hold different data when they point to a different field, even in the same file (for example "session/ip_address" and "session/datr_cookie"), to a different file, or to another kind of record. A shared folder or a shared word is not enough.

# Steps
1. Read the given path from the end: first the field name, then the file name, then the folder names. The field name and the file name matter most, the folder names least.
2. Translate names where needed, and ignore wrapper folders and part numbers.
3. Look in the catalogue for the path that points to the same field of the same kind of file.
4. If there is one, return it. If there are several (for example part 1 and part 2 of one file), return the one with the closest part number, otherwise the first.
5. If no catalogue path points to the same data, return "NA". Do not guess because a path looks similar. Also return "NA" when the path belongs to the export of another platform than the catalogue (for example a TikTok file in the Instagram data), or is not a path to data.

# Rules
- "match" must be copied exactly, character for character, from one line of the catalogue, or be "NA". Never invent, shorten, change or combine paths.
- Return exactly one match, or "NA".

# Catalogue of paths
One path per line.
{CATALOGUE}

# Output format
Return only valid JSON, with no text before or after it:
{"path": "<the given path>", "match": "<exact catalogue path, or NA>", "rationale": "<one or two sentences: what makes the two paths the same data, or why no catalogue path fits>"}

# Examples
Each example has a small catalogue of its own, which is shown with it. Your catalogue is the one above.

Catalogue:
Takeout/YouTube y YouTube Music/historial/historial-de-reproducciones.json/title
Takeout/YouTube y YouTube Music/historial/historial-de-búsquedas.json/header
Input: Takeout/YouTube en YouTube Music/geschiedenis/zoekgeschiedenis.json/header
Output: {"path": "Takeout/YouTube en YouTube Music/geschiedenis/zoekgeschiedenis.json/header", "match": "Takeout/YouTube y YouTube Music/historial/historial-de-búsquedas.json/header", "rationale": "The Dutch zoekgeschiedenis (search history) is the Spanish historial de búsquedas, and both paths end in the same field, header."}

Catalogue:
your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_1.json/attachments/data/media/creation_timestamp
your_facebook_activity/comments_and_reactions/comments.json/comments_v2/timestamp
Input: facebook-jan-2026-ab12/your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_2.json/attachments/data/media/creation_timestamp
Output: {"path": "facebook-jan-2026-ab12/your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_2.json/attachments/data/media/creation_timestamp", "match": "your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_1.json/attachments/data/media/creation_timestamp", "rationale": "Apart from the wrapper folder and the part number of the file (2 instead of 1), the path and the field creation_timestamp are the same."}

Catalogue:
security_and_login_information/record_details.json/admin_records_v2/session/ip_address
security_and_login_information/record_details.json/admin_records_v2/session/user_agent
Input: security_and_login_information/record_details.json/admin_records_v2/session/datr_cookie
Output: {"path": "security_and_login_information/record_details.json/admin_records_v2/session/datr_cookie", "match": "NA", "rationale": "The file is in the catalogue, but the field datr_cookie is not; ip_address and user_agent are different data."}

Catalogue (Instagram):
preferences/settings/use_cross-app_messaging.json/settings_upgraded_to_cross_app_messaging/string_map_data/Time Upgraded
Input: user_data_tiktok.json/Tiktok Live/Go Live Settings/SettingsMap/Allow suggested LIVE hosts to invite you to co-host in LIVE/Value
Output: {"path": "user_data_tiktok.json/Tiktok Live/Go Live Settings/SettingsMap/Allow suggested LIVE hosts to invite you to co-host in LIVE/Value", "match": "NA", "rationale": "This is a TikTok export file, not an Instagram path, so no Instagram catalogue path holds the same data."}

# Path to match
{PATH}

"""



# ---------------------------------------------------------------------------------------------
# Shortlist version of the path standardisation (src/inference/pathshortlist.py): instead of the whole
# catalogue (path_std2026), the model sees a numbered shortlist of candidates and answers with a number.
# Step 1 matches a FILE (path_file2026), step 2 a FIELD inside a matched file (path_field2026).
# Placeholders {CANDIDATES} and {QUERY} are filled with str.replace; {QUERY} is last.
# ---------------------------------------------------------------------------------------------

def path_file2026():

    return """

Reasoning: medium

# Role
You are an expert on Digital Data Packages (DDPs): the raw data exports that platforms give users on request. The DDPs you will see come from X, Facebook, Instagram, YouTube and TikTok. An export is a set of files, each with fields. The export of one platform is built differently for different people.

Your task is to decide whether a file of a DDP is the same file as one of the candidate files from a catalogue of known files of the same platform.

# What "the same file" means
Two files are the same file when they hold the same kind of data: the platform wrote the same information in both exports and only the name or place of the file looks different. They can look different because of:
- Language. Folder, file and field names are translated in the exports of people with another language setting (for example English, Spanish, Dutch, Catalan). "history/search-history.json", "historial/historial de búsquedas.json" and "geschiedenis/zoekgeschiedenis.json" are the same file.
- Folders or files that are renamed or reorganised between versions of the platform's export (for example "Profile" and "Profile And Settings").
- Differences in separators, capital letters or spaces.

Two files are different when they hold another kind of data, even if their names share a word: a watch history is not a search history, comments are not likes.

# Steps
1. Read the name of the file first, then the folders. Use the fields of the file as well: the same file has fields that correspond, although the field names may be translated.
2. Check the numbered candidates. They were selected because their names look similar, so the right one may not be among them.
3. Choose the candidate that holds the same kind of data. If none does, choose 0. Do not guess because a name looks similar.

# Candidates
{CANDIDATES}

# Output format
Return only valid JSON, with no text before or after it:
{"choice": <number of the candidate, or 0 if none holds the same data>, "rationale": "<one or two sentences: what makes the files the same data, or why none fits>"}

# Examples
Each example has candidates of its own, which are shown with it.

Candidates:
1. Takeout/YouTube y YouTube Music/historial/historial-de-reproducciones.json  [fields: header, title, titleUrl, time]
2. Takeout/YouTube y YouTube Music/historial/historial-de-búsquedas.json  [fields: header, title, titleUrl, time]
File to match: Takeout/YouTube en YouTube Music/geschiedenis/zoekgeschiedenis.json  [fields: header, title, titleUrl, time]
Output: {"choice": 2, "rationale": "Zoekgeschiedenis is Dutch for search history, the Spanish historial de búsquedas; the watch history (1) is another kind of data although it has the same fields."}

Candidates:
1. Profile/Profile Info/Profile Info/Bio  [fields: Bio]
2. Profile/Profile Info/Profile Info/Birth Date  [fields: Birth Date]
File to match: Profile And Settings/Profile Info/Profile Info/Bio  [fields: Bio]
Output: {"choice": 1, "rationale": "The folder Profile And Settings is a renamed Profile, and both files hold the bio."}

Candidates:
1. preferences/settings/use_cross-app_messaging.json  [fields: Time Upgraded]
File to match: user_data_tiktok.json/Tiktok Live/Go Live Settings  [fields: SettingsMap]
Output: {"choice": 0, "rationale": "This is a TikTok export file, not an Instagram file, and no candidate holds the same data."}

# File to match
{QUERY}

"""


def path_field2026():

    return """

Reasoning: medium

# Role
You are an expert on Digital Data Packages (DDPs): the raw data exports that platforms give users on request. The DDPs you will see come from X, Facebook, Instagram, YouTube and TikTok. An export is a set of files, each with fields. The export of one platform is built differently for different people.

A file of a DDP has already been matched to a file of a catalogue of known files of the same platform. Your task is to decide whether a field of that file is the same field as one of the candidate fields of the catalogue file.

# What "the same field" means
Two fields are the same when they hold the same piece of information in the same kind of record. They can look different because the names are translated in the exports of people with another language setting (for example English, Spanish, Dutch, Catalan), or because of differences in separators, capital letters or spaces. Fields are different when they hold other information, even if the names share a word: "timestamp" is not "last_modified_timestamp", "ip_address" is not "user_agent". A nested field path ("attachments/data/media/creation_timestamp") must correspond level by level.

# Steps
1. Read the field from the end: the last name matters most, then the names above it.
2. Check the numbered candidates, which were selected because their names look similar. The right one may not be among them.
3. Choose the candidate that is the same field. If none is, choose 0: the catalogue may simply not have this field. Do not guess because a name looks similar.

# Candidates (fields of the catalogue file)
{CANDIDATES}

# Output format
Return only valid JSON, with no text before or after it:
{"choice": <number of the candidate, or 0 if none is the same field>, "rationale": "<one or two sentences: what makes the fields the same, or why none fits>"}

# Examples
Each example has candidates of its own, which are shown with it.

Candidates:
1. session/ip_address
2. session/user_agent
Field to match: sessie/ip-adres
Output: {"choice": 1, "rationale": "Sessie is Dutch for session and ip-adres is the IP address."}

Candidates:
1. session/ip_address
2. session/user_agent
Field to match: session/datr_cookie
Output: {"choice": 0, "rationale": "Neither the IP address nor the user agent is a cookie; the catalogue file has no such field."}

# Field to match
{QUERY}

"""

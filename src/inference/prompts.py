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
# (the parent and label definitions) differs; role, steps, decision rules, confidence scoring,
# output format and examples are those of kmetty2026.
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


def kmetty2026_simple():
    base = kmetty2026()
    start = base.index("# DDP topology")
    end = base.index("# Decision rules")
    return base[:start] + _TOPOLOGY_SIMPLE + base[end:]

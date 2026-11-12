# Annotation instructions DDP topology

Nov 9, 2026 · @Nienke

## Purpose and scope

You classify paths to data entries in Digital Data Packages (DDPs) into the DDP topology below. For each path you choose the best fitting label and write a short rationale.

The DDPs come from five platforms: X, Facebook, Instagram, YouTube and TikTok. A language model annotates the same paths with the same definitions, so human and model annotations can be compared.

## The steps

1. Read carefully the definition of the DDP topology below, including the decision rules.
2. Read the path to a data entry. Use every part of it: platform, folder names, file name and field names.
3. Choose the best fitting label for the path.
4. Write a rationale of one or two sentences explaining why the label fits its definition.

Only the 15 numbered labels are valid answers. The parent categories explain the structure; never use them as a label.

## Service-provider-related data

**Definition:** Data the platform records automatically about how its systems are used. These are technical and analytical records, not things the user chose to share.

### 1. Login data

**Definition:** Data the platform needs to recognise the user, let them into their account securely and protect their identity. Examples: usernames, email addresses and timestamps of when the account was accessed.

### 2. Connection / device telemetry

**Definition:** Technical details the platform records automatically about the devices and connections used to reach it. Examples: device type, operating system, hardware, camera model, synced devices, browser information and IP addresses.

### 3. Application / third-party links

**Definition:** Records of outside apps or services that are connected to the user’s account, and the permissions they were given. Examples: Facebook’s “Third party application access” file and TikTok’s “User Third Platform Information” file.

### 4. Algorithmic and inferred profiles, usage and screen-time metrics

**Definition:** What the platform itself concludes or measures about the user, rather than what the user stated. Examples: interest categories the platform assigned to the user, screen-time logs and usage metrics such as time spent on Facebook or TikTok.

## User-related data: semantically specified

**Definition:** Data about the user stored in fixed, predefined fields, so each value has a set meaning (for example a birthdate field or a list of followers). This sets it apart from free text and media, where the user decides what the content is.

### 5. Mandatory profile fields

**Definition:** Basic identity details the platform requires when someone creates an account. Examples: legal name, account ID, registration date, date of birth and gender.

### 6. Extended profile (settings)

**Definition:** Optional settings and choices the user made in predefined fields. Examples: account settings, notification preferences, education history the user listed and registries of personal assets.

### 7. Network (ego ties)

**Definition:** Connections between the user and other people on the platform. Examples: friend lists, follower and following lists, and connection tables. See the decision rules for the boundary with Ratings and interests.

### 8. Ratings and interests

**Definition:** Traces that show what content the user chooses and what they like, and so mainly express their lifestyle, consumer habits and cultural taste. Examples: following an organization or subscribing to a YouTube channel. See the decision rules for the boundary with Network (ego ties).

### 9. Contextual tags and mentions

**Definition:** Tags and mentions attached to existing content that say who or what it relates to. Examples: photo and post tags on Facebook and Instagram, user mentions in comments on LinkedIn and @username mentions in tweets.

### 10. Location and GPS traces

**Definition:** Ongoing records of where the user’s device was located, such as location tracking a smartphone records in the background.

### 11. Passive consumption and exposure

**Definition:** Records of the content the platform showed the user on their screen. The user saw this content; they did not create it. Examples: YouTube watch history and TikTok recommended video feeds.

## User-related data: semantically unspecified

**Definition:** Data where the platform only provides an empty container (a text field, a JSON string or an HTML block) and the user decides what goes in it. You need to read, watch or listen to it to know what it means. It covers both text and media: photos, videos and voice notes.

### 12. Profile free text / bio

**Definition:** Free text the user wrote about themselves on their profile, such as a bio. The structured profile fields belong under Mandatory profile fields or Extended profile; only the free text belongs here. Because these fields have no limits, they often hold personal details such as religion, political views, job or private circumstances, often mixed with names or details that identify the user or people close to them.

### 13. Private communication

**Definition:** Messages and media sent to one person or to a closed group. Examples: direct messages, group chats, voice notes and shared media on Facebook Messenger, Instagram, X, TikTok, LinkedIn and WhatsApp.

### 14. One-to-many communication

**Definition:** Free text and media the user shares with a broad audience. Examples: public status updates, posts, shared links, stories and, most of all, comments.

### 15. Human-machine dialogue

**Definition:** What the user typed to a system in their own words: search queries and conversations with AI chatbots such as ChatGPT and Meta AI. Unlike Passive consumption and exposure, which records what the user was shown, this records what the user actively asked or wrote.

## Decision rules (apply when categories seem to overlap)

**Network (ego ties) vs. Ratings and interests.** The boundary between network data and interest data is blurry. When a user follows an organization or subscribes to a specific YouTube channel, the action generates a database trace that can technically be interpreted as a network connection. However, from an analytical standpoint, these traces function primarily as clear statements of lifestyle, consumer habits, and cultural tastes. Therefore:

- Use Network (ego ties) strictly for bidirectional or unidirectional interpersonal connections.
- Use Ratings and interests for content curation and media consumption properties, including following organizations and subscribing to channels.
- If a file can contain both (e.g., a following list with both people and organizations), choose the label that fits what the file mainly records and mention the other option in your rationale.

**Passive consumption and exposure vs. Human-machine dialogue.** Passive consumption records what a user was exposed to; human-machine dialogue records what a user actively asks or formulates.

**Semantically specified vs. semantically unspecified.** Fields with pre-structured data definitions belong to the specified side; free text and media whose content is left entirely to the user belong to the unspecified side.


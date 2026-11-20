# Annotation instructions and codebook: DDP topology

Copied from the annotation interface (`annotation/annotation_interface.html`), so this is the text the annotators see.
The longer version of the instructions is `12112026_annotation_instructions_DDP_topology.md`.

## The task

You will classify paths to data entries in Digital Data Packages (DDPs) from four platforms: X, Facebook, Instagram and TikTok. A language model annotates the same paths, so your labels can be compared with the model's.

The task has two parts, each ordered by platform. In part 1 the model's suggested labels are shown next to the paths; in part 2 you choose from the full list of labels only.

**When you are done**, download the CSV and email it to Nienke Visscher (nienke.visscher@bsc.es). For any questions, contact the same address.

Your progress is saved in this browser, so you can close the page and continue later.

## Steps

1. Read the path. Use every part of it: platform, folder names, file name and field names.
2. Choose the best fitting label. Hover over an option to see its definition.
3. If none of the suggested labels fits, choose **None of the above**. A table with all 15 labels and their definitions appears; pick one there.
4. If the path does not give you enough information to decide, choose **I cannot decide** and explain why in the text box that appears.
5. Only if you chose **None of the above**: write a rationale of one or two sentences explaining why the label fits its definition and why none of the suggestions did. Otherwise no rationale is needed.

## Overarching categories

The 15 labels are grouped under three overarching categories. These explain the structure; they are never a label themselves.

- **Service-provider-related data:** data the platform records automatically about how its systems are used. These are technical and analytical records, not things the user chose to share.
- **User-related data: semantically specified:** data about the user stored in fixed, predefined fields, so each value has a set meaning (for example a birthdate field or a list of followers). This sets it apart from free text and media, where the user decides what the content is.
- **User-related data: semantically unspecified:** data where the platform only provides an empty container (a text field, a JSON string or an HTML block) and the user decides what goes in it. You need to read, watch or listen to it to know what it means. It covers both text and media: photos, videos and voice notes.

## Decision rules

- **Network (ego ties)** is strictly for interpersonal connections. **Ratings and interests** covers following organizations and subscribing to channels. If a file holds both, choose what it mainly records and mention the other in your rationale.
- **Passive consumption and exposure** is what the user was shown; **Human-machine dialogue** is what the user typed or asked.
- Fixed, predefined fields are *semantically specified*; free text and media are *semantically unspecified*.

## Codebook

The 15 labels, grouped under the three overarching categories. Only the 15 numbered labels are valid answers.

### Service-provider-related data

Data the platform records automatically about how its systems are used. These are technical and analytical records, not things the user chose to share.

#### 1. Login data

Data the platform needs to recognise the user, let them into their account securely and protect their identity. Examples: usernames, email addresses and timestamps of when the account was accessed.

#### 2. Connection / device telemetry

Technical details the platform records automatically about the devices and connections used to reach it. Examples: device type, operating system, hardware, camera model, synced devices, browser information and IP addresses.

#### 3. Application / third-party links

Records of outside apps or services that are connected to the user’s account, and the permissions they were given.

#### 4. Algorithmic and inferred profiles, usage and screen-time metrics

What the platform itself concludes or measures about the user, rather than what the user stated. Examples: interest categories assigned to the user, screen-time logs and usage metrics.

### User-related data: semantically specified

Data about the user stored in fixed, predefined fields, so each value has a set meaning (for example a birthdate field or a list of followers). This sets it apart from free text and media, where the user decides what the content is.

#### 5. Mandatory profile fields

Basic identity details the platform requires when someone creates an account. Examples: legal name, account ID, registration date, date of birth and gender.

#### 6. Extended profile (settings)

Optional settings and choices the user made in predefined fields. Examples: account settings, notification preferences, education history and registries of personal assets.

#### 7. Network (ego ties)

Connections between the user and other people on the platform. Examples: friend lists, follower and following lists, and connection tables. Use strictly for interpersonal connections.

#### 8. Ratings and interests

Traces that show what content the user chooses and likes: lifestyle, consumer habits and cultural taste. Examples: following an organization or subscribing to a YouTube channel.

#### 9. Contextual tags and mentions

Tags and mentions attached to existing content that say who or what it relates to. Examples: photo and post tags, user mentions in comments, @username mentions in tweets.

#### 10. Location and GPS traces

Ongoing records of where the user’s device was located, such as background location tracking by a smartphone.

#### 11. Passive consumption and exposure

Records of the content the platform showed the user. The user saw this content; they did not create it. Examples: YouTube watch history and TikTok recommended video feeds.

### User-related data: semantically unspecified

Data where the platform only provides an empty container (a text field, a JSON string or an HTML block) and the user decides what goes in it. You need to read, watch or listen to it to know what it means. It covers both text and media: photos, videos and voice notes.

#### 12. Profile free text / bio

Free text the user wrote about themselves on their profile, such as a bio. Structured profile fields belong under Mandatory profile fields or Extended profile.

#### 13. Private communication

Messages and media sent to one person or to a closed group. Examples: direct messages, group chats, voice notes and shared media.

#### 14. One-to-many communication

Free text and media the user shares with a broad audience. Examples: public status updates, posts, shared links, stories and, most of all, comments.

#### 15. Human-machine dialogue

What the user typed to a system in their own words: search queries and conversations with AI chatbots. Unlike Passive consumption, this records what the user actively asked or wrote.

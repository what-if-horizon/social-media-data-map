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

Under each label are example paths per platform. They were drawn at random from paths that a language model assigned to this label; **a person has not checked them**. Wrapper folders around the export (such as `ig/`) are left out, and a platform is missing where no example was found.

### Service-provider-related data

Data the platform records automatically about how its systems are used. These are technical and analytical records, not things the user chose to share.

#### 1. Login data

Data the platform needs to recognise the user, let them into their account securely and protect their identity. Examples: usernames, email addresses and timestamps of when the account was accessed.

**Examples**

- Facebook
  - `personal_information/other_personal_information/emails_we_sent_you.json/label_values/value`
  - `security_and_login_information/account_recoveries_without_password_changes.json/label_values/timestamp_value`
  - `security_and_login_information/your_recent_account_recovery_successes.json/label_values/label`
- Instagram
  - `security_and_login_information/login_and_profile_creation/login_activity.json/account_history_login_history/string_map_data/Agente del usuario/value`
  - `security_and_login_information/login_and_profile_creation/logout_activity.json/account_history_logout_history/string_map_data/CÃ³digo de idioma/timestamp`
  - `security_and_login_information/record_details.json/admin_records_v2/session/datr_cookie`
- TikTok
  - `Activity/Login History/LoginHistoryList/Date`
  - `Profile/Autofill/Email`
  - `Your Activity/Login History/LoginHistoryList/Carrier`
- X
  - `data/account.js/account/createdAt`

#### 2. Connection / device telemetry

Technical details the platform records automatically about the devices and connections used to reach it. Examples: device type, operating system, hardware, camera model, synced devices, browser information and IP addresses.

**Examples**

- Facebook
  - `security_and_login_information/recognized_devices.json/recognized_devices_v2/user_agent`
  - `security_and_login_information/where_you're_logged_in.json/active_sessions_v2/user_agent`
  - `your_facebook_activity/facebook_marketplace/your_marketplace_device_history.json/label_values/ent_field_name`
- Instagram
  - `your_instagram_activity/media/reels.json/ig_reels_media/media/media_metadata/video_metadata/exif_data/date_time_original`
  - `user_data_tiktok.json/Your Activity/Login History/LoginHistoryList/DeviceSystem`
  - `your_instagram_activity/threads/threads_and_replies.json/text_post_app_text_posts/media/media_metadata/photo_metadata/exif_data/date_time_digitized`
- TikTok
  - `Activity/Login History/LoginHistoryList/Carrier`
  - `Activity/Status/Status List/GAID`
  - `Your Activity/Status/Status List/IDFA`
- X
  - `data/ad-engagements.js/ad/adsUserData/adEngagements/engagements/impressionAttributes/deviceInfo/deviceId`
  - `data/key-registry.js/keyRegistryData/deregisteredDevices/deRegisteredDeviceMetadataList`

#### 3. Application / third-party links

Records of outside apps or services that are connected to the user’s account, and the permissions they were given.

**Examples**

- Facebook
  - `apps_and_websites_off_of_facebook/permissions_you_have_granted_to_apps.json/fbid`
  - `apps_and_websites_off_of_facebook/permissions_you_have_granted_to_apps.json/label_values/vec`
  - `your_facebook_activity/facebook_gaming/your_instant_games_links.json/label_values/value`
- Instagram
  - `apps_and_websites_off_of_facebook/connected_apps_and_websites.json/installed_apps_v2/removed_timestamp`
  - `apps_and_websites_off_of_instagram/apps_and_websites/your_activity_off_meta_technologies.json/apps_and_websites_off_meta_activity/events/timestamp`
  - `apps_and_websites_off_of_instagram/apps_and_websites/your_activity_off_meta_technologies_settings.json/timestamp`
- TikTok
  - `Profile And Settings/Off TikTok Activity/OffTikTokActivityDataList/Source`
  - `Profile And Settings/Settings/App`
  - `Profile/Profile Info/ProfileMap/instagramLink`
- X
  - `data/connected-application.js/connectedApplication/organization/url`
  - `data/shop-module.js`

#### 4. Algorithmic and inferred profiles, usage and screen-time metrics

What the platform itself concludes or measures about the user, rather than what the user stated. Examples: interest categories assigned to the user, screen-time logs and usage metrics.

**Examples**

- Facebook
  - `ads_information/meta_ad_library_accounts.json/label_values/vec`
  - `security_and_login_information/your_facebook_activity_history.json/last_activity_v2/last_activity_time/Messenger Lite for Android/activity_by_day`
  - `your_facebook_activity/navigation_bar/notification_tab_display_information.json/label_values/timestamp_value`
- Instagram
  - `personal_information/personal_information/instagram_profile_information.json/profile_account_insights/string_map_data/Has Shared Live Video/timestamp`
  - `logged_information/past_instagram_insights/content_interactions.json/organic_insights_interactions/string_map_data/You engaged delta% more accounts that werenât following you compared to previous period/href`
  - `personal_information/personal_information/instagram_profile_information.json/profile_account_insights/string_map_data/Fecha de la Ãºltima historia/value`
- TikTok
  - `Ads and data/Ad Interests/AdInterestCategories`
  - `Ads and data/Off TikTok Activity/OffTikTokActivityDataList/TimeStamp`
  - `Profile And Settings/Profile Info/ProfileMap/inferredGender`
- X
  - `data/ad-impressions.js/ad/adsUserData/adImpressions/impressions/promotedTrendInfo/trendId`
  - `data/personalization.js/p13nData/interests/audienceAndAdvertisers/lookalikeAdvertisers`

### User-related data: semantically specified

Data about the user stored in fixed, predefined fields, so each value has a set meaning (for example a birthdate field or a list of followers). This sets it apart from free text and media, where the user decides what the content is.

#### 5. Mandatory profile fields

Basic identity details the platform requires when someone creates an account. Examples: legal name, account ID, registration date, date of birth and gender.

**Examples**

- Facebook
  - `logged_information/other_logged_information/your_professional_dashboard_activity.json/fbid`
  - `personal_information/avatars/avatar_data.json/label_values/timestamp_value`
  - `your_facebook_activity/other_activity/your_information_download_requests.json/label_values/ent_field_name`
- Instagram
  - `personal_information/personal_information/personal_information.json/profile_user/string_map_data/Phone Confirmed/href`
  - `personal_information/personal_information/personal_information.json/profile_user/string_map_data/Gender/timestamp`
  - `user_data_tiktok.json/Profile/Autofill/FirstName`
- TikTok
  - `Profile/Auto Fill/LastName`
  - `Profile/Profile Info/ProfileMap/PlatformInfo/Name`
  - `Profile/Profile Information/ProfileMap/telephoneNumber`
- X
  - `data/tweet-headers.js/tweet/user_id`

#### 6. Extended profile (settings)

Optional settings and choices the user made in predefined fields. Examples: account settings, notification preferences, education history and registries of personal assets.

**Examples**

- Facebook
  - `personal_information/profile_information/profile_update_history.json/profile_updates_v2/attachments/data/life_event/end_date/day`
  - `personal_information/profile_information/profile_update_history.json/profile_updates_v2/attachments/data/media/uri`
  - `your_facebook_activity/dating/your_dating_preferences.json/dating_preferences_v2/distance`
- Instagram
  - `preferences/settings/comments_allowed_from.json/settings_allow_comments_from/string_map_data/Comments Allowed From/href`
  - `personal_information/personal_information/instagram_friend_map.json/profile_friend_map/string_map_data/Fecha de caducidad del modo invisible/value`
  - `your_instagram_activity/threads/personal_information.json/text_post_app_text_post_app_profile/string_map_data/TelÃ©fono confirmado/value`
- TikTok
  - `Profile And Settings/Settings/SettingsMap/Suggest your account to contacts`
  - `Profile/AI-Moji/CreateDate`
  - `TikTok Live/Watch Live Settings/WatchLiveSettingsMap/web`
- X
  - `data/tweetdeck.js/deck/columns/pathname`

#### 7. Network (ego ties)

Connections between the user and other people on the platform. Examples: friend lists, follower and following lists, and connection tables. Use strictly for interpersonal connections.

**Examples**

- Facebook
  - `connections/followers/who_you've_followed.json/following_v3/name`
  - `your_facebook_activity/groups/group_invites_you've_sent.json/label_values/timestamp_value`
  - `your_facebook_activity/groups/your_group_messages/$USERNAME.json/messages/reactions/actor`
- Instagram
  - `connections/followers_and_following/following.json/relationships_following/title`
  - `logged_information/past_instagram_insights/audience_insights.json/organic_insights_audience/string_map_data/Actividad de seguidores del jueves/timestamp`
  - `logged_information/past_instagram_insights/audience_insights.json/organic_insights_audience/string_map_data/Follower percentage by town/city/timestamp`
- TikTok
  - `Activity/Following List/Following/UserName`
  - `Profile And Settings/Block List/BlockList/Date`
  - `Profile And Settings/Block List/BlockList/UserName`
- X
  - `data/direct-messages-group.js/dmConversation/messages/joinConversation/participantsSnapshot`
  - `data/periscope-account-information.js/periscopeAccountInformation/twitterScreenName`

#### 8. Ratings and interests

Traces that show what content the user chooses and likes: lifestyle, consumer habits and cultural taste. Examples: following an organization or subscribing to a YouTube channel.

**Examples**

- Facebook
  - `your_facebook_activity/comments_and_reactions/likes_and_reactions.json/label_values/title`
  - `your_facebook_activity/other_activity/your_interactions_with_promotional_content_in_reels.json/label_values/label`
  - `your_facebook_activity/pages/pages_and_profiles_you_follow.json/pages_followed_v2/data/name`
- Instagram
  - `logged_information/past_instagram_insights/audience_insights.json/organic_insights_audience/string_map_data/Porcentaje de seguidoras por edad/timestamp`
  - `logged_information/past_instagram_insights/content_interactions.json/organic_insights_interactions/string_map_data/Post Likes/timestamp`
  - `logged_information/past_instagram_insights/content_interactions.json/organic_insights_interactions/string_map_data/Video interactions/href`
- TikTok
  - `TikTok Shop/Vouchers/Vouchers/VoucherId`
  - `Your Activity/Favorite Collection/FavoriteCollectionList`
  - `Your Activity/Like List/ItemFavoriteList`
- X
  - `data/ad-online-conversions-attributed.js`

#### 9. Contextual tags and mentions

Tags and mentions attached to existing content that say who or what it relates to. Examples: photo and post tags, user mentions in comments, @username mentions in tweets.

**Examples**

- Facebook
  - `ads_information/your_pages_mentions.json/timestamp`
  - `your_facebook_activity/groups/group_posts_and_comments.json/group_posts_v2/attachments/data/event/place/name`
  - `your_facebook_activity/other_activity/your_content_visibility_notification_history.json/label_values/label`
- TikTok
  - `Post/Posts/VideoList/Location`
  - `Your Activity/Hashtag/HashtagList/HashtagLink`
  - `Your Activity/Hashtag/HashtagList/HashtagName`
- X
  - `data/community-note-batsignal.js/communityNoteBatSignal/tweetId`
  - `data/tweets.js/tweet/entities/symbols`
  - `data/tweets.js/tweet/extended_entities/media/source_user_id_str`

#### 10. Location and GPS traces

Ongoing records of where the user’s device was located, such as background location tracking by a smartphone.

**Examples**

- Facebook
  - `ads_information/your_sampled_locations.json/media`
  - `your_facebook_activity/groups/group_posts_and_comments.json/group_posts_v2/attachments/data/for_sale_item/location/coordinate/longitude`
  - `your_facebook_activity/your_places/cities_you_have_checked_into.json/label_values/vec/value`
- Instagram
  - `security_and_login_information/login_and_profile_creation/last_known_location.json/account_history_imprecise_last_known_location/string_map_data/Onnauwkeurige lengtegraad/href`
  - `security_and_login_information/login_and_profile_creation/last_known_location.json/account_history_imprecise_last_known_location/string_map_data/Imprecise Longitude/href`
  - `security_and_login_information/login_and_profile_creation/last_known_location.json/account_history_imprecise_last_known_location/string_map_data/Longitud exacta/timestamp`
- TikTok
  - `Activity/Most Recent Location Data/LocationData/GpsData`
  - `Activity/Most Recent Location Data/LocationData/LastRegion`
  - `Your Activity/Instant Form Ads Responses/ResponsesList/Post/Zip code`
- X
  - `data/tweets.js/tweet/coordinates/type`
  - `data/tweets.js/tweet/geo/coordinates`
  - `data/tweets.js/tweet/geo/type`

#### 11. Passive consumption and exposure

Records of the content the platform showed the user. The user saw this content; they did not create it. Examples: YouTube watch history and TikTok recommended video feeds.

**Examples**

- Facebook
  - `logged_information/other_logged_information/your_facebook_watch_activity_in_the_last_28_days.json/ent_name`
  - `your_facebook_activity/other_activity/last_sent_notification_info.json/label_values/value`
  - `your_facebook_activity/saved_items_and_collections/your_saved_items.json/saves_v2/attachments/data/event/start_timestamp`
- Instagram
  - `personal_information/personal_information/note_interactions.json/profile_note_interactions/string_map_data/Last Notes Seen Time/href`
  - `logged_information/notifications/notifications.json/notifications_v2/text`
  - `your_facebook_activity/facebook_gaming/instant_games.json/instant_games_played_v2/name`
- TikTok
  - `TikTok Shop/Product Browsing History/ProductBrowsingHistories/product_name`
  - `Tiktok Live/Watch Live History/WatchLiveMap/$NUMBER/Link`
  - `Tiktok Live/Watch Live History/WatchLiveMap/$NUMBER/WatchTime`
- X
  - `data/ad-engagements.js/ad/adsUserData/adEngagements/engagements/impressionAttributes/displayLocation`
  - `data/ad-impressions.js/ad/adsUserData/adImpressions/impressions/displayLocation`

### User-related data: semantically unspecified

Data where the platform only provides an empty container (a text field, a JSON string or an HTML block) and the user decides what goes in it. You need to read, watch or listen to it to know what it means. It covers both text and media: photos, videos and voice notes.

#### 12. Profile free text / bio

Free text the user wrote about themselves on their profile, such as a bio. Structured profile fields belong under Mandatory profile fields or Extended profile.

**Examples**

- Facebook
  - `personal_information/profile_information/profile_update_history.json/profile_updates_v2/attachments/data/life_event/description`
  - `personal_information/profile_information/profile_update_history.json/profile_updates_v2/attachments/data/media/description`
  - `personal_information/profile_information/profile_update_history.json/profile_updates_v2/data/text`
- Instagram
  - `personal_information/personal_information/notes.json/profile_notes/string_map_data/Audiencia/href`
  - `your_instagram_activity/threads/personal_information.json/text_post_app_text_post_app_profile/string_map_data/Cumple los requisitos para obtener la insignia de activaciÃ³n en el perfil/timestamp`
  - `your_instagram_activity/threads/saved_threads.json/text_post_app_text_post_app_saved_posts/title`
- TikTok
  - `Profile And Settings/Profile Info/ProfileMap/PlatformInfo/Description`
  - `Profile/Profile Information/ProfileMap/bioDescription`
  - `TikTok Shop/Order History/OrderHistories/$NUMBER/customer_note`
- X
  - `data/periscope-profile-description.js`
  - `data/tweetdeck.js/deck/title`

#### 13. Private communication

Messages and media sent to one person or to a closed group. Examples: direct messages, group chats, voice notes and shared media.

**Examples**

- Facebook
  - `your_facebook_activity/$USERNAME/message_1.json/messages/gifs/uri`
  - `your_facebook_activity/$USERNAME/message_1.json/messages/reactions/timestamp`
  - `your_facebook_activity/other_activity/your_streaks.json/media`
- Instagram
  - `your_instagram_activity/$USERNAME/message_1.json/messages/timestamp_ms`
  - `your_instagram_activity/messages/broadcast/$USERNAME/replies_1.json/replies/original_message_sender`
  - `your_instagram_activity/messages/inbox/$USERNAME/message_1.json/thread_path`
- TikTok
  - `Direct Message/Direct Messages/ChatHistory/Chat History with $USERNAME:/Content`
- X
  - `data/direct-message-headers.js/dmConversation/messages/messageCreate/senderId`
  - `data/direct-messages-group.js/dmConversation/messages/messageCreate/mediaUrls`

#### 14. One-to-many communication

Free text and media the user shares with a broad audience. Examples: public status updates, posts, shared links, stories and, most of all, comments.

**Examples**

- Facebook
  - `your_facebook_activity/facebook_marketplace/items_sold.json/items_selling_v2/description`
  - `your_facebook_activity/facebook_marketplace/items_sold.json/items_selling_v2/title`
  - `your_facebook_activity/posts/media_used_for_memories.json/media`
- Instagram
  - `logged_information/past_instagram_insights/content_interactions.json/organic_insights_interactions/string_map_data/Reels Comments/href`
  - `personal_information/personal_information/reposts.json/profile_media_reposts/string_map_data/Texto/timestamp`
  - `your_instagram_activity/subscriptions/reels.json/subscriptions_reels/string_map_data/URL externa/href`
- TikTok
  - `Location Review/Location Reviews/ReviewsList/PlaceName`
  - `Video/RecentlyDeletedPosts/PostList/Title`
  - `Your Activity/Status/Status List/Web ID`
- X
  - `data/deleted-tweets.js/tweet/entities/media/sizes/thumb/w`
  - `data/deleted-tweets.js/tweet/extended_entities/media/sizes/medium/resize`
  - `data/note-tweet.js/noteTweet/updatedAt`

#### 15. Human-machine dialogue

What the user typed to a system in their own words: search queries and conversations with AI chatbots. Unlike Passive consumption, this records what the user actively asked or wrote.

**Examples**

- Facebook
  - `your_facebook_activity/facebook_marketplace/recent_searches_on_marketplace.json/media`
  - `your_facebook_activity/messages/ai_conversations.json/label_values/dict/dict/label`
  - `your_facebook_activity/messages/ai_conversations.json/label_values/dict/dict/title`
- Instagram
  - `logged_information/recent_searches/place_searches.json/searches_place/string_map_data/Time/value`
  - `logged_information/recent_searches/word_or_phrase_searches.json/searches_keyword/string_map_data/Zoeken/timestamp`
  - `logged_information/search/your_search_history.json/searches_v2/timestamp`
- TikTok
  - `Activity/Search History/SearchList/Date`
  - `Your Activity/Searches/SearchList/Date`
  - `Your Activity/Searches/SearchList/SearchTerm`
- X
  - `data/reply-prompt.js`
  - `data/saved-search.js/savedSearch/savedSearchId`

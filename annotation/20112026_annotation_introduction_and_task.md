# Annotating paths from Digital Data Packages: introduction and your first task

## What the data are

When you ask a platform for your data (X, Facebook, Instagram or TikTok), you receive a **Digital Data Package (DDP)**: a download with folders, files and, inside the files, fields. Every field has a name (a *key*) and a content (a *value*).

We collected DDPs that people donated for research. From each DDP we **kept only the keys and no values**. We have the names of the folders, files and fields, and nothing that a person wrote, watched, searched or did.

For example, a small part of a DDP could look like this (the value is made up):

```json
{ "profile": { "bioDescription": "I love hiking and my cat" } }
```

We kept `profile/bioDescription`. The text "I love hiking and my cat" is not in our data.

The route to one key is called a **path**: folder / folder / file / field. The paths you will see look like this:

- `Profile/Profile Information/ProfileMap/bioDescription` (TikTok)
- `data/follower.js/follower/userLink` (X)
- `security_and_login_information/recognized_devices.json/recognized_devices_v2/user_agent` (Facebook)

Because there are no values, a path only tells you **what kind of information the platform stores in that field**. That is what you will judge. Every part of the path can help: the platform, the folder names, the file name and the field name.

Some things to expect:

- Names come from exports in different languages (English, Spanish, Dutch, Catalan, and more). Translate where you need to.
- Many paths are technical and short. Some do not give you much to go on. For those there is the option "I cannot decide".

## What you will do in the annotation

You will assign each path to **one of 15 categories**, grouped under three overarching categories. The categories, their definitions, the decision rules and one example path per category are in:

**`20112026_annotation_instructions_and_codebook.md`**

## Your first task: read the categories and tell me your doubts

You do not have to annotate any data yet. First, please go through **all 15 categories** and the decision rules, and write down every doubt you have. Doubts are exactly what I am looking for: if something is unclear to you, it will be unclear to others too.

For each category, ask yourself:

1. **Is the definition clear?** Which word or sentence is vague, or can be read in two ways?
2. **Does it overlap with another category?** Can you think of a field that would fit this category and another one? Which two?
4. **Is the example convincing?** Would you have chosen the same category for the example path? Tell me if one is not a good example.
5. **Do we need an extra decision rule?** The codebook already has rules for the pairs that are easy to confuse (for instance *Network* versus *Ratings and interests*). Which other pairs would you want a rule for? How would you word it?

You can think of paths from your own knowledge of the platforms. You do not need real data to raise a doubt.

### How to send them

Write your doubts in a short note or in a copy of this table, and email it to Nienke Visscher (nienke.visscher@bsc.es) **before the introductory session**. One row per doubt, and you can add rows.

| Category (number) | What is unclear, overlapping or missing | Your suggestion for a rule or change |
| --- | --- | --- |
|  |  |  |  
|  |  |  |  
|  |  |  |  

If you have doubts about the overarching categories or about the way the task works, write those down as well.

## What happens next

1. I collect the doubts of everyone and deal with them: I clarify definitions, add or change decision rules, and replace examples where needed. You will get the updated codebook.
2. We then have an **introductory session**. In the session we **code a smoke sample together**: a small sample of paths for practice. We label the paths one by one, compare our choices, discuss where we differ and settle what is still unclear.

Questions at any time: Nienke Visscher, nienke.visscher@bsc.es.

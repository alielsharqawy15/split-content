# Split — game content

Word decks, "Most likely to" prompts, Taboo cards and Odd One Out question
ideas for the party games in the Split app (قسّمها), in English and Arabic.

The app downloads this repo through jsDelivr:

```
https://cdn.jsdelivr.net/gh/alielsharqawy15/split-content@main/manifest.json
```

It checks `manifest.json` when it starts (at most every 6 hours) and from
**Games → Check for new content**, downloads only packs whose `version`
went up, validates them, and keeps them for offline play. **No app update is
needed to ship new words.**

## Add or change content

1. Edit a pack in `packs/`, or add a new one (copy an existing file and give
   it a new `id`; add it to `manifest.json`).
2. **Bump `version`** in the pack *and* the matching entry in `manifest.json`.
   Packs whose version didn't change are not downloaded again.
3. Validate: `python3 scripts/validate.py` (also runs automatically on every
   push — a red ❌ on GitHub means the app would reject that pack).
4. Commit and push to `main`.
5. jsDelivr caches `@main` for up to 12 hours. To publish immediately, open
   these purge links in a browser:
   - `https://purge.jsdelivr.net/gh/alielsharqawy15/split-content@main/manifest.json`
   - `https://purge.jsdelivr.net/gh/alielsharqawy15/split-content@main/packs/<pack-id>.json`

Before an app release, copy this repo into the app so new installs start up
to date: from the app repo run `tool/sync_content.sh`.

## Pack format (schema 1)

```json
{
  "schema": 1,
  "id": "words-egyptian-food",
  "version": 2,
  "kind": "words",
  "name": { "en": "Egyptian food", "ar": "أكل مصري" },
  "emoji": "🇪🇬",
  "oddOneOut": true,
  "items": [ { "en": "Koshari", "ar": "كشري" } ]
}
```

| Field | Notes |
|---|---|
| `id` | lowercase letters, digits, dashes; a pack with the same id as a built-in one replaces it |
| `kind` | `words` (decks in Odd One Out / Charades / Heads Up), `likely`, `taboo`, `ideas` (pooled) |
| `oddOneOut` | words only — also offer the deck as an Odd One Out topic (use concrete nouns) |
| `items` | 1–500 entries, each text ≤ 160 characters; duplicates are dropped |

Taboo items have a word and 3–5 forbidden words per language:

```json
{ "en": { "word": "Camel", "forbidden": ["Desert", "Hump", "Ride", "Animal"] },
  "ar": { "word": "الجمل", "forbidden": ["صحرا", "سنام", "يركب", "حيوان"] } }
```

Write the Arabic side natively (light Egyptian colloquial is welcome), not as
a word-for-word translation.

## Content guidelines

Family-friendly for mixed groups: no gambling, alcohol, romance, politics,
religion jokes or anything mean. Prefer things most people in Egypt and the
Gulf know.

# gta6-companion-content

Content for the GTA 6 companion iOS app. The app downloads the built files from GitHub Pages and caches them for offline use, so new content ships without an App Store update.

```
content/   source of truth (with evidence and internal notes)
schema/    JSON Schema for the content files
scripts/   validate.py (schema + rating rules), build.py (public files -> dist/v1)
agent/     prompt for the daily content agent (opens PRs)
docs/      HANDOFF.md — product decisions and rules
```

Flow: agent opens a PR → `validate` runs → owner reviews and merges → `deploy` publishes `dist/` to GitHub Pages → app picks it up via `v1/manifest.json` hashes.

Local:
```
pip install jsonschema
python scripts/validate.py --check-links
python scripts/build.py
```

Unofficial fan content. Not affiliated with Rockstar Games or Take-Two Interactive.

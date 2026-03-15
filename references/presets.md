# Presets

Preset-first mode uses curated source-selection and parser defaults for known courses. If `preset_id` is present and recognized, the analyzer prefers the preset behavior before falling back to generic heuristics.

Current preset IDs:

- `biochemistry`
- `from-molecules-to-cells`
- `drugs`
- `excitable-cells`

Each preset currently provides:

- preferred source order (`slides_dir` before `notes_pdf`)
- benchmark artifact discovery rules for local regression
- default parser expectations for the known paper format

Public example specs should reference preset IDs only by name. Local runnable specs can be generated with the bundled local-spec generator.

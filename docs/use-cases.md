# Use Cases

## Known Course With a Preset

Use this when:

- the course already has a known preset
- raw slide decks are available
- formal past papers are available

Expected behavior:

- slide extraction is preferred
- parser defaults are stronger
- question segmentation is more robust
- review noise should be lower than generic mode

## Unknown Course With Generic Mode

Use this when:

- there is no preset
- only note PDFs and past papers are available

Expected behavior:

- note extraction drives lecture detection
- topic clustering is heuristic
- more items may enter `Review_Queue`

## Slides + Papers, No Answer Keys

Use this when:

- slide decks exist
- answer keys do not exist or cannot be shared

Expected behavior:

- the analyzer still runs
- mappings rely on lecture content plus question stems
- confidence is lower
- review gating is more important

## Slides + Papers + Answer Keys

Use this when:

- you want stronger mapping confidence
- papers are image-heavy or OCR-noisy

Expected behavior:

- answer-key OCR improves validation
- some missing paper blocks can be recovered
- review rows still remain visible when recovery was needed

## Formal Papers Plus Revision Tests

Use this when:

- you have official yearly papers
- you also have revision tests, mocks, or modified syllabus papers

Model them with:

- `role = "formal"` for official papers
- `role = "auxiliary"` for revision-style papers

Expected behavior:

- auxiliary papers contribute to analysis context
- formal papers drive default retention

## Exam Prioritization

Use the outputs to prioritize revision:

- `Anchor` topics are stable targets across years
- `Core` topics recur often enough to deserve early coverage
- `Recurring` topics matter, but are less stable
- `One-off` topics are lower priority unless they matter conceptually

Hotness helps identify what is tested often.
Retention helps identify what persists across years.
They should be interpreted together, not merged into one score.
Each question is still counted against one primary knowledge point only.

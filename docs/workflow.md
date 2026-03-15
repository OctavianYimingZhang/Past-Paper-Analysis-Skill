# Workflow

## 1. Resolve Inputs

The analyzer reads a course spec and decides which material sources are available:

- `slides_dir`
- `notes_pdf`
- `papers[]`
- optional `answer_keys[]`

At least one of `slides_dir` or `notes_pdf` must be present.

## 2. Choose Source Strategy

The analyzer operates in two modes:

- **Preset-first mode** for known courses with curated defaults
- **Generic mode** for unknown courses

When a known preset is available and `slides_dir` exists, the analyzer prefers slide extraction first. If slides are unavailable or weak, it falls back to note-PDF extraction.

## 3. Extract Lecture Structure

### Preferred path

Use raw `.pptx` slide decks to infer:

- lecture order
- lecture titles
- candidate examinable statements

### Fallback path

Use lecture-note PDFs when slides are unavailable. If note text extraction is weak, the analyzer may fall back to OCR.

## 4. Extract Initial Knowledge Points

The analyzer scans lecture content and pulls out candidate lines that look like examinable units.

It filters boilerplate and then clusters overlapping candidates into optimized knowledge points.

## 5. Segment Paper Questions

The analyzer parses each paper using question markers and parser hints.

Supported patterns include:

- standard MCQ numbering
- grouped/shared-context questions
- explicit `question_numbers` sequences for papers that skip printed numbers
- auxiliary papers such as revision tests

## 6. Optional Answer-Key OCR

If answer keys are present:

- embedded images are extracted from the DOCX file
- OCR is run over those images
- answer and explanation blocks are parsed

Answer-key OCR is used to:

- validate paper segmentation
- improve topic mapping confidence
- recover placeholder question records when the paper OCR is too weak

## 7. Map Questions to Knowledge Points

Each question is mapped to:

- one **primary lecture**
- one **primary knowledge point**
- optional **secondary points** for context only

Only the primary point is counted in hotness and retention.

## 8. Compute Statistics

### Hotness

Hotness tracks how often a primary knowledge point is tested:

- raw hits
- yearly counts
- question-share percentage
- rank

### Retention

Retention is computed over `formal` papers only by default:

- years present
- retention fraction
- retention percent
- `meets_50`
- `meets_75`
- retention band

Auxiliary papers can be analyzed without changing default retention unless the spec explicitly chooses otherwise.

## 9. Emit Review Queue

The analyzer never hides weak cases. It records them in `Review_Queue`, including:

- low OCR confidence
- weak lecture/topic mapping
- missing question numbers
- answer-key parse failures
- paper question undercounts

## 10. Export Outputs

The analyzer writes:

- Excel workbook
- JSON analysis payload
- Markdown summary

All public-facing labels and generated summaries are kept in English.

## Course Spec Schema

Use one JSON file per course. Public example specs must avoid private absolute paths. Local runnable specs can contain absolute paths, but generate them outside the public skill tree.

```json
{
  "course_id": "example-course",
  "course_name": "Example Course",
  "preset_id": "biochemistry",
  "output_language": "en",
  "slides_dir": "/absolute/path/to/slide-decks",
  "notes_pdf": "/absolute/path/to/notes.pdf",
  "slides_manifest": [
    {
      "file_name": "Lecture 1.pptx",
      "lecture_id": "L01",
      "lecture_number": 1,
      "lecture_title": "Introduction"
    }
  ],
  "formal_years": ["2021", "2022", "2024"],
  "paper_skip_pages": 2,
  "notes": {
    "ocr_fallback_mode": "text_first",
    "min_detected_lectures": 6,
    "lecture_header_patterns": [
      "Lecture\\s*(\\d{1,2})",
      "\\bL(\\d{1,2})\\b"
    ]
  },
  "parser_hints": {
    "paper_strategy": "mcq_standard"
  },
  "papers": [
    {
      "year": "2021",
      "role": "formal",
      "pdf": "/absolute/path/to/paper.pdf",
      "expected_questions": 50
    },
    {
      "year": "2024",
      "role": "formal",
      "pdf": "/absolute/path/to/paper.pdf",
      "expected_questions": 49,
      "question_numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
    },
    {
      "year": "Revision",
      "role": "auxiliary",
      "pdf": "/absolute/path/to/revision.pdf",
      "expected_questions": 24
    }
  ],
  "answer_keys": [
    {
      "year": "2021",
      "docx": "/absolute/path/to/answer-key.docx"
    }
  ],
  "manual_overrides": {
    "2021-Q01": {
      "lecture_id": "L12",
      "point_id": "L12-T03",
      "secondary_point_ids": ["L13-T02"],
      "notes": "Use only after the automatic pass has shown a stable failure mode."
    }
  }
}
```

### Required fields

- `course_id`: stable slug used in filenames and JSON keys.
- `course_name`: human-readable title.
- `output_language`: currently only `"en"` is supported in the public analyzer.
- `papers[]`: each entry needs `year`, `role`, `pdf`, and `expected_questions`.
- At least one of `slides_dir` or `notes_pdf`.

### Optional fields

- `preset_id`: known-course preset. Current public presets are documented in [presets.md](./presets.md).
- `slides_manifest`: optional explicit file-to-lecture mapping. Use this when slide filenames do not reliably encode lecture order.
- `formal_years`: if omitted, the analyzer derives them from `papers[]` where `role == "formal"`.
- `paper_skip_pages`: number of front pages to skip before question extraction. Use `2` for the common Manchester MCQ layout.
- `notes.ocr_fallback_mode`: `"text_first"` or `"ocr_only"`.
- `notes.min_detected_lectures`: minimum lecture headers expected before note OCR fallback is triggered.
- `notes.lecture_header_patterns`: regex list. Each regex must contain one capturing group for the lecture number.
- `parser_hints`: strategy-specific hints. Keep this sparse and course-level.
- `papers[].role`: `"formal"` or `"auxiliary"`. Only formal papers count toward default retention.
- `papers[].question_numbers`: explicit numbering sequence for papers that skip printed question numbers.
- `answer_keys[]`: optional. Strongly preferred when available.
- `manual_overrides`: keyed by `YEAR-QNN`. Use only for persistent extraction failures or known bad OCR.

### Output expectations

The analyzer writes:

- Excel workbook
- JSON analysis payload
- Markdown summary

Each output must keep hotness and retention separate:

- hotness: `raw_question_hits`, `question_share_percent`, `hotness_rank`, per-year counts
- retention: `years_present`, `retention_fraction`, `retention_percent`, `meets_50`, `meets_75`, `retention_band`

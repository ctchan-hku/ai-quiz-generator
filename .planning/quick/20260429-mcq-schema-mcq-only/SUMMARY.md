---
status: complete
---

Implemented `backend/app/models/mcq_constraints.py`; slim `schemas.py` (Quiz = list of MultipleChoiceQuestion only); `prompts.MULTIPLE_CHOICE_INSTRUCTIONS` uses shared counts; validators on options length and correct_indices (non-empty, in-range, no dupes); `test_mcq_schema.py` + parser tests. Frontend: `config/mcq_constraints.ts`, `lib/mcqLabels.ts`, `QuizDisplay`/clipboard labels A–F; `quiz.ts` flat MCQ shape. Backend pytest 42; `tsc` pass.

# Quick: MCQ-only schema (2–6 options, ≥1 correct)

**Goal:** Remove unused question unions; enforce `multiple_choice` only with option count `[2, 6]` (default **4** in prompts), distinct `correct_indices` in range, minimum one correct; mirror constants on frontend (`mcq_constraints` + option labels).

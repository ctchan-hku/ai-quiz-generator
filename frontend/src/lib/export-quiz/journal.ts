import type { MultipleChoiceQuestion } from "../../types/quiz";
import type { QuizFormConfig } from "../../types/quiz-machine";
import {
  EXPORT_JOURNAL_SCHEMA_VERSION,
  type BuildQuizExportRecordParams,
  type ExportJournal,
  type ExportedQuizQuestion,
  type QuizExportRecord,
  type QuizGenerationRequestSnapshot,
} from "../../types/export-journal";

export const EXPORT_JOURNAL_STORAGE_KEY = "mastery-exec-quiz-export-journal";

export type {
  BuildQuizExportRecordParams,
  ExportJournal,
  ExportedQuizQuestion,
  QuizExportRecord,
  QuizGenerationRequestSnapshot,
} from "../../types/export-journal";

export function toQuizGenerationRequestSnapshot(
  form: QuizFormConfig,
): QuizGenerationRequestSnapshot {
  return {
    num_questions: form.numQuestions,
    primary_model_id: form.model.trim(),
    few_shot_examples: [...(form.few_shot_examples ?? [])],
    user_instruction_lines: [...(form.user_instructions ?? [])],
    ...(form.battle_opponent_model?.trim()
      ? { battle_opponent_model_id: form.battle_opponent_model.trim() }
      : {}),
  };
}

function emptyJournal(): ExportJournal {
  return {
    schema_version: EXPORT_JOURNAL_SCHEMA_VERSION,
    updated_at: new Date().toISOString(),
    quizzes: [],
  };
}

export function loadJournal(): ExportJournal {
  try {
    const raw = localStorage.getItem(EXPORT_JOURNAL_STORAGE_KEY);
    if (raw == null || raw === "") return emptyJournal();
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object") return emptyJournal();
    const o = parsed as Record<string, unknown>;
    if (o.schema_version !== EXPORT_JOURNAL_SCHEMA_VERSION || !Array.isArray(o.quizzes)) {
      return emptyJournal();
    }
    return {
      schema_version: EXPORT_JOURNAL_SCHEMA_VERSION,
      updated_at:
        typeof o.updated_at === "string"
          ? o.updated_at
          : new Date().toISOString(),
      quizzes: o.quizzes as QuizExportRecord[],
    };
  } catch {
    return emptyJournal();
  }
}

export function saveJournal(j: ExportJournal): void {
  const next: ExportJournal = {
    ...j,
    updated_at: new Date().toISOString(),
  };
  try {
    localStorage.setItem(EXPORT_JOURNAL_STORAGE_KEY, JSON.stringify(next));
  } catch (e) {
    if (e instanceof DOMException && e.name === "QuotaExceededError") {
      throw new Error(
        "Storage full — clear the journal or free browser space.",
      );
    }
    throw e;
  }
}

export function appendQuizRecord(record: QuizExportRecord): ExportJournal {
  const j = loadJournal();
  j.quizzes.push(record);
  saveJournal(j);
  return j;
}

export function clearJournal(): void {
  localStorage.removeItem(EXPORT_JOURNAL_STORAGE_KEY);
}

function buildExportedQuizQuestion(
  q: MultipleChoiceQuestion,
  index: number,
  comment: string,
): ExportedQuizQuestion {
  return {
    index,
    question_type: q.question_type,
    question: q.question,
    options: q.options,
    correct_indices: q.correct_indices,
    explanation: q.explanation,
    comment: comment.trim(),
  };
}

export function removeQuizRecord(index: number): ExportJournal {
  const j = loadJournal();
  j.quizzes.splice(index, 1);
  saveJournal(j);
  return j;
}

export function buildQuizExportRecord(
  params: BuildQuizExportRecordParams,
): QuizExportRecord {
  const { quiz, topic, commentsByIndex, generationRequestSnapshot } = params;

  const record: QuizExportRecord = {
    exported_at: new Date().toISOString(),
    topic: topic.trim(),
    model_used: quiz.model_used,
    cost_usd: quiz.cost_usd,
    source: quiz.source,
    truncated: quiz.truncated,
    questions: quiz.questions.map((q, i) =>
      buildExportedQuizQuestion(q, i, commentsByIndex[i] ?? ""),
    ),
  };

  if (generationRequestSnapshot != null) {
    record.generation_request = generationRequestSnapshot;
  }

  return record;
}

export function downloadJournalFile(
  journal: ExportJournal,
  filename = "quiz-export-journal.json",
): void {
  const json = JSON.stringify(journal, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

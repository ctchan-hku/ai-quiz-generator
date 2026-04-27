import {
  TOPIC_MAX_LENGTH,
  TOPIC_TEXTAREA_MIN_HEIGHT_PX,
} from "../../config/quiz";

interface TopicFieldProps {
  topic: string;
  onTopicChange: (value: string) => void;
  isLoading: boolean;
}

export function TopicField({ topic, onTopicChange, isLoading }: TopicFieldProps) {
  return (
    <>
      <h2 className="mt-0 mb-4 font-[family-name:var(--font-heading)] text-xl font-semibold text-[var(--color-text)]">
        Topic
      </h2>
      <label
        className="mb-1 block text-sm font-bold text-[var(--color-text)]"
        htmlFor="quiz-topic"
      >
        What should the quiz cover?
      </label>
      <textarea
        id="quiz-topic"
        className="input mb-4 resize-y"
        style={{ minHeight: TOPIC_TEXTAREA_MIN_HEIGHT_PX }}
        placeholder="e.g. HKU history, organic chemistry, Python basics…"
        value={topic}
        onChange={(e) => onTopicChange(e.target.value)}
        disabled={isLoading}
        maxLength={TOPIC_MAX_LENGTH}
      />
    </>
  );
}

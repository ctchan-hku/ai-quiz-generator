import { Textarea } from "@/components/ui/textarea";
import {
  QUIZ_FORM_SECTION_TITLE_CLASS,
  TOPIC_MAX_LENGTH,
  TOPIC_TEXTAREA_MIN_HEIGHT_PX,
} from "../../config/quiz-form";

interface TopicFieldProps {
  topic: string;
  onTopicChange: (value: string) => void;
  isLoading: boolean;
}

export function TopicField({
  topic,
  onTopicChange,
  isLoading,
}: TopicFieldProps) {
  return (
    <div className="mb-4">
      <p
        id="quiz-coverage-heading"
        className={`${QUIZ_FORM_SECTION_TITLE_CLASS} mb-2 block`}
      >
        Quiz Coverage
      </p>
      <Textarea
        id="quiz-topic"
        className="resize-y"
        aria-labelledby="quiz-coverage-heading"
        style={{ minHeight: TOPIC_TEXTAREA_MIN_HEIGHT_PX }}
        placeholder="e.g. HKU history, organic chemistry, Python basics…"
        value={topic}
        onChange={(e) => onTopicChange(e.target.value)}
        disabled={isLoading}
        maxLength={TOPIC_MAX_LENGTH}
      />
    </div>
  );
}

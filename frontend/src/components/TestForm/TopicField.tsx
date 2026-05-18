import { Textarea } from "@/components/ui/textarea";
import { TOPIC_MAX_LENGTH, TOPIC_TEXTAREA_MIN_HEIGHT_PX } from "../../config/test-form";
import { TestFormSectionTitle } from "./TestFormSectionTitle";

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
      <TestFormSectionTitle
        as="p"
        id="test-coverage-heading"
        className="mb-2 block"
      >
        Test coverage
      </TestFormSectionTitle>
      <Textarea
        id="test-topic"
        className="resize-y"
        aria-labelledby="test-coverage-heading"
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

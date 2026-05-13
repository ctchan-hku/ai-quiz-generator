import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  TOPIC_MAX_LENGTH,
  TOPIC_TEXTAREA_MIN_HEIGHT_PX,
} from "../../config/quiz";

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
    <div className="mb-6">
      <h2 className="mt-0 mb-4 font-heading text-xl font-semibold text-foreground">
        Topic
      </h2>
      <Label
        className="mb-2 block text-sm font-bold text-foreground"
        htmlFor="quiz-topic"
      >
        What should the quiz cover?
      </Label>
      <Textarea
        id="quiz-topic"
        className="resize-y"
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

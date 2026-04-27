import type { ModelInfo } from "../../types/api";
import type { QuizFormConfig } from "../../types/quiz-machine";

export interface QuizFormProps {
  topic: string;
  onTopicChange: (topic: string) => void;
  numQuestions: number;
  onNumQuestionsChange: (n: number) => void;
  model: string;
  onModelChange: (model: string | null) => void;
  models: ModelInfo[];
  modelsLoading: boolean;
  modelsError: string | null;
  onSubmit: (config: QuizFormConfig) => void;
  isLoading: boolean;
}

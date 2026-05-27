export interface ModelPrice {
  input: number | null;
  output: number | null;
}

export interface ModelInfo {
  id: string;
  label: string;
  price: ModelPrice;
}

export interface MultipleChoiceQuestion {
  question_type: "multiple_choice";
  question: string;
  options: string[];
  correct_indices: number[];
  explanation: string;
}

export interface TestSummary {
  id: string;
  name: string;
  num_questions: number;
}

export interface CourseGroupWithTests {
  id: string;
  name: string;
  tests: TestSummary[];
}

export interface QuestionEditRequest {
  model: string;
  topic: string;
  question: MultipleChoiceQuestion;
  comment: string;
}

export interface GenerateTestRequest {
  topic: string;
  num_questions: number;
  model: string;
  pipeline_version: 1 | 2;
  few_shot_examples: string[];
  user_instructions: string[];
  selected_test_ids: string[];
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface QuestionEditResponse {
  question: MultipleChoiceQuestion;
  cost_usd: number;
}

export interface GenerateTestResponse {
  questions: MultipleChoiceQuestion[];
  model_used: string;
  cost_usd: number;
}

export interface LoginResponse {
  user_id: string;
  username: string;
  course_groups: CourseGroupWithTests[];
}

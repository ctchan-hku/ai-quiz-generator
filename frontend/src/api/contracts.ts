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
  questionType: "multiple_choice";
  question: string;
  options: string[];
  correctIndices: number[];
  explanation: string;
}

export interface TestSummary {
  id: string;
  name: string;
  numQuestions: number;
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

export interface LoginRequest {
  username: string;
  password: string;
}

export interface QuestionEditResponse {
  question: MultipleChoiceQuestion;
  costUsd: number;
}

export interface GenerateTestRequest {
  topic: string;
  numQuestions: number;
  model: string;
  pipelineVersion: 1 | 2;
  fewShotExamples: string[];
  userInstructions: string[];
  selectedTestIds: string[];
}

export interface GenerateTestResponse {
  questions: MultipleChoiceQuestion[];
  modelUsed: string;
  costUsd: number;
}

export interface LoginResponse {
  userId: string;
  username: string;
  courseGroups: CourseGroupWithTests[];
}

export interface PdfChunk {
  chunkId: string;
  pageNumber: number;
  content: string;
  type: string;
}

export interface ParsedPdfDocument {
  filename: string;
  chunks: PdfChunk[];
}

export interface UploadDocumentsResponse {
  documents: ParsedPdfDocument[];
}

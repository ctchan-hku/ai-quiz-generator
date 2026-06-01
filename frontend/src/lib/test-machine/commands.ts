import { editQuestion, generateTest } from "@/api";
import type {
  GenerateTestRequest,
  MultipleChoiceQuestion,
} from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import type { GenerateTestMachineSuccess, QuestionEditParams } from "./types";

export async function runGenerateTest(
  config: TestFormConfig,
  signal: AbortSignal,
): Promise<GenerateTestMachineSuccess> {
  const requestFields: Omit<GenerateTestRequest, "model"> = {
    topic: config.topic,
    numQuestions: config.numQuestions,
    pipelineVersion: config.pipelineVersion,
    fewShotExamples: config.fewShotExamples,
    userInstructions: config.userInstructions,
    selectedTestIds: config.selectedTestIds,
  };

  if (config.battleEnabled) {
    const [left, right] = await Promise.all([
      generateTest(
        { ...requestFields, model: config.models[0].trim() },
        signal,
      ),
      generateTest(
        { ...requestFields, model: config.models[1].trim() },
        signal,
      ),
    ]);
    return { mode: "battle", payload: { left, right } };
  }

  const test = await generateTest(
    { ...requestFields, model: config.models[0].trim() },
    signal,
  );
  return { mode: "single", payload: test };
}

export async function runEditQuestion(
  params: QuestionEditParams,
  signal: AbortSignal,
): Promise<MultipleChoiceQuestion> {
  const { comment, model, topic, question } = params;
  return editQuestion(
    { model, topic, question, comment: comment.trim() },
    signal,
  );
}

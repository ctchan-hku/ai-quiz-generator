import { editQuestion, generateTest } from "@/api";
import type {
  GenerateTestRequest,
  MultipleChoiceQuestion,
} from "@/api/contracts";
import type { TestFormConfig } from "@/config/test-form";
import type { GenerateTestMachineSuccess, QuestionEditParams } from "./types";

export async function runGenerateTest(
  formConfig: TestFormConfig,
  signal: AbortSignal,
): Promise<GenerateTestMachineSuccess> {
  const requestFields: Omit<GenerateTestRequest, "model"> = {
    topic: formConfig.topic,
    numQuestions: formConfig.numQuestions,
    pipelineVersion: formConfig.pipelineVersion,
    fewShotExamples: formConfig.fewShotExamples,
    userInstructions: formConfig.userInstructions,
    selectedTestIds: formConfig.selectedTestIds,
  };

  if (formConfig.battleEnabled) {
    const [left, right] = await Promise.all([
      generateTest(
        { ...requestFields, model: formConfig.models[0].trim() },
        signal,
      ),
      generateTest(
        { ...requestFields, model: formConfig.models[1].trim() },
        signal,
      ),
    ]);
    return { mode: "battle", payload: { left, right } };
  }

  const test = await generateTest(
    { ...requestFields, model: formConfig.models[0].trim() },
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

import { generateTest } from "../../api";
import type { TestFormConfig } from "../../config/test-form";
import type { GenerateTestMachineSuccess } from "./types";

export async function runGenerateTest(
  config: TestFormConfig,
  signal: AbortSignal,
): Promise<GenerateTestMachineSuccess> {
  if (config.battleEnabled) {
    const sharedFields = {
      topic: config.topic,
      numQuestions: config.numQuestions,
      pipeline_version: config.pipeline_version,
      few_shot_examples: config.few_shot_examples,
      user_instructions: config.user_instructions,
      selected_test_ids: config.selected_test_ids,
    };

    const singleGenerateConfig = (modelId: string): TestFormConfig => ({
      ...sharedFields,
      models: [modelId, ""],
      battleEnabled: false,
    });

    const [left, right] = await Promise.all([
      generateTest(singleGenerateConfig(config.models[0]), signal),
      generateTest(singleGenerateConfig(config.models[1]), signal),
    ]);
    return { mode: "battle", payload: { left, right } };
  }

  const test = await generateTest(config, signal);
  return { mode: "single", payload: test };
}

import { generateTest } from "../../api";
import type { TestFormConfig } from "../../config/test-form";
import type { GenerateTestMachineSuccess } from "./types";

export async function runGenerateTest(
  config: TestFormConfig,
  signal: AbortSignal,
): Promise<GenerateTestMachineSuccess> {
  if (config.battleEnabled) {
    const [left, right] = await Promise.all([
      generateTest(config, signal, config.models[0]),
      generateTest(config, signal, config.models[1]),
    ]);
    return { mode: "battle", payload: { left, right } };
  }

  const test = await generateTest(config, signal);
  return { mode: "single", payload: test };
}

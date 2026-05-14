/**
 * USD per question by pipeline version (1 = single-call, 2 = multi-step).
 * Keys are the model ids from `AVAILABLE_MODELS` (`backend/.env.example`).
 */
export const modelGenerationCostPerQuestionUsd = {
  "gemini-3-flash": { v1: 0.0015, v2: 0.003 },
  "gemini-3.1-pro": { v1: 0.01, v2: 0.01 },
  "claude-sonnet-4.6": { v1: 0.01, v2: 0.015 },
  "gpt-5.1-instant": { v1: 0.0045, v2: 0.005 },
  "grok-4.20-multi-agent": { v1: 0.006, v2: 0 },
  "deepseek-v4-pro-e": { v1: 0.01, v2: 0.01 },
} as const;

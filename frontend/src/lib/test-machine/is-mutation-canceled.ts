import { CanceledError, isAxiosError } from "axios";

export function isMutationCanceled(err: unknown): boolean {
  if (!isAxiosError(err)) return false;
  return err.code === "ERR_CANCELED" || err instanceof CanceledError;
}

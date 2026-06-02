import { useMutation } from "@tanstack/react-query";
import { getRequestErrorMessage, login } from "@/api";
import type { LoginResponse } from "@/api/contracts";

interface UseLoginParams {
  onSuccess: (response: LoginResponse) => void;
}

export function useLogin({ onSuccess }: UseLoginParams) {
  const mutation = useMutation({
    mutationFn: login,
    onSuccess,
  });

  return {
    submit: (username: string, password: string) =>
      mutation.mutate({ username, password }),
    isPending: mutation.isPending,
    error: mutation.isError ? getRequestErrorMessage(mutation.error) : null,
  };
}

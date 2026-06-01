import { useQuery } from "@tanstack/react-query";
import { getRequestErrorMessage, listModels } from "@/api";
import { MODELS_LIST_STALE_TIME_MS } from "@/config/test-form";

export function useModels() {
  const query = useQuery({
    queryKey: ["models"],
    queryFn: listModels,
    staleTime: MODELS_LIST_STALE_TIME_MS,
  });

  return {
    models: query.data ?? [],
    isLoading: query.isLoading,
    error: query.isError ? getRequestErrorMessage(query.error) : null,
  };
}

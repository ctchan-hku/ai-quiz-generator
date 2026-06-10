import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect } from "react";
import {
  listKnowledgeDocuments,
  toggleKnowledgeDocument,
  getRequestErrorMessage,
} from "@/api";

interface UseKnowledgeDocumentsParams {
  enabled: boolean;
}

export function useKnowledgeDocuments({
  enabled,
}: UseKnowledgeDocumentsParams) {
  const queryClient = useQueryClient();

  const {
    data: documents = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["knowledge-documents"],
    queryFn: listKnowledgeDocuments,
    enabled,
  });

  useEffect(() => {
    if (!enabled) {
      queryClient.removeQueries({ queryKey: ["knowledge-documents"] });
    }
  }, [enabled, queryClient]);

  const toggleMutation = useMutation({
    mutationFn: ({
      documentId,
      isActive,
    }: {
      documentId: string;
      isActive: boolean;
    }) => toggleKnowledgeDocument(documentId, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-documents"] });
    },
  });

  const toggleDocument = useCallback(
    (documentId: string, isActive: boolean) => {
      toggleMutation.mutate({ documentId, isActive });
    },
    [toggleMutation],
  );

  return {
    documents,
    isLoading,
    error: enabled && error ? getRequestErrorMessage(error) : null,
    toggleDocument,
    isToggling: toggleMutation.isPending,
  };
}

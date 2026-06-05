import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import {
  listKnowledgeDocuments,
  toggleKnowledgeDocument,
  getRequestErrorMessage,
} from "@/api";

export function useKnowledgeDocuments() {
  const queryClient = useQueryClient();

  const {
    data: documents = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["knowledge-documents"],
    queryFn: listKnowledgeDocuments,
  });

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
    error: error ? getRequestErrorMessage(error) : null,
    toggleDocument,
    isToggling: toggleMutation.isPending,
  };
}

import { useState, type Dispatch, type SetStateAction } from "react";
import { ChevronRight } from "lucide-react";

import { logoutSession } from "@/api";
import type { LoginResponse } from "@/api/contracts";
import { Button } from "@/components/ui/button";
import { CourseGroupsList } from "@/components/Login/CourseGroupsList";
import { LoginForm } from "@/components/Login/LoginForm";
import { useCourseTestSelection } from "@/hooks/useCourseTestSelection";
import { useDocumentUpload } from "@/hooks/useDocumentUpload";
import { DocumentUploadSection } from "./DocumentUploadSection";
import { TestFormSectionTitle } from "./TestFormSectionTitle";

interface CourseTestsSectionProps {
  loggedInUser: LoginResponse | null;
  onLoggedInUserChange: (user: LoginResponse | null) => void;
  selectedTestIds: string[];
  onSelectedTestIdsChange: Dispatch<SetStateAction<string[]>>;
  isLoading: boolean;
}

export function CourseTestsSection({
  loggedInUser,
  onLoggedInUserChange,
  selectedTestIds,
  onSelectedTestIdsChange,
  isLoading,
}: CourseTestsSectionProps) {
  const [isOpen, setIsOpen] = useState(true);
  const documentUpload = useDocumentUpload();
  const selection = useCourseTestSelection({
    courseGroups: loggedInUser?.courseGroups ?? [],
    selectedTestIds,
    onSelectedTestIdsChange: (ids) => onSelectedTestIdsChange(ids),
  });

  function handleDisconnect() {
    logoutSession();
    onLoggedInUserChange(null);
    onSelectedTestIdsChange([]);
    documentUpload.reset();
  }

  return (
    <details
      className="mb-4 overflow-visible text-left"
      open={isOpen}
      onToggle={(event) => setIsOpen(event.currentTarget.open)}
    >
      <TestFormSectionTitle
        as="summary"
        className="flex cursor-pointer list-none items-center gap-2 [&::-webkit-details-marker]:hidden"
      >
        <ChevronRight
          className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200${isOpen ? " rotate-90" : ""}`}
          aria-hidden
        />
        Course tests
        <span className="sr-only">
          {isOpen ? "Collapse section" : "Expand section"}
        </span>
      </TestFormSectionTitle>

      <div className="mt-3 space-y-4 overflow-visible">
        <p className="m-0 text-xs leading-relaxed text-muted-foreground">
          Log in to load course groups, select reference tests, and upload past
          exam papers or lecture slides.
        </p>

        {loggedInUser ? (
          <>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm text-muted-foreground">
                Courses loaded for{" "}
                <span className="font-medium text-foreground">
                  {loggedInUser.username}
                </span>
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={isLoading}
                onClick={handleDisconnect}
              >
                Disconnect
              </Button>
            </div>
            <CourseGroupsList
              courseGroups={loggedInUser.courseGroups}
              selectedTestIds={selectedTestIds}
              {...selection}
            />
            <DocumentUploadSection
              documents={documentUpload.documents}
              onUploadFiles={documentUpload.uploadFiles}
              isUploading={documentUpload.isUploading}
              notice={documentUpload.notice}
              error={documentUpload.error}
              disabled={isLoading}
            />
          </>
        ) : (
          <LoginForm onSuccess={onLoggedInUserChange} disabled={isLoading} />
        )}
      </div>
    </details>
  );
}

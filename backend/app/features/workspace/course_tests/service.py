from app.features.workspace.core.vector_search import VectorSearchService
from app.features.workspace.course_tests.models import FewShotMatch, FewShotResult


class FewShotSearchService(VectorSearchService):
    def find_few_shots(self, examples: list[str]) -> list[FewShotResult]:
        results: list[FewShotResult] = []

        for index, example in enumerate(examples):
            prompt = example.strip()
            if not prompt:
                results.append(
                    FewShotResult(
                        index=index,
                        prompt="",
                        matches=[],
                    )
                )
                continue

            scored = self.search(prompt)
            matches = [
                FewShotMatch(
                    question_id=str(document.metadata["question_id"]),
                    prompt=str(document.metadata["prompt"]),
                    options=list(document.metadata.get("options", [])),
                    score=float(score),
                )
                for document, score in scored
            ]
            results.append(
                FewShotResult(
                    index=index,
                    prompt=prompt,
                    matches=matches,
                )
            )

        return results

from app.features.workspace.core.service import VectorSearchService
from app.features.workspace.course_tests.models import SimilarityMatch, SimilarityResult


class SimilarityService(VectorSearchService):
    def find_similar_for_examples(self, examples: list[str]) -> list[SimilarityResult]:
        results: list[SimilarityResult] = []

        for index, example in enumerate(examples):
            prompt = example.strip()
            if not prompt:
                results.append(
                    SimilarityResult(
                        index=index,
                        prompt="",
                        matches=[],
                    )
                )
                continue

            scored = self.search(prompt)
            matches = [
                SimilarityMatch(
                    question_id=str(document.metadata["question_id"]),
                    prompt=str(document.metadata["prompt"]),
                    options=list(document.metadata.get("options", [])),
                    score=float(score),
                )
                for document, score in scored
            ]
            results.append(
                SimilarityResult(
                    index=index,
                    prompt=prompt,
                    matches=matches,
                )
            )

        return results

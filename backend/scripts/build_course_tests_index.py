import asyncio

from app.features.workspace.course_tests import build_course_tests_index


async def main() -> None:
    count = await build_course_tests_index()
    if count == 0:
        raise SystemExit("No embeddable questions found in MongoDB")


if __name__ == "__main__":
    asyncio.run(main())

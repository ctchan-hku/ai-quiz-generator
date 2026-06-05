import asyncio

from app.features.workspace.course_tests import sync_question_index

if __name__ == "__main__":
    asyncio.run(sync_question_index())

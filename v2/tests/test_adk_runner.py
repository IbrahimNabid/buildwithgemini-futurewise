import os
import asyncio

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "qwiklabs-gcp-04-7459370ad109"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east1"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from v2.agents.agent import coordinator_agent
from google.genai import types

async def test_coordinator_run():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=coordinator_agent,
        session_service=session_service,
        app_name="futurewise_v2_coordinator"
    )

    user_id = "test_user_taylor"
    session = await session_service.create_session(
        app_name="futurewise_v2_coordinator",
        user_id=user_id,
        state={"uid": user_id, "current_page": "overview"}
    )

    prompt = "I am on the overview page. Give me my high-level Money Brief or safe to spend summary."
    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)]
    )

    print("Running coordinator agent via ADK Runner...")
    reply_text = ""
    async for event in runner.run_async(
        session_id=session.id,
        user_id=user_id,
        new_message=user_msg
    ):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if p.text:
                    reply_text += p.text

    print("\n--- ADK RUNNER REAL AI RESPONSE ---")
    print(reply_text)
    print("-----------------------------------")
    assert len(reply_text) > 0

if __name__ == "__main__":
    asyncio.run(test_coordinator_run())

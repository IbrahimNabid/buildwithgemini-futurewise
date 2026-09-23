import os
import agentplatform
from google.genai.types import Content, Part
from agentplatform._genai import types

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-7459370ad109")
LOCATION = os.environ.get("MEMORY_BANK_LOCATION", "us-east1")
MEMORY_BANK_ID = os.environ.get("MEMORY_BANK_ID", "4417655201473757184")
RESOURCE_NAME = f"projects/754395904178/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"

client = agentplatform.Client(project=PROJECT_ID, location=LOCATION)

user_id = "test_user_taylor"
app_name = "futurewise"

conversation = [
    Content(
        role="user",
        parts=[
            Part(
                text=(
                    "Hey Futurewise! To give you some context on my finances: "
                    "I earn $68,000 a year as a graphic designer and get paid on the 1st and 15th of each month. "
                    "My main goal right now is building up a $10,000 emergency fund and contributing $200/month to an HSA. "
                    "I already completed your lessons on 401(k) matching and Roth vs Traditional IRAs yesterday. "
                    "For my spending, I usually spend $350 on groceries and $250 on weekend dining. "
                    "Also, I've decided to keep my Spotify Family plan, but definitely cancel my gym membership and the Disney+ free trial before next Tuesday."
                )
            )
        ],
    ),
    Content(
        role="model",
        parts=[
            Part(
                text="Got it, Taylor! I have noted your income, pay schedule, savings goals, completed lessons, and subscription decisions."
            )
        ],
    ),
]

events = [
    types.GenerateMemoriesRequestDirectContentsSourceEvent(content=c)
    for c in conversation
]

print("Generating memories via Memory Bank...")
op = client.agent_engines.generate_memories(
    name=RESOURCE_NAME,
    direct_contents_source=types.GenerateMemoriesRequestDirectContentsSource(events=events),
    scope={"user_id": user_id, "app_name": app_name},
)

print("Operation result:")
print(op)

print("\nRetrieving memories for user:", user_id)
memories = client.agent_engines.retrieve_memories(
    name=RESOURCE_NAME,
    scope={"user_id": user_id, "app_name": app_name},
)
print("Retrieved memories:")
for m in memories.memories:
    print(f"- Fact: {m.fact}")

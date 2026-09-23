import os
import agentplatform
from agentplatform._genai import types
from google.genai.types import Content, Part

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-7459370ad109")
LOCATION = os.environ.get("MEMORY_BANK_LOCATION", "us-east1")
MEMORY_BANK_ID = os.environ.get("MEMORY_BANK_ID", "4417655201473757184")
RESOURCE_NAME = f"projects/754395904178/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"

client = agentplatform.Client(project=PROJECT_ID, location=LOCATION)

customization_config = types.MemoryBankCustomizationConfig(
    memory_topics=[
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.USER_PERSONAL_INFO
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.USER_PREFERENCES
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.KEY_CONVERSATION_DETAILS
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            managed_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicManagedMemoryTopic(
                managed_topic_enum=types.ManagedTopicEnum.EXPLICIT_INSTRUCTIONS
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            custom_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic(
                label="income_and_pay_schedule",
                description="User's income, salary, wages, pay schedule, pay frequency, and pay dates.",
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            custom_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic(
                label="financial_goals",
                description="User's financial goals, savings targets, retirement targets, debt payoff plans, and emergency fund milestones.",
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            custom_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic(
                label="completed_lessons",
                description="Financial education lessons, topics, modules, or guides the user has completed or learned (e.g. Roth vs Traditional IRA, 401(k) match, HSA, FSA, credit scores, APR, compound interest).",
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            custom_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic(
                label="spending_habits",
                description="User's spending habits, discretionary vs non-discretionary expenses, budget status, dining out patterns, and routine purchase behavior.",
            )
        ),
        types.MemoryBankCustomizationConfigMemoryTopic(
            custom_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic(
                label="subscription_decisions",
                description="User's subscriptions, recurring services, free trials ending soon, and decisions on which subscriptions they want to keep or cancel.",
            )
        ),
    ],
    generate_memories_examples=[
        types.MemoryBankCustomizationConfigGenerateMemoriesExample(
            conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
                events=[
                    types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                        content=Content(
                            role="user",
                            parts=[
                                Part(
                                    text="I make $75,000 a year and get paid bi-weekly on alternating Fridays."
                                )
                            ],
                        )
                    )
                ]
            ),
            generated_memories=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                    fact="The user earns $75,000 annually and gets paid bi-weekly on alternating Fridays."
                )
            ],
        ),
        types.MemoryBankCustomizationConfigGenerateMemoriesExample(
            conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
                events=[
                    types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                        content=Content(
                            role="user",
                            parts=[
                                Part(
                                    text="My primary goal is to save a 6-month emergency fund of $18,000 and pay off my $4,000 credit card debt."
                                )
                            ],
                        )
                    )
                ]
            ),
            generated_memories=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                    fact="The user's financial goals are building an $18,000 6-month emergency fund and paying off $4,000 of credit card debt."
                )
            ],
        ),
        types.MemoryBankCustomizationConfigGenerateMemoriesExample(
            conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
                events=[
                    types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                        content=Content(
                            role="user",
                            parts=[
                                Part(
                                    text="I just finished the Roth vs Traditional IRA module and the HSA comparison lesson."
                                )
                            ],
                        )
                    )
                ]
            ),
            generated_memories=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                    fact="The user completed the Roth vs Traditional IRA module and the HSA comparison lesson."
                )
            ],
        ),
        types.MemoryBankCustomizationConfigGenerateMemoriesExample(
            conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
                events=[
                    types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                        content=Content(
                            role="user",
                            parts=[
                                Part(
                                    text="I usually spend $450 on groceries each month and about $300 on takeout."
                                )
                            ],
                        )
                    )
                ]
            ),
            generated_memories=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                    fact="The user typically spends $450/month on groceries and $300/month on takeout."
                )
            ],
        ),
        types.MemoryBankCustomizationConfigGenerateMemoriesExample(
            conversation_source=types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSource(
                events=[
                    types.MemoryBankCustomizationConfigGenerateMemoriesExampleConversationSourceEvent(
                        content=Content(
                            role="user",
                            parts=[
                                Part(
                                    text="I want to keep Spotify and Apple Music, but I definitely want to cancel my gym membership and the streaming free trial before it renews on Thursday."
                                )
                            ],
                        )
                    )
                ]
            ),
            generated_memories=[
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                    fact="The user wants to keep Spotify and Apple Music subscriptions."
                ),
                types.MemoryBankCustomizationConfigGenerateMemoriesExampleGeneratedMemory(
                    fact="The user decided to cancel their gym membership and streaming free trial before Thursday."
                ),
            ],
        ),
    ],
    enable_third_person_memories=True,
)

memory_bank_config = types.ReasoningEngineContextSpecMemoryBankConfig(
    customization_configs=[customization_config],
)

context_spec = types.ReasoningEngineContextSpec(
    memory_bank_config=memory_bank_config,
)

agent_engine_config = types.AgentEngineConfig(
    context_spec=context_spec,
)

print(f"Updating Memory Bank instance {RESOURCE_NAME}...")
updated = client.agent_engines.update(
    name=RESOURCE_NAME,
    config=agent_engine_config,
)
print("Updated successfully!")
print(updated)

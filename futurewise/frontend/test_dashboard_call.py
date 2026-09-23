import asyncio, os, httpx, uuid, json, re
os.environ['AGENT_ENGINE_RESOURCE_NAME'] = 'projects/754395904178/locations/us-east1/reasoningEngines/8383074673373478912'
os.environ['AGENT_DIRECTORY'] = 'app'
import main

prompt = """You are Taylor's financial assistant. Run your tools to inspect Taylor's actual accounts (user_id="taylor_27"): check free trials, check monthly budget and transactions, check financial stability, and search the latest economic news.
Then return a valid JSON object only (no extra explanation) with:
{
  "safe_to_spend_this_week": <float number, remaining safe-to-spend>,
  "budget_used_percent": <float number, total spent / budget * 100>,
  "top_spending_categories": [{"category": <name>, "amount": <total spent in positive dollars>}],
  "trials_ending": [{"service": <name>, "days_left": <int>, "cost_if_forgotten": <float>, "cancel_by_date": <date string>}],
  "months_of_expenses_covered": <float>,
  "savings_rate_percent": <float>,
  "news_headline": <string>,
  "what_it_means_for_me": <string>
}
Make sure top_spending_categories lists the top categories from Taylor's transactions (Rent, Groceries, Dining, Transit, Subscriptions, Utilities).
Make sure trials_ending lists the trials ending soonest (Calm, Duolingo, TestFitnessPro, etc.)."""

async def test():
    async with httpx.AsyncClient(headers=main._auth_headers(), timeout=180) as client:
        card = await main._get_card(client)
        from a2a.client import ClientConfig, ClientFactory
        from a2a.types import TransportProtocol, Message, Role, Part, TextPart
        factory = ClientFactory(ClientConfig(supported_transports=[TransportProtocol.jsonrpc, TransportProtocol.http_json], httpx_client=client))
        a2a_client = factory.create(card)
        msg = Message(message_id=str(uuid.uuid4()), role=Role.user, parts=[Part(root=TextPart(text=prompt))])
        last_task = None
        async for event in a2a_client.send_message(msg):
            if isinstance(event, tuple):
                task, update = event
                if task: last_task = task
        if last_task:
            for m in reversed(last_task.history):
                if m.role == Role.agent:
                    for p in m.parts:
                        root = getattr(p, 'root', p)
                        if hasattr(root, 'text'):
                            print("RAW TEXT:\n", root.text)
                            match = re.search(r'\{.*\}', root.text, re.DOTALL)
                            if match:
                                data = json.loads(match.group(0))
                                print("\nPARSED SUCCESSFULLY:")
                                print(json.dumps(data, indent=2))
                                return data

asyncio.run(test())

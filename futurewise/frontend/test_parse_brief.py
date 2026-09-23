import asyncio, os, httpx, uuid, json, re
os.environ['AGENT_ENGINE_RESOURCE_NAME'] = 'projects/754395904178/locations/us-east1/reasoningEngines/8383074673373478912'
os.environ['AGENT_DIRECTORY'] = 'app'
import main

async def test():
    async with httpx.AsyncClient(headers=main._auth_headers(), timeout=180) as client:
        card = await main._get_card(client)
        from a2a.client import ClientConfig, ClientFactory
        from a2a.types import TransportProtocol, Message, Role, Part, TextPart
        factory = ClientFactory(ClientConfig(supported_transports=[TransportProtocol.jsonrpc, TransportProtocol.http_json], httpx_client=client))
        a2a_client = factory.create(card)
        msg = Message(message_id=str(uuid.uuid4()), role=Role.user, parts=[Part(root=TextPart(text="Give me my Money Brief"))])
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
                            text = root.text
                            print("RAW AGENT TEXT:")
                            print(text)
                            
                            # Parse structured data from text
                            data = {
                                "safe_to_spend_this_week": 0.0,
                                "budget_used_percent": 0.0,
                                "top_spending_categories": [],
                                "trials_ending": [],
                                "months_of_expenses_covered": 0.0,
                                "savings_rate_percent": 0.0,
                                "news_headline": "",
                                "what_it_means_for_me": ""
                            }
                            
                            # Safe to spend
                            m_spend = re.search(r"weekly safe-to-spend remainder is \$?([0-9.,]+)", text, re.I)
                            if m_spend: data["safe_to_spend_this_week"] = float(m_spend.group(1).replace(",", ""))
                            
                            # Budget
                            m_bud = re.search(r"total monthly budget of \$?([0-9.,]+).*?spent \$?([0-9.,]+)", text, re.I | re.DOTALL)
                            if m_bud:
                                b_tot = float(m_bud.group(1).replace(",", ""))
                                b_sp = float(m_bud.group(2).replace(",", ""))
                                if b_tot > 0: data["budget_used_percent"] = round((b_sp / b_tot) * 100, 1)
                                
                            # Categories
                            cats = re.findall(r"\*\s+\*\*([^*]+)\*\*:\s+Spent\s+-\$?([0-9.,]+)", text)
                            for c_name, c_amt in cats:
                                if c_name.lower() != "income":
                                    data["top_spending_categories"].append({
                                        "category": c_name.strip(),
                                        "amount": float(c_amt.replace(",", ""))
                                    })
                            data["top_spending_categories"].sort(key=lambda x: x["amount"], reverse=True)
                            data["top_spending_categories"] = data["top_spending_categories"][:5]
                            
                            # Trials
                            trials = re.findall(r"\*\s+\*\*([^*]+)\s*\(([^)]+)\)\*\*:\s+Ends in\s+(\d+)\s+days.*?Will cost \$?([0-9.,]+)/([a-zA-Z0-9]+).*?Recommended cancel date:\s+([^.\n]+)", text)
                            for t_serv, t_plat, t_days, t_cost, t_cycle, t_date in trials:
                                data["trials_ending"].append({
                                    "service": f"{t_serv.strip()} ({t_plat.strip()})",
                                    "days_left": int(t_days),
                                    "cost_if_forgotten": float(t_cost.replace(",", "")),
                                    "cancel_by_date": t_date.strip()
                                })
                                
                            # Stability
                            m_cov = re.search(r"([0-9.]+)\s+months of expenses covered", text, re.I)
                            if m_cov: data["months_of_expenses_covered"] = float(m_cov.group(1))
                            m_sav = re.search(r"monthly savings rate is\s+([0-9.]+)%", text, re.I)
                            if m_sav: data["savings_rate_percent"] = float(m_sav.group(1))
                            
                            # News
                            m_news = re.search(r"\*\*Economy Headline:\*\*\s*\n*(.+)", text, re.DOTALL)
                            if m_news:
                                news_block = m_news.group(1).strip()
                                parts = news_block.split("\n", 1)
                                data["news_headline"] = parts[0].strip()
                                data["what_it_means_for_me"] = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                                
                            print("\nSTRUCTURED DASHBOARD RESULT:")
                            print(json.dumps(data, indent=2))
                            return data

asyncio.run(test())

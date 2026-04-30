class QAAgent:

    def __init__(self, llm, config):
        self.llm = llm
        self.config = config

    async def run(self, state):

        question = state["question"]

        # 🔥 Identify relevant KPI
        relevant_kpis = [
            k for k in state["kpis"]
            if k["status"] != "green"
        ]

        # Simple heuristic (can upgrade later)
        kpi = relevant_kpis[0] if relevant_kpis else None

        # 🔥 Retrieve best practices
        chunks = state.get("retrieved_chunks", {}).get(kpi["raw_kpi"], [])

        context = "\n".join([c["text"] for c in chunks])

        prompt = f"""
        You are an ESG advisor.

        Question: {question}

        KPI: {kpi['kpi_name']}
        Gap: {kpi['gap_pct']}%

        Best Practices:
        {context}

        Answer clearly with actionable steps.
        """

        answer = await self.llm.generate("", prompt)

        state["answer"] = answer
        return state
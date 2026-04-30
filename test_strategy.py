import asyncio
from app.graph.nodes.strategy_synthesizer import StrategySynthesizer   # replace with your filename


# 🔹 Mock LLM (so you can test without API)
class DummyLLM:
    async def generate(self, system, user):
        return f"Generated recommendation for: {user[:50]}"


# 🔹 Dummy config
config = {
    "prompts": {
        "strategy_synthesizer": {
            "system": "You are an ESG expert.",
            "user_template": (
                "Company: {company}\n"
                "KPI: {kpi_name}\n"
                "Value: {company_value} vs {peer_value}\n"
                "Gap: {gap_pct}\n"
                "{kpi_context}\n"
                "Best practices:\n{retrieved_chunks}"
            )
        }
    },
    "llm": {
        "retry_attempts": 2,
        "retry_backoff_seconds": 1
    }
}


# 🔹 Dummy state (VERY IMPORTANT)
state = {
    "company": "ABC Corp",
    "kpis": [
        {
            "kpi_name": "Carbon Emissions",
            "raw_kpi": "emissions",
            "company_value": 100,
            "peer_value": 70,
            "gap_pct": 30,
            "status": "red",
            "direction": "lower_better"
        },
        {
            "kpi_name": "Water Usage",
            "raw_kpi": "water",
            "company_value": 200,
            "peer_value": 150,
            "gap_pct": 25,
            "status": "amber",
            "direction": "lower_better"
        }
    ],
    "retrieved_chunks": {
        "emissions": [
            {"text": "Use renewable energy", "source": "Report A", "year": 2023}
        ],
        "water": []
    }
}


async def main():
    synthesizer = StrategySynthesizer(DummyLLM(), config)
    result = await synthesizer.run(state)
    print("\nFINAL OUTPUT:\n", result["recommendations"])


if __name__ == "__main__":
    asyncio.run(main())
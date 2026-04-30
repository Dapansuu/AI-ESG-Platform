from loguru import logger
import asyncio


class StrategySynthesizer:

    def __init__(self, llm, config):
        self.llm = llm
        self.config = config

    async def run(self, state):

        recs = []
        prompt = self.config["prompts"]["strategy_synthesizer"]

        # ---------------------------------
        # 🔥 PRIORITIZE KPIs (CRITICAL FIX)
        # ---------------------------------
        critical_kpis = sorted(
            [k for k in state["kpis"] if k["status"] != "green"],
            key=lambda x: x["gap_pct"]
        )[:3]  # top 3 only

        for kpi in critical_kpis:
            print("DEBUG KPI:", kpi)  # 👈 add it here
            # ---------------------------------
            # 🔥 Format retrieved chunks
            # ---------------------------------
            raw_chunks = state.get("retrieved_chunks", {}).get(kpi["raw_kpi"], [])

            if not raw_chunks:
                formatted_chunks = "No best practice found"
            else:
                formatted_chunks = "\n\n".join([
                    f"- {c['text']} (Source: {c['source']} {c['year']})"
                    for c in raw_chunks
                ])

            # ---------------------------------
            # 🔥 ESG CONTEXT (VERY IMPORTANT)
            # ---------------------------------
            direction = kpi.get("direction", "higher_better")

            kpi_context = (
                "Lower values are better (e.g., emissions, water usage)"
                if direction == "lower_better"
                else "Higher values are better (e.g., diversity, recycling)"
            )

            performance_direction = kpi.get("performance", "unknown")

            # ---------------------------------
            # 🔥 BUILD PROMPT
            # ---------------------------------
            try:
                user_prompt = prompt["user_template"].format(
                    company=state["company"],
                    kpi_name=kpi["kpi_name"],
                    company_value=kpi["company_value"],
                    peer_value=kpi["peer_value"],
                    gap_pct=kpi["gap_pct"],
                    performance_direction=performance_direction,
                    kpi_context=kpi_context,
                    retrieved_chunks=formatted_chunks
                )
            except KeyError as e:
                logger.error(f"Prompt formatting failed: missing key {e}")
                continue

            # ---------------------------------
            # 🔁 RETRY LOGIC
            # ---------------------------------
            attempts = self.config["llm"].get("retry_attempts", 3)
            backoff = self.config["llm"].get("retry_backoff_seconds", 2)

            for attempt in range(attempts):
                try:
                    output = await self.llm.generate(
                        prompt["system"],
                        user_prompt
                    )

                    # ---------------------------------
                    # 🔥 SAFETY FILTER (VERY IMPORTANT)
                    # ---------------------------------
                    if (
                        direction == "lower_better"
                        and "increase" in output.lower()
                        and "emission" in output.lower()
                    ):
                        output = "Reduce emissions through efficiency improvements and cleaner energy adoption."

                    recs.append({
                        "kpi_name": kpi["kpi_name"],
                        "content": output
                    })

                    break

                except Exception as e:
                    logger.warning(f"LLM failed attempt {attempt+1}: {e}")

                    if attempt == attempts - 1:
                        recs.append({
                            "kpi_name": kpi["kpi_name"],
                            "content": "Recommendation unavailable due to LLM error"
                        })
                    else:
                        await asyncio.sleep(backoff ** attempt)

        state["recommendations"] = recs
        return state
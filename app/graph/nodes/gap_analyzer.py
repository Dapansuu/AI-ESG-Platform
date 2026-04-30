from .base import BaseNode
from loguru import logger


class GapAnalyzer(BaseNode):

    def __init__(self, config):
        self.config = config

    def run(self, state):

        thresholds = self.config["gap_thresholds"]
        mapping = self.config.get("kpi_mapping", {})
        direction_map = self.config.get("kpi_direction", {})

        kpis = []

        for raw_kpi, peer_val in state["peer_data"].items():

            kpi_name = mapping.get(raw_kpi, raw_kpi)

            if raw_kpi not in state["company_data"]:
                logger.warning(f"KPI missing in company data: {raw_kpi}")
                continue

            company_val = state["company_data"][raw_kpi]

            direction = direction_map.get(raw_kpi, "higher_better")

            # 🔥 SAFE GAP CALCULATION
            if peer_val == 0:
                logger.warning(f"Peer value zero for {raw_kpi}")
                gap_pct = 0
            else:
                if direction == "lower_better":
                    gap_pct = ((peer_val - company_val) / peer_val) * 100
                else:
                    gap_pct = ((company_val - peer_val) / peer_val) * 100

            # 🔥 CORRECT STATUS LOGIC
            if gap_pct < thresholds["red"]:
                status = "red"
            elif gap_pct < thresholds["amber"]:
                status = "amber"
            else:
                status = "green"

            # 🔥 PERFORMANCE LABEL
            if gap_pct > 0:
                performance = "better than peers"
            elif gap_pct < 0:
                performance = "worse than peers"
            else:
                performance = "at par with peers"

            kpis.append({
                "kpi_name": kpi_name,
                "raw_kpi": raw_kpi,
                "direction": direction,
                "company_value": company_val,
                "peer_value": peer_val,
                "gap_pct": round(gap_pct, 2),
                "status": status,
                "performance": performance
            })

        # 🔥 SORT KPIs (worst first)
        kpis = sorted(kpis, key=lambda x: x["gap_pct"])

        state["kpis"] = kpis
        state["all_green"] = all(k["status"] == "green" for k in kpis)

        return state
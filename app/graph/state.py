from typing import TypedDict, List, Dict


class GraphState(TypedDict):
    request_id: str
    company: str

    company_data: dict
    peer_data: dict

    kpis: list
    retrieved_chunks: dict
    recommendations: list

    forecast: List[float]

    all_green: bool
    report_path: str
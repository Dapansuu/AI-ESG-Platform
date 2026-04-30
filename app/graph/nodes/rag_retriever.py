from .base import BaseNode


class RAGRetriever(BaseNode):

    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, state):

        results = {}

        for kpi in state["kpis"]:
            print("RAG INPUT KPI:", kpi) 
            if kpi["status"] == "green":
                continue
            tag = kpi["raw_kpi"]  # use raw for DB filtering
            docs = self.retriever.query(kpi["raw_kpi"], 3)

            if not docs:
                docs = [{"text": "No best practice found"}]

            results[kpi["raw_kpi"]] = docs

        state["retrieved_chunks"] = results
        return state
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
import uuid
import yaml
import os
from app.graph.qa_workflow import build_qa_graph
from app.graph.nodes.qa_agent import QAAgent
from app.api.schemas import QARequest
from app.api.dependencies import verify_api_key
from app.graph.workflow import build_graph
from app.graph.nodes.gap_analyzer import GapAnalyzer
from app.graph.nodes.rag_retriever import RAGRetriever
from app.graph.nodes.strategy_synthesizer import StrategySynthesizer
from app.graph.nodes.report_compiler import ReportCompiler
from app.vectorstore.retriever import ChromaRetriever
from app.llm.openai_client import OpenRouterClient
import json
from fastapi.responses import FileResponse
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")
app = FastAPI()

# load config
with open("app/config.yaml") as f:
    config = yaml.safe_load(f)

# init components
retriever = ChromaRetriever()
llm = OpenRouterClient(config["llm"])

nodes = {
    "gap": GapAnalyzer(config),
    "rag": RAGRetriever(retriever),
    "strategy": StrategySynthesizer(llm, config),
    "report": ReportCompiler(config)
}

graph = build_graph(nodes)

@app.get("/")
async def root():
    return {"message": "ESG GenAI API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze", dependencies=[Depends(verify_api_key)])
async def analyze(payload: dict):

    request_id = str(uuid.uuid4())

    state = {
        "request_id": request_id,
        "company": payload.get("company", "Unknown"),
        "company_data": payload["company_data"],
        "peer_data": payload["peer_data"],
        "forecast": payload["forecast"],
    }

    result = await graph.ainvoke(state)

    return {
        "report_id": request_id,
        "path": result["report_path"]
    }

@app.get("/report/{report_id}")
async def get_report(report_id: str):

    path = f"reports/{report_id}/report.json"

    return FileResponse(path, media_type="application/json")

@app.get("/report/{report_id}/download")
async def download_report(report_id: str):

    path = f"reports/{report_id}/report.pdf"

    return FileResponse(path, media_type="application/pdf")

def load_report_state(report_id: str):
    path = f"reports/{report_id}/report.json"

    if not os.path.exists(path):
        raise FileNotFoundError(f"Report not found: {report_id}")

    with open(path, "r") as f:
        return json.load(f)

@app.post("/ask")
async def ask_question(request: QARequest):

    try:
        state = load_report_state(request.report_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report not found")

    state["question"] = request.question

    result = qa_graph.invoke(state)

    return {
        "answer": result.get("answer", "No response generated")
    }
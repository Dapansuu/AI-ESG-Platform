from pydantic import BaseModel, Field
from typing import List, Optional


class CompanyInput(BaseModel):
    company: str
    scope1_emissions_tCO2e: Optional[float] = Field(gt=0)


class PeerInput(BaseModel):
    peer_avg_scope1_tCO2e: float


class ForecastInput(BaseModel):
    carbon_forecast_5yr: List[float]


class AnalyzeRequest(BaseModel):
    company_data: dict
    peer_data: dict
    forecast: List[float]


class AnalyzeResponse(BaseModel):
    report_id: str
    path: str

class QARequest(BaseModel):
    report_id: str = Field(..., description="Report UUID")
    question: str = Field(..., min_length=3)
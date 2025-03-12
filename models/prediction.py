# models/prediction.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PredictionResult(BaseModel):
    prediction_type: str
    time_series: List[Dict[str, Any]]
    summary: Dict[str, Any]
    chart_data: Optional[Dict[str, Any]] = None
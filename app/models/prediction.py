from pydantic import BaseModel

class PredictionResult(BaseModel):
    category: str
    probability: float
    fccc_code: int
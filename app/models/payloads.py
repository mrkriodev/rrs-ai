from pydantic import BaseModel

class RequestPayload(BaseModel):
    videos: list
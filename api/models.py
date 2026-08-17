from pydantic import BaseModel
from typing import Optional

class QRValidationRequest(BaseModel):
    hash: str
    device_identifier: Optional[str] = None

class ValidationData(BaseModel):
    guest_name: str
    residence_id: int

class QRValidationResponse(BaseModel):
    status: str
    message: str
    data: Optional[ValidationData] = None

class PlateValidationRequest(BaseModel):
    plate: str
    device_identifier: Optional[str] = None

class PlateValidationResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None


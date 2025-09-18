from pydantic import BaseModel
from typing import Optional

class CandidateSearchReq(BaseModel):
    q: Optional[str] = None
    gender: Optional[str] = None
    ageMin: Optional[int] = None
    ageMax: Optional[int] = None
    distanceKm: Optional[int] = None
    myLat: Optional[float] = None
    myLng: Optional[float] = None
    element: Optional[str] = None
    cungPhi: Optional[str] = None
    job: Optional[str] = None
    financeMin: Optional[int] = None
    financeMax: Optional[int] = None
    limit: int = 50
    offset: int = 0

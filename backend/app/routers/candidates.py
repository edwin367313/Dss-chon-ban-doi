from fastapi import APIRouter
from typing import List, Dict, Any
from backend.app.Schemas.candidates import CandidateSearchReq
from backend.app.Services.candidate_services import CandidateService

router = APIRouter(prefix="/api/candidates", tags=["candidates"])
svc = CandidateService()

@router.post("/search")
def search(req: CandidateSearchReq) -> List[Dict[str, Any]]:
    return svc.search(req)

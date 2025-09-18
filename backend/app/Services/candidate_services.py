from typing import List, Dict, Any
from backend.app.db.sessin import get_conn
from backend.app.Schemas.candidates import CandidateSearchReq

class CandidateService:
    def search(self, req: CandidateSearchReq) -> List[Dict[str, Any]]:
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("""
                EXEC dbo.sp_search_candidates
                    @Q=?, @Gender=?, @AgeMin=?, @AgeMax=?,
                    @DistanceKm=?, @MyLat=?, @MyLng=?,
                    @Element=?, @CungPhi=?, @Job=?,
                    @FinanceMin=?, @FinanceMax=?,
                    @Limit=?, @Offset=?;
            """, (
                req.q, req.gender, req.ageMin, req.ageMax,
                req.distanceKm, req.myLat, req.myLng,
                req.element, req.cungPhi, req.job,
                req.financeMin, req.financeMax,
                req.limit, req.offset
            ))
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            return rows
        finally:
            cur.close(); conn.close()

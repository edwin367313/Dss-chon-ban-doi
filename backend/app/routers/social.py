# backend/app/Routers/social.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.app.db.sessin import get_conn

router = APIRouter(prefix="/api", tags=["social"])

# ======== Schemas ========

class SwipeReq(BaseModel):
    meId: str
    targetId: str
    action: str  # "like" | "skip"

class SwipeResp(BaseModel):
    status: str                  # "liked" | "skipped"
    matched: bool = False
    matchId: Optional[str] = None

class SendMessageReq(BaseModel):
    matchId: str
    senderId: str
    content: str

# ======== Helpers ========

def _fetch_all_dict(cur) -> List[Dict[str, Any]]:
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

# ======== Endpoints ========

@router.post("/swipe", response_model=SwipeResp)
def swipe(req: SwipeReq):
    """User meId quẹt với targetId. Nếu cả hai 'like' sẽ tạo match."""
    action = req.action.lower().strip()
    if action not in ("like", "skip"):
        raise HTTPException(status_code=400, detail="action phải là 'like' hoặc 'skip'")

    conn = get_conn(); cur = conn.cursor()
    try:
        # 1) Ghi lịch sử swipe
        cur.execute("""
            INSERT INTO dbo.Swipes(UserID, TargetUserID, Action, CreatedAt)
            VALUES (?, ?, ?, GETDATE());
        """, (req.meId, req.targetId, action))

        matched = False
        match_id = None

        if action == "like":
            # 2) Kiểm tra đối phương đã like mình chưa
            cur.execute("""
                SELECT TOP 1 1
                FROM dbo.Swipes
                WHERE UserID = ? AND TargetUserID = ? AND Action = 'like'
            """, (req.targetId, req.meId))
            reciprocal = cur.fetchone() is not None

            if reciprocal:
                # 3) Đã có match chưa?
                cur.execute("""
                    SELECT TOP 1 ID
                    FROM dbo.Matches
                    WHERE (UserA = ? AND UserB = ?)
                       OR (UserA = ? AND UserB = ?)
                """, (req.meId, req.targetId, req.targetId, req.meId))
                r = cur.fetchone()
                if r:
                    matched = True
                    match_id = str(r[0])
                else:
                    # 4) Tạo match mới
                    cur.execute("""
                        DECLARE @id UNIQUEIDENTIFIER = NEWID();
                        INSERT INTO dbo.Matches(ID, UserA, UserB, CreatedAt)
                        VALUES (@id, ?, ?, GETDATE());
                        SELECT @id;
                    """, (req.meId, req.targetId))
                    match_id = str(cur.fetchone()[0])
                    matched = True

        conn.commit()
        return SwipeResp(status="liked" if action == "like" else "skipped",
                         matched=matched, matchId=match_id)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close(); conn.close()


@router.get("/matches/{meId}")
def get_matches(meId: str) -> List[Dict[str, Any]]:
    """
    Danh sách match của meId, kèm thông tin cơ bản của đối phương và tin nhắn cuối (nếu có).
    Yêu cầu:
      - Bảng Matches(ID, UserA, UserB, CreatedAt)
      - View vw_candidate_base (đã có trong repo) để lấy FullName, AvatarUrl, Age, ElementName, CungPhiName
      - Bảng Messages (tuỳ chọn) để lấy last message
    """
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("""
            ;WITH mymatch AS (
              SELECT
                m.ID           AS MatchID,
                CASE WHEN m.UserA = ? THEN m.UserB ELSE m.UserA END AS OtherUserID,
                m.CreatedAt    AS MatchedAt
              FROM dbo.Matches m
              WHERE m.UserA = ? OR m.UserB = ?
            )
            SELECT
              mm.MatchID,
              mm.OtherUserID AS UserID,
              cb.FullName,
              cb.AvatarUrl,
              cb.Age,
              cb.ElementName,
              cb.CungPhiName,
              mm.MatchedAt,
              lm.Content  AS LastMessage,
              lm.CreatedAt AS LastMessageAt
            FROM mymatch mm
            LEFT JOIN dbo.vw_candidate_base cb
              ON cb.UserId = mm.OtherUserID
            OUTER APPLY (
              SELECT TOP 1 Content, CreatedAt
              FROM dbo.Messages msg
              WHERE msg.MatchID = mm.MatchID
              ORDER BY CreatedAt DESC
            ) lm
            ORDER BY ISNULL(lm.CreatedAt, mm.MatchedAt) DESC
        """, (meId, meId, meId))
        return _fetch_all_dict(cur)
    finally:
        cur.close(); conn.close()


@router.get("/messages/{matchId}")
def get_messages(matchId: str,
                 limit: int = Query(100, ge=1, le=500),
                 offset: int = Query(0, ge=0)) -> List[Dict[str, Any]]:
    """Trả về tin nhắn trong 1 match, cũ → mới, có phân trang."""
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT ID, MatchID, SenderID, Content, CreatedAt
            FROM dbo.Messages
            WHERE MatchID = ?
            ORDER BY CreatedAt ASC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;
        """, (matchId, offset, limit))
        return _fetch_all_dict(cur)
    finally:
        cur.close(); conn.close()


@router.post("/messages")
def send_message(req: SendMessageReq) -> Dict[str, Any]:
    """
    Gửi tin nhắn:
      - Chỉ cho phép sender là thành viên của match.
      - Trả về ID message mới, CreatedAt.
    """
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="content không được rỗng")

    conn = get_conn(); cur = conn.cursor()
    try:
        # 1) Xác thực quyền trong match
        cur.execute("""
            SELECT TOP 1 1
            FROM dbo.Matches
            WHERE ID = ?
              AND (UserA = ? OR UserB = ?)
        """, (req.matchId, req.senderId, req.senderId))
        if cur.fetchone() is None:
            raise HTTPException(status_code=403, detail="Sender không thuộc match này")

        # 2) Ghi message
        cur.execute("""
            DECLARE @id UNIQUEIDENTIFIER = NEWID();
            DECLARE @now DATETIME = GETDATE();
            INSERT INTO dbo.Messages(ID, MatchID, SenderID, Content, CreatedAt)
            VALUES (@id, ?, ?, ?, @now);
            SELECT @id, @now;
        """, (req.matchId, req.senderId, req.content.strip()))
        row = cur.fetchone()
        conn.commit()
        return {"id": str(row[0]), "matchId": req.matchId, "senderId": req.senderId,
                "content": req.content.strip(), "createdAt": row[1]}
    except HTTPException:
        # giữ nguyên status code/chi tiết đã ném ở trên
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close(); conn.close()

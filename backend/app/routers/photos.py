# backend/app/Routers/photos.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
from uuid import uuid4
import re
from backend.app.db.sessin import get_conn

router = APIRouter(prefix="/api/photos", tags=["photos"])

def _safe(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\.\-_]", "-", s)
    return re.sub(r"-{2,}", "-", s).strip("-")

@router.post("/upload")
async def upload_photo(
    userId: str = Form(...),
    isPrimary: int = Form(1),
    sortOrder: int = Form(1),
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(400, "Thiếu file ảnh")
    ext = Path(file.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        raise HTTPException(400, "Chỉ cho phép .jpg/.jpeg/.png/.webp/.gif")

    # Thư mục uploads đã được mount trong main.py
    UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
    user_dir = UPLOAD_DIR / _safe(userId)
    user_dir.mkdir(parents=True, exist_ok=True)

    fname = f"{uuid4().hex}{ext}"
    fpath = user_dir / fname
    with fpath.open("wb") as out:
        out.write(await file.read())

    url = f"/uploads/{_safe(userId)}/{fname}"

    conn = get_conn(); cur = conn.cursor()
    try:
        # Nếu set primary, hạ primary cũ
        if isPrimary:
            try:
                cur.execute("UPDATE dbo.Photos SET IsPrimary = 0 WHERE UserID = ?;", (userId,))
            except Exception:
                pass
        cur.execute("""
            INSERT INTO dbo.Photos(UserID, Url, IsPrimary, SortOrder)
            VALUES (?, ?, ?, ?);
        """, (userId, url, int(bool(isPrimary)), sortOrder))
        conn.commit()
    except Exception as e:
        conn.rollback()
        try: fpath.unlink(missing_ok=True)
        except Exception: pass
        raise HTTPException(400, str(e))
    finally:
        cur.close(); conn.close()

    return {"userId": userId, "url": url, "isPrimary": int(bool(isPrimary)), "sortOrder": sortOrder}

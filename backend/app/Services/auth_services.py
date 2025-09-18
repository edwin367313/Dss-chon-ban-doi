# backend/app/Services/auth_services.py
import uuid
from backend.app.db.sessin import get_conn
from backend.app.Core.security import hash_password
from backend.app.Schemas.auth import SignupReq, SignupResp, LoginReq, LoginResp

def _mk_address(req: SignupReq) -> str:
    parts = [req.district.strip() if req.district else None,
             req.province.strip() if req.province else None,
             "Việt Nam"]
    return ", ".join([p for p in parts if p])

class AuthService:
    def signup(self, req: SignupReq) -> SignupResp:
        user_id = str(uuid.uuid4())
        conn = get_conn(); cur = conn.cursor()
        try:
            # 1) Tạo User
            cur.execute("""
                INSERT INTO dbo.[User](ID, Email, PasswordHash)
                VALUES (?, ?, ?);
            """, (user_id, req.email, hash_password(req.password)))

            # 2) Hồ sơ cơ bản + địa chỉ (lưu vào Nativeland)
            nativeland = _mk_address(req)
            cur.execute("""
                INSERT INTO dbo.Profiles(UserID, FullName, Gender, Birthday, Education, Occupation, Bio, Nativeland)
                VALUES (?, ?, ?, ?, NULL, NULL, NULL, ?);
            """, (user_id, req.fullName, req.gender, req.birthday, nativeland))

            # 3) Free text (tuỳ chọn)
            cur.execute("""
                IF NOT EXISTS (SELECT 1 FROM dbo.ProfileFreeText WHERE UserID=?)
                  INSERT INTO dbo.ProfileFreeText(UserID, HobbiesText, HabitsText, ValuesText)
                  VALUES (?, ?, ?, ?);
                ELSE
                  UPDATE dbo.ProfileFreeText SET HobbiesText=?, HabitsText=?, ValuesText=? WHERE UserID=?;
            """, (user_id, user_id, req.hobbiesText, req.habitsText, req.valuesText,
                  req.hobbiesText, req.habitsText, req.valuesText, user_id))

            conn.commit()
            return SignupResp(userId=user_id)
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close(); conn.close()

    def login(self, req: LoginReq) -> LoginResp:
        conn = get_conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT u.ID, u.Email, p.FullName
                FROM dbo.[User] u
                LEFT JOIN dbo.Profiles p ON p.UserID = u.ID
                WHERE u.Email=? AND u.PasswordHash=?;
            """, (req.email, hash_password(req.password)))
            row = cur.fetchone()
            if not row:
                raise ValueError("Invalid credentials")
            return LoginResp(userId=str(row[0]), email=row[1], fullName=row[2])
        finally:
            cur.close(); conn.close()

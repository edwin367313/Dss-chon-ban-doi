# backend/app/Schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupReq(BaseModel):
    email: EmailStr
    password: str
    fullName: str
    gender: str            # "male" | "female" | ...
    birthday: str          # "YYYY-MM-DD"

    # Địa chỉ Việt Nam
    province: str          # Tỉnh/Thành phố
    district: str          # Quận/Huyện
    # (có thể mở rộng thêm ward sau này)

    # Thông tin khác (tùy chọn)
    hobbiesText: Optional[str] = None
    habitsText: Optional[str] = None
    valuesText: Optional[str] = None

class SignupResp(BaseModel):
    userId: str

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class LoginResp(BaseModel):
    userId: str
    email: EmailStr
    fullName: Optional[str] = None

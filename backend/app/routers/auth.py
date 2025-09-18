from fastapi import APIRouter, HTTPException
from backend.app.Schemas.auth import SignupReq, SignupResp, LoginReq, LoginResp
from backend.app.Services.auth_services import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
svc = AuthService()

@router.post("/signup", response_model=SignupResp)
def signup(req: SignupReq):
    try:
        return svc.signup(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=LoginResp)
def login(req: LoginReq):
    try:
        return svc.login(req)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")

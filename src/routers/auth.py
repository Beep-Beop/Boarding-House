import secrets
import threading
import time
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import requests
from src import crud, schemas, database, security
from src.config import settings
from src.dependencies import limiter, get_current_user, require_role
from src.models import AdminLogs
from src.email_service import send_reset_code, send_verification_email

class _TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self._store: dict = {}
        self._ttl = ttl_seconds
        self._lock = threading.Lock()

    def __setitem__(self, key, value):
        with self._lock:
            self._store[key] = (value, time.monotonic())

    def __contains__(self, key):
        with self._lock:
            if key not in self._store:
                return False
            _, ts = self._store[key]
            if time.monotonic() - ts > self._ttl:
                del self._store[key]
                return False
            return True

    def pop(self, key, default=None):
        with self._lock:
            if key in self._store:
                val, _ = self._store.pop(key)
                return val
            return default

_oauth_states = _TTLCache(ttl_seconds=300)

bearer_scheme = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)

    user = user_crud.get_user_by_email(credentials.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not security.verify_password(credentials.password, user.password):
        if user.auth_provider in ("google", "both"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This account uses Google login. Please sign in with Google.",
                headers={"X-Auth-Hint": "google_login"}
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}"
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in."
        )
    
    user.token_version = (user.token_version or 0) + 1
    db.commit()
    db.refresh(user)

    token_expiry = timedelta(days=7) if credentials.remember_me else None
    access_token = security.create_access_token(
        data={"sub": str(user.user_id), "role": user.role},
        expires_delta=token_expiry,
        token_version=user.token_version
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "role": user.role,
        "name": user.name
    }


@router.post("/send-verification")
@limiter.limit("5/minute")
def send_verification(request: Request, background_tasks: BackgroundTasks, body: schemas.SendVerificationRequest, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)
    user = user_crud.get_user_by_email(body.email)

    if not user:
        return {"message": "If the email exists, a verification email has been sent."}

    if user.email_verified:
        return {"message": "Email is already verified."}

    token = security.create_verification_token()
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user_crud.set_verification_token(user.user_id, token, expires)

    background_tasks.add_task(send_verification_email, body.email, token)

    return {"message": "Verification email sent."}


@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)
    user = user_crud.verify_email_token(token)

    if not user:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            "<html><body style='font-family: Arial; text-align: center; padding: 80px; background: #f6f1e8;'>"
            "<h1 style='color: #D9534F;'>Invalid or Expired Link</h1>"
            "<p>The verification link is invalid or has expired.</p></body></html>",
            status_code=400
        )

    from fastapi.responses import HTMLResponse
    return HTMLResponse(
        "<html><body style='font-family: Arial; text-align: center; padding: 80px; background: #f6f1e8;'>"
        "<div style='max-width: 400px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;'>"
        "<h1 style='color: #28a745;'>&#10003;</h1>"
        "<h2 style='color: #3E362A;'>Email Verified!</h2>"
        "<p style='color: #666;'>Your email has been verified successfully. You can now close this page and log in.</p>"
        "</div></body></html>"
    )


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, background_tasks: BackgroundTasks, body: schemas.ForgotPasswordRequest, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)
    user = user_crud.get_user_by_email(body.email)

    if not user:
        return {"message": "If the email exists, a reset code has been sent."}

    code = f"{secrets.randbelow(1000000):06d}"
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    user_crud.set_reset_code(body.email, code, expires)

    background_tasks.add_task(send_reset_code, body.email, code)

    return {"message": "Reset code sent to your email."}


@router.post("/verify-reset-code")
@limiter.limit("10/minute")
def verify_reset_code(request: Request, body: schemas.VerifyResetCodeRequest, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)
    user = user_crud.verify_reset_code(body.email, body.code)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code."
        )

    return {"message": "Code verified."}


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, body: schemas.ResetPasswordRequest, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)
    user = user_crud.verify_reset_code(body.email, body.code)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code."
        )

    hashed = security.get_password_hash(body.new_password)
    user_crud.update_password(body.email, hashed)

    return {"message": "Password has been reset successfully."}


@router.post("/change-password")
@limiter.limit("5/minute")
def change_password(request: Request, body: schemas.ChangePasswordRequest, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    user_crud = crud.UsersCRUD(db)
    user = user_crud.get(current_user.user_id)
    if not user or not security.verify_password(body.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    hashed = security.get_password_hash(body.new_password)
    user_crud.update_password(user.email, hashed)
    return {"message": "Password changed successfully."}


@router.post("/logout")
@limiter.limit("30/minute")
def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(database.get_db)):
    payload = security.decode_access_token(credentials.credentials)
    if payload and payload.get("jti"):
        from src.models import TokenBlacklist
        expires = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        blacklisted = TokenBlacklist(jti=payload["jti"], expires_at=expires)
        db.add(blacklisted)
        db.commit()
    return {"message": "Logged out successfully."}


@router.post("/create-admin", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_admin(
    request: Request,
    admin_data: schemas.AdminCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(require_role("admin"))
):
    """Admin-only: Creates a new admin account with email_verified and account_setup_complete pre-set."""
    user_crud = crud.UsersCRUD(db)

    existing = user_crud.get_user_by_email(admin_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed = security.get_password_hash(admin_data.password)
    new_admin = user_crud.create(
        name=admin_data.name,
        email=admin_data.email,
        password=hashed,
        role="admin",
        email_verified=True,
        account_setup_complete=True,
        status="active",
    )

    log = AdminLogs(
        admin_id=current_user.user_id,
        action="CREATED_ADMIN",
        target_type="user",
        target_id=new_admin.user_id,
        description=f"Admin {current_user.user_id} created admin account for {admin_data.email}",
    )
    db.add(log)
    db.commit()

    return schemas.UserResponse.model_validate(new_admin)


@router.get("/google/login")
def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google OAuth is not configured")

    redirect_port = request.query_params.get("redirect_port", "9876")
    state = secrets.token_urlsafe(16)
    _oauth_states[state] = redirect_port
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    from urllib.parse import urlencode
    google_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=google_url)


@router.get("/google/callback")
def google_callback(request: Request, code: str = None, state: str = None, error: str = None, db: Session = Depends(database.get_db)):
    if error:
        return {"message": f"Google login failed: {error}"}

    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No authorization code provided")

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google OAuth is not configured")

    if not state or state not in _oauth_states:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or missing OAuth state parameter")
    redirect_port = _oauth_states.pop(state, "9876")

    try:
        token_response = requests.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }, timeout=10)
        token_response.raise_for_status()
        token_data = token_response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token exchange failed: {str(e)}")

    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No ID token received")

    try:
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
            timeout=10
        )
        userinfo_response.raise_for_status()
        google_user = userinfo_response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get user info: {str(e)}")

    google_email = google_user.get("email")
    google_name = google_user.get("name", "Google User")

    if not google_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account has no email")

    user_crud = crud.UsersCRUD(db)
    user = user_crud.get_user_by_email(google_email)
    is_new = False

    if not user:
        is_new = True
        user = user_crud.create(
            name=google_name,
            email=google_email,
            password=security.get_password_hash(secrets.token_urlsafe(32)),
            role="student",
            email_verified=True,
            profile_photo=google_user.get("picture"),
            auth_provider="google",
        )
    elif user.auth_provider == "email":
        user.auth_provider = "both"
        db.commit()
        db.refresh(user)

    if not user.email_verified:
        setattr(user, "email_verified", True)
        db.commit()

    if is_new or not getattr(user, "account_setup_complete", False):
        account_setup_complete = False
    else:
        account_setup_complete = True

    user.token_version = (user.token_version or 0) + 1
    db.commit()
    db.refresh(user)

    access_token = security.create_access_token(
        data={"sub": str(user.user_id), "role": user.role},
        token_version=user.token_version
    )

    from fastapi.responses import HTMLResponse
    import json
    payload = json.dumps({
        "access_token": access_token,
        "user_id": user.user_id,
        "role": user.role,
        "name": user.name,
        "email": user.email,
        "is_new": is_new,
        "account_setup_complete": account_setup_complete,
    })
    callback_url = f"http://127.0.0.1:{redirect_port}/token"
    html = f"""\
<html>
<body style="font-family: Arial; text-align: center; padding: 80px; background: #f6f1e8;">
  <h1 style="color: #28a745;">&#10003; Signed in with Google</h1>
  <p>Welcome, {user.name}.</p>
  <p>You can close this window now.</p>
  <script>
    var data = {payload};
    var params = new URLSearchParams(data);
    fetch("{callback_url}?" + params.toString())
      .then(function(r) {{ window.close() }})
      .catch(function() {{ document.body.innerHTML += '<p>Return to the app to continue.</p>'; }});
  </script>
</body>
</html>"""
    return HTMLResponse(content=html)
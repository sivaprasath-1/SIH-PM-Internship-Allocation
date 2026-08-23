from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.company import Company
from app.auth.auth_service import hash_password, verify_password, create_access_token, get_current_user
from app.schemas.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user (student, company, or admin)."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole(data.role),
    )
    db.add(user)
    db.flush()

    # Create associated profile based on role
    if data.role == "student":
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
    elif data.role == "company":
        company = Company(
            user_id=user.id,
            organization_name=data.name,
        )
        db.add(company)

    db.commit()
    db.refresh(user)

    # Send welcome notification
    create_notification(
        db, user.id,
        title="Welcome to PM Internship Scheme!",
        message=f"Welcome {user.name}! Your account has been created successfully.",
        notif_type="success"
    )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout (client should discard the token)."""
    return {"message": "Logged out successfully"}

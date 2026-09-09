
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.organizations import Organization
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
from app.security.security import (
    hash_password,
    verify_password,
    create_access_token,
)


logger = logging.getLogger("projectscope.audit")


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        logger.warning(
            "registration_failed | reason=email_already_registered"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    organization_name = data.organization_name or "Default Organization"

    organization = (
        db.query(Organization)
        .filter(
            Organization.slug
            == organization_name.lower().replace(" ", "-")
        )
        .first()
    )

    if not organization:
        organization = Organization(
            name=organization_name,
            slug=organization_name.lower().replace(" ", "-"),
        )

        db.add(organization)
        db.flush()

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        organization_id=organization.id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(
        "user_registered | user_id=%s | organization_id=%s",
        user.id,
        user.organization_id,
    )

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "organization_id": str(user.organization_id),
        }
    )

    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user or not verify_password(
        data.password,
        user.hashed_password,
    ):
        logger.warning(
            "login_failed | reason=invalid_credentials"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    logger.info(
        "user_login_success | user_id=%s | organization_id=%s",
        user.id,
        user.organization_id,
    )

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "organization_id": str(user.organization_id),
        }
    )

    return TokenResponse(access_token=token)


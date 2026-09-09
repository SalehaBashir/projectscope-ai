from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.models.user import User
from app.security.security import get_current_user, verify_password

router = APIRouter(prefix="/users", tags=["Users"])


class AccountDeleteRequest(BaseModel):
    password: str


@router.delete("/me")
def delete_my_account(
    request: AccountDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Account was not deleted.",
        )

    try:
        db.delete(current_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Could not delete your account because you still have "
                "projects or data linked to it. Please delete your "
                "projects first, then try again."
            ),
        )

    return {"detail": "Account deleted successfully"}
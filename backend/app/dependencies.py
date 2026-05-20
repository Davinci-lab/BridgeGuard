import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import get_db
from .models.auth_models import Project, User
from .models.payment_models import ApiKey


SECRET_KEY = os.getenv("SECRET_KEY", "bridgeguard-dev-secret-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def get_current_project(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    project_id_query: Annotated[int | None, Query(alias="project_id")] = None,
    project_id_header: Annotated[int | None, Header(alias="X-Project-ID")] = None,
) -> Project:
    if project_id_header is not None and project_id_query is not None:
        if project_id_header != project_id_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID header and query parameter do not match",
            )

    project_id = project_id_header if project_id_header is not None else project_id_query
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID is required",
        )

    project = db.get(Project, project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project


def get_admin_emails() -> set[str]:
    raw_emails = os.getenv("BRIDGEGUARD_ADMIN_EMAILS", "demo@bridgeguard.local")
    return {
        email.strip().lower()
        for email in raw_emails.split(",")
        if email.strip()
    }


def require_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.email.lower() not in get_admin_emails():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def validate_api_key(
    api_key: str | None,
    db: Session,
    project_id: int | None = None,
) -> ApiKey | None:
    if not api_key:
        return None

    key_record = db.query(ApiKey).filter(
        ApiKey.key == api_key,
        ApiKey.is_active.is_(True),
    ).first()
    if key_record is None:
        return None

    if project_id is not None and key_record.project_id != project_id:
        return None

    return key_record

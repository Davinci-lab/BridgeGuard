from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_project, get_current_user
from ..models.auth_models import Project, User
from ..models.decision_models import DecisionRecord as DBDecisionRecord
from ..models.listener_models import Listener
from ..schemas.v2.projects import ProjectCreate, ProjectRead
from ..schemas.v2.simulation import DecisionRecordRead, PaginatedDecisions, TransferSimulation
from ..schemas.v2.listeners import ListenerRead, ListenerStartRequest, ListenerStopRequest
from ..services.listener_service import save_simulation_decision, start_listener, stop_listener


router = APIRouter(tags=["v2"])


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return db.scalars(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .order_by(Project.id)
    ).all()


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    project = Project(name=payload.name.strip(), owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    project = db.get(Project, project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    db.execute(delete(Listener).where(Listener.project_id == project.id))
    db.execute(delete(DBDecisionRecord).where(DBDecisionRecord.project_id == project.id))
    db.delete(project)
    db.commit()
    return {"status": "deleted"}


@router.post("/simulate", response_model=DecisionRecordRead)
def simulate_transfer_v2(
    sim: TransferSimulation,
    project: Annotated[Project, Depends(get_current_project)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        return save_simulation_decision(db, project.id, sim)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/decisions", response_model=PaginatedDecisions)
def list_decisions(
    project: Annotated[Project, Depends(get_current_project)],
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    base_query = select(DBDecisionRecord).where(DBDecisionRecord.project_id == project.id)
    total = db.scalar(
        select(func.count())
        .select_from(DBDecisionRecord)
        .where(DBDecisionRecord.project_id == project.id)
    ) or 0
    items = db.scalars(
        base_query
        .order_by(DBDecisionRecord.timestamp.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return PaginatedDecisions(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "/projects/{project_id}/listeners/start",
    response_model=ListenerRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_project_listener(
    project_id: int,
    payload: ListenerStartRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    project = db.get(Project, project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return start_listener(db, project, payload.connector, payload.mode)


@router.post("/projects/{project_id}/listeners/stop", response_model=list[ListenerRead])
def stop_project_listener(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    payload: ListenerStopRequest = ListenerStopRequest(),
):
    project = db.get(Project, project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    listeners = stop_listener(db, project, payload.connector_id)
    if payload.connector_id and not listeners:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listener not found")
    return listeners

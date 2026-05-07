from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.schemas import ConfigCreate, ConfigUpdate, ConfigResponse
from backend.db.database import get_session
from backend.db.models import Config

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/", response_model=list[ConfigResponse])
def list_configs(session: Session = Depends(get_session)):
    return session.query(Config).all()


@router.get("/{config_id}", response_model=ConfigResponse)
def get_config(config_id: int, session: Session = Depends(get_session)):
    config = session.get(Config, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.post("/", response_model=ConfigResponse, status_code=201)
def create_config(body: ConfigCreate, session: Session = Depends(get_session)):
    config = Config(**body.model_dump())
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


@router.put("/{config_id}", response_model=ConfigResponse)
def update_config(config_id: int, body: ConfigUpdate, session: Session = Depends(get_session)):
    config = session.get(Config, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(config, field, value)
    session.commit()
    session.refresh(config)
    return config


@router.delete("/{config_id}", status_code=204)
def delete_config(config_id: int, session: Session = Depends(get_session)):
    config = session.get(Config, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    session.delete(config)
    session.commit()

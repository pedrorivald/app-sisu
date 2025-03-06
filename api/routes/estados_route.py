import uuid
from fastapi import APIRouter, Query, Depends
from sqlalchemy import func, select
from exceptions.exceptions import NotFoundException
from schemas.estado import EstadoCreate, EstadoOut, EstadoPaginationResponse, EstadoUpdate
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Estado

router = APIRouter(prefix="/estados", tags=["CRUD Estados"])

async def get_estado(db: AsyncSession, estado_id: str):
  result = await db.execute(select(Estado).where(Estado.id == estado_id))
  estado = result.scalars().first()
  if not estado:
    raise NotFoundException("Estado não encontrado")
  return estado

async def get_estados(db: AsyncSession, page: int = 1, size: int = 10):
  offset = (page - 1) * size
  result = await db.execute(select(Estado).limit(size).offset(offset))
  estados = result.scalars().all()

  total_result = await db.execute(select(func.count(Estado.id)))
  total = total_result.scalar()

  return {"page": page, "size": size, "total": total, "data": estados}

async def create_estado(db: AsyncSession, estado_data: EstadoCreate):
  new_estado = Estado(**estado_data.dict())
  new_estado.id = str(uuid.uuid4())
  db.add(new_estado)
  await db.commit()
  return new_estado

async def update_estado(db: AsyncSession, estado_id: str, estado_data: EstadoUpdate):
  estado = await get_estado(db, estado_id)
  for key, value in estado_data.dict(exclude_unset=True).items():
    setattr(estado, key, value)
  await db.commit()
  return estado

async def delete_estado(db: AsyncSession, estado_id: str):
  estado = await get_estado(db, estado_id)
  await db.delete(estado)
  await db.commit()
  return {"message": "Estado deletado com sucesso"}

@router.get("/", response_model=EstadoPaginationResponse)
async def list_estados(page: int = Query(1, ge=1), size: int = Query(10, le=100), db: AsyncSession = Depends(get_session)):
  result = await get_estados(db, page=page, size=size)
  return result

@router.get("/{estado_id}", response_model=EstadoOut)
async def read_estado(estado_id: str, db: AsyncSession = Depends(get_session)):
  estado = await get_estado(db, estado_id)
  return estado

@router.post("/", response_model=EstadoOut)
async def create_estado_view(estado: EstadoCreate, db: AsyncSession = Depends(get_session)):
  new_estado = await create_estado(db, estado)
  return new_estado

@router.put("/{estado_id}", response_model=EstadoOut)
async def update_estado_view(estado_id: str, estado: EstadoUpdate, db: AsyncSession = Depends(get_session)):
  updated_estado = await update_estado(db, estado_id, estado)
  return updated_estado

@router.delete("/{estado_id}")
async def delete_estado_view(estado_id: str, db: AsyncSession = Depends(get_session)):
  response = await delete_estado(db, estado_id)
  return response
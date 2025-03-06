import uuid
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy import func, select
from schemas.chamada import ChamadaCreate, ChamadaOut, ChamadaPaginationResponse, ChamadaUpdate
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Chamada

router = APIRouter(prefix="/chamadas", tags=["CRUD Chamadas"])

async def get_chamada(db: AsyncSession, chamada_id: str):
  result = await db.execute(select(Chamada).where(Chamada.id == chamada_id))
  chamada = result.scalars().first()
  if not chamada:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamada não encontrada")
  return chamada

async def get_chamadas(db: AsyncSession, page: int = 1, size: int = 10):
  offset = (page - 1) * size
  result = await db.execute(select(Chamada).limit(size).offset(offset))
  chamadas = result.scalars().all()

  total_result = await db.execute(select(func.count(Chamada.id)))
  total = total_result.scalar()

  return {"page": page, "size": size, "total": total, "data": chamadas}

async def create_chamada(db: AsyncSession, chamada_data: ChamadaCreate):
  new_chamada = Chamada(**chamada_data.dict())
  new_chamada.id = str(uuid.uuid4())
  db.add(new_chamada)
  await db.commit()
  return new_chamada

async def update_chamada(db: AsyncSession, chamada_id: str, chamada_data: ChamadaUpdate):
  chamada = await get_chamada(db, chamada_id)
  for key, value in chamada_data.dict(exclude_unset=True).items():
    setattr(chamada, key, value)
  await db.commit()
  return chamada

async def delete_chamada(db: AsyncSession, chamada_id: str):
  chamada = await get_chamada(db, chamada_id)
  await db.delete(chamada)
  await db.commit()
  return {"message": "Chamada deletada com sucesso"}

@router.get("/", response_model=ChamadaPaginationResponse)
async def list_chamadas(page: int = Query(1, ge=1), size: int = Query(10, le=100), db: AsyncSession = Depends(get_session)):
  result = await get_chamadas(db, page=page, size=size)
  return result

@router.get("/{chamada_id}", response_model=ChamadaOut)
async def read_chamada(chamada_id: str, db: AsyncSession = Depends(get_session)):
  chamada = await get_chamada(db, chamada_id)
  return chamada

@router.post("/", response_model=ChamadaOut)
async def create_chamada_view(chamada: ChamadaCreate, db: AsyncSession = Depends(get_session)):
  new_chamada = await create_chamada(db, chamada)
  return new_chamada

@router.put("/{chamada_id}", response_model=ChamadaOut)
async def update_chamada_view(chamada_id: str, chamada: ChamadaUpdate, db: AsyncSession = Depends(get_session)):
  updated_chamada = await update_chamada(db, chamada_id, chamada)
  return updated_chamada

@router.delete("/{chamada_id}")
async def delete_chamada_view(chamada_id: str, db: AsyncSession = Depends(get_session)):
  response = await delete_chamada(db, chamada_id)
  return response
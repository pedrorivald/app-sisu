import uuid
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy import func, select
from exceptions.exceptions import NotFoundException
from schemas.idade import IdadeCreate, IdadeOut, IdadePaginationResponse, IdadeUpdate
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Idade

router = APIRouter(prefix="/idades", tags=["CRUD Idades"])

async def get_idade(db: AsyncSession, idade_id: str):
  result = await db.execute(select(Idade).where(Idade.id == idade_id))
  idade = result.scalars().first()
  if not idade:
    raise NotFoundException("Idade não encontrada")
  return idade

async def get_idades(db: AsyncSession, page: int = 1, size: int = 10):
  offset = (page - 1) * size
  result = await db.execute(select(Idade).limit(size).offset(offset))
  idades = result.scalars().all()

  total_result = await db.execute(select(func.count(Idade.id)))
  total = total_result.scalar()

  return {"page": page, "size": size, "total": total, "data": idades}

async def create_idade(db: AsyncSession, idade_data: IdadeCreate):
  new_idade = Idade(**idade_data.dict())
  new_idade.id = str(uuid.uuid4())
  db.add(new_idade)
  await db.commit()
  return new_idade

async def update_idade(db: AsyncSession, idade_id: str, idade_data: IdadeUpdate):
  idade = await get_idade(db, idade_id)
  for key, value in idade_data.dict(exclude_unset=True).items():
    setattr(idade, key, value)
  await db.commit()
  return idade

async def delete_idade(db: AsyncSession, idade_id: str):
  idade = await get_idade(db, idade_id)
  await db.delete(idade)
  await db.commit()
  return {"message": "Idade deletada com sucesso"}

@router.get("/", response_model=IdadePaginationResponse)
async def list_idades(page: int = Query(1, ge=1), size: int = Query(10, le=100), db: AsyncSession = Depends(get_session)):
  result = await get_idades(db, page=page, size=size)
  return result

@router.get("/{idade_id}", response_model=IdadeOut)
async def read_idade(idade_id: str, db: AsyncSession = Depends(get_session)):
  idade = await get_idade(db, idade_id)
  return idade

@router.post("/", response_model=IdadeOut)
async def create_idade_view(idade: IdadeCreate, db: AsyncSession = Depends(get_session)):
  new_idade = await create_idade(db, idade)
  return new_idade

@router.put("/{idade_id}", response_model=IdadeOut)
async def update_idade_view(idade_id: str, idade: IdadeUpdate, db: AsyncSession = Depends(get_session)):
  updated_idade = await update_idade(db, idade_id, idade)
  return updated_idade

@router.delete("/{idade_id}")
async def delete_idade_view(idade_id: str, db: AsyncSession = Depends(get_session)):
  response = await delete_idade(db, idade_id)
  return response
import uuid
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy import func, select
from schemas.populacao_por_idade import PopulacaoPorIdadeCreate, PopulacaoPorIdadeOut, PopulacaoPorIdadePaginationResponse, PopulacaoPorIdadeUpdate
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import PopulacaoPorIdade

router = APIRouter(prefix="/populacao_por_idades", tags=["CRUD PopulacaoPorIdades"])

async def get_populacao_por_idade(db: AsyncSession, populacao_por_idade_id: str):
  result = await db.execute(select(PopulacaoPorIdade).where(PopulacaoPorIdade.id == populacao_por_idade_id))
  populacao_por_idade = result.scalars().first()
  if not populacao_por_idade:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PopulacaoPorIdade não encontrada")
  return populacao_por_idade

async def get_populacao_por_idades(db: AsyncSession, page: int = 1, size: int = 10):
  offset = (page - 1) * size
  result = await db.execute(select(PopulacaoPorIdade).limit(size).offset(offset))
  populacao_por_idades = result.scalars().all()

  total_result = await db.execute(select(func.count(PopulacaoPorIdade.id)))
  total = total_result.scalar()

  return {"page": page, "size": size, "total": total, "data": populacao_por_idades}

async def create_populacao_por_idade(db: AsyncSession, populacao_por_idade_data: PopulacaoPorIdadeCreate):
  new_populacao_por_idade = PopulacaoPorIdade(**populacao_por_idade_data.dict())
  new_populacao_por_idade.id = str(uuid.uuid4())
  db.add(new_populacao_por_idade)
  await db.commit()
  return new_populacao_por_idade

async def update_populacao_por_idade(db: AsyncSession, populacao_por_idade_id: str, populacao_por_idade_data: PopulacaoPorIdadeUpdate):
  populacao_por_idade = await get_populacao_por_idade(db, populacao_por_idade_id)
  for key, value in populacao_por_idade_data.dict(exclude_unset=True).items():
    setattr(populacao_por_idade, key, value)
  await db.commit()
  return populacao_por_idade

async def delete_populacao_por_idade(db: AsyncSession, populacao_por_idade_id: str):
  populacao_por_idade = await get_populacao_por_idade(db, populacao_por_idade_id)
  await db.delete(populacao_por_idade)
  await db.commit()
  return {"message": "PopulacaoPorIdade deletada com sucesso"}

@router.get("/", response_model=PopulacaoPorIdadePaginationResponse)
async def list_populacao_por_idades(page: int = Query(1, ge=1), size: int = Query(10, le=100), db: AsyncSession = Depends(get_session)):
  result = await get_populacao_por_idades(db, page=page, size=size)
  return result

@router.get("/{populacao_por_idade_id}", response_model=PopulacaoPorIdadeOut)
async def read_populacao_por_idade(populacao_por_idade_id: str, db: AsyncSession = Depends(get_session)):
  populacao_por_idade = await get_populacao_por_idade(db, populacao_por_idade_id)
  return populacao_por_idade

@router.post("/", response_model=PopulacaoPorIdadeOut)
async def create_populacao_por_idade_view(populacao_por_idade: PopulacaoPorIdadeCreate, db: AsyncSession = Depends(get_session)):
  new_populacao_por_idade = await create_populacao_por_idade(db, populacao_por_idade)
  return new_populacao_por_idade

@router.put("/{populacao_por_idade_id}", response_model=PopulacaoPorIdadeOut)
async def update_populacao_por_idade_view(populacao_por_idade_id: str, populacao_por_idade: PopulacaoPorIdadeUpdate, db: AsyncSession = Depends(get_session)):
  updated_populacao_por_idade = await update_populacao_por_idade(db, populacao_por_idade_id, populacao_por_idade)
  return updated_populacao_por_idade

@router.delete("/{populacao_por_idade_id}")
async def delete_populacao_por_idade_view(populacao_por_idade_id: str, db: AsyncSession = Depends(get_session)):
  response = await delete_populacao_por_idade(db, populacao_por_idade_id)
  return response
import uuid
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy import func, select, text
from schemas.instituicao import InstituicaoCreate, InstituicaoOut, InstituicaoPaginationResponse, InstituicaoUpdate
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Instituicao

router = APIRouter(prefix="/instituicoes", tags=["CRUD Instituicoes"])

async def get_instituicao(db: AsyncSession, instituicao_id: str):
  result = await db.execute(select(Instituicao).where(Instituicao.id == instituicao_id))
  instituicao = result.scalars().first()
  if not instituicao:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituicao não encontrada")
  return instituicao

async def get_instituicoes(db: AsyncSession, page: int = 1, size: int = 10):
  offset = (page - 1) * size
  result = await db.execute(select(Instituicao).limit(size).offset(offset))
  instituicoes = result.scalars().all()

  total_result = await db.execute(select(func.count(Instituicao.id)))
  total = total_result.scalar()

  return {"page": page, "size": size, "total": total, "data": instituicoes}

async def create_instituicao(db: AsyncSession, instituicao_data: InstituicaoCreate):
  new_instituicao = Instituicao(**instituicao_data.dict())
  new_instituicao.id = str(uuid.uuid4())
  db.add(new_instituicao)
  await db.commit()
  return new_instituicao

async def update_instituicao(db: AsyncSession, instituicao_id: str, instituicao_data: InstituicaoUpdate):
  instituicao = await get_instituicao(db, instituicao_id)
  for key, value in instituicao_data.dict(exclude_unset=True).items():
    setattr(instituicao, key, value)
  await db.commit()
  return instituicao

async def delete_instituicao(db: AsyncSession, instituicao_id: str):
  instituicao = await get_instituicao(db, instituicao_id)
  await db.delete(instituicao)
  await db.commit()
  return {"message": "Instituicao deletada com sucesso"}

@router.get("/", response_model=InstituicaoPaginationResponse)
async def list_instituicoes(page: int = Query(1, ge=1), size: int = Query(10, le=100), db: AsyncSession = Depends(get_session)):
  result = await get_instituicoes(db, page=page, size=size)
  return result

@router.get("/{instituicao_id}", response_model=InstituicaoOut)
async def read_instituicao(instituicao_id: str, db: AsyncSession = Depends(get_session)):
  instituicao = await get_instituicao(db, instituicao_id)
  return instituicao

@router.post("/", response_model=InstituicaoOut)
async def create_instituicao_view(instituicao: InstituicaoCreate, db: AsyncSession = Depends(get_session)):
  new_instituicao = await create_instituicao(db, instituicao)
  return new_instituicao

@router.put("/{instituicao_id}", response_model=InstituicaoOut)
async def update_instituicao_view(instituicao_id: str, instituicao: InstituicaoUpdate, db: AsyncSession = Depends(get_session)):
  updated_instituicao = await update_instituicao(db, instituicao_id, instituicao)
  return updated_instituicao

@router.delete("/{instituicao_id}")
async def delete_instituicao_view(instituicao_id: str, db: AsyncSession = Depends(get_session)):
  response = await delete_instituicao(db, instituicao_id)
  return response
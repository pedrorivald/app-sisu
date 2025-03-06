import uuid
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy import func, select
from schemas.curso_instituicao import CursoInstituicaoCreate, CursoInstituicaoOut, CursoInstituicaoPaginationResponse, CursoInstituicaoUpdate
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import CursoInstituicao

router = APIRouter(prefix="/curso-instituicoes", tags=["CRUD Curso Instituicoes"])

async def get_curso_instituicao(db: AsyncSession, curso_instituicao_id: str):
  result = await db.execute(select(CursoInstituicao).where(CursoInstituicao.id == curso_instituicao_id))
  curso_instituicao = result.scalars().first()
  if not curso_instituicao:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CursoInstituicao não encontrada")
  return curso_instituicao

async def get_curso_instituicoes(db: AsyncSession, page: int = 1, size: int = 10):
  offset = (page - 1) * size
  result = await db.execute(select(CursoInstituicao).limit(size).offset(offset))
  curso_instituicoes = result.scalars().all()

  total_result = await db.execute(select(func.count(CursoInstituicao.id)))
  total = total_result.scalar()

  return {"page": page, "size": size, "total": total, "data": curso_instituicoes}

async def create_curso_instituicao(db: AsyncSession, curso_instituicao_data: CursoInstituicaoCreate):
  new_curso_instituicao = CursoInstituicao(**curso_instituicao_data.dict())
  new_curso_instituicao.id = str(uuid.uuid4())
  db.add(new_curso_instituicao)
  await db.commit()
  return new_curso_instituicao

async def update_curso_instituicao(db: AsyncSession, curso_instituicao_id: str, curso_instituicao_data: CursoInstituicaoUpdate):
  curso_instituicao = await get_curso_instituicao(db, curso_instituicao_id)
  for key, value in curso_instituicao_data.dict(exclude_unset=True).items():
    setattr(curso_instituicao, key, value)
  await db.commit()
  return curso_instituicao

async def delete_curso_instituicao(db: AsyncSession, curso_instituicao_id: str):
  curso_instituicao = await get_curso_instituicao(db, curso_instituicao_id)
  await db.delete(curso_instituicao)
  await db.commit()
  return {"message": "CursoInstituicao deletada com sucesso"}

@router.get("/", response_model=CursoInstituicaoPaginationResponse)
async def list_curso_instituicoes(page: int = Query(1, ge=1), size: int = Query(10, le=100), db: AsyncSession = Depends(get_session)):
  result = await get_curso_instituicoes(db, page=page, size=size)
  return result

@router.get("/{curso_instituicao_id}", response_model=CursoInstituicaoOut)
async def read_curso_instituicao(curso_instituicao_id: str, db: AsyncSession = Depends(get_session)):
  curso_instituicao = await get_curso_instituicao(db, curso_instituicao_id)
  return curso_instituicao

@router.post("/", response_model=CursoInstituicaoOut)
async def create_curso_instituicao_view(curso_instituicao: CursoInstituicaoCreate, db: AsyncSession = Depends(get_session)):
  new_curso_instituicao = await create_curso_instituicao(db, curso_instituicao)
  return new_curso_instituicao

@router.put("/{curso_instituicao_id}", response_model=CursoInstituicaoOut)
async def update_curso_instituicao_view(curso_instituicao_id: str, curso_instituicao: CursoInstituicaoUpdate, db: AsyncSession = Depends(get_session)):
  updated_curso_instituicao = await update_curso_instituicao(db, curso_instituicao_id, curso_instituicao)
  return updated_curso_instituicao

@router.delete("/{curso_instituicao_id}")
async def delete_curso_instituicao_view(curso_instituicao_id: str, db: AsyncSession = Depends(get_session)):
  response = await delete_curso_instituicao(db, curso_instituicao_id)
  return response
from typing import List
from pydantic import BaseModel

class IdadeBase(BaseModel):
  idade: int

class IdadeCreate(IdadeBase):
  pass

class IdadeUpdate(IdadeBase):
  pass

class IdadeOut(IdadeBase):
  id: str

  class Config:
    from_attributes = True

class IdadePaginationResponse(BaseModel):
  page: int
  size: int
  total: int
  data: List[IdadeOut]
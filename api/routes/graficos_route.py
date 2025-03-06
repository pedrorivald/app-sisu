import os
import uuid
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Chamada, Estado, Instituicao

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import matplotlib.colors as mcolors

router = APIRouter(prefix="/graficos", tags=["Gráficos"])
  
@router.get("/mapa/nota-media")
async def get_nota_media_por_estado(
  session: AsyncSession = Depends(get_session)):
  try:
    query = (
      select(
        Estado.codigo,
        Estado.uf,
        Estado.nome,
        func.coalesce(func.avg(Chamada.nu_nota_candidato), 0).label("nota_media_estado")
      )
      .join(Instituicao, Instituicao.id_estado == Estado.id)
      .join(Chamada, Chamada.id_ies == Instituicao.id)
      .group_by(Estado.id)
      .order_by(func.avg(Chamada.nu_nota_candidato).desc())
    )
    
    result = await session.execute(query)
    estados = result.all()
    
    data = [
      {
        "codigo_estado": estado.codigo,
        "uf_estado": estado.uf,
        "nome_estado": estado.nome,
        "nota_media_estado": round(estado.nota_media_estado, 2),
      }
      for estado in estados
    ]
    
    df = pd.DataFrame(data)
    
    # Baixa o shapefile dos estados do Brasil (GeoJSON)
    shapefile_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    brasil = gpd.read_file(shapefile_url)

    # Converter a coluna "id" para string antes de aplicar .str.upper()
    brasil["uf"] = brasil["sigla"].astype(str).str.upper()
    
    # Junta o shapefile com os dados da API
    brasil = brasil.merge(df, left_on="uf", right_on="uf_estado", how="left")
    
    # Verifica se os dados foram corretamente unidos
    if brasil["nota_media_estado"].isnull().sum() > 0:
        brasil["nota_media_estado"] = brasil["nota_media_estado"].fillna(0)  # Preenche valores ausentes

    # Converte para uma projeção geográfica comum (WGS84)
    brasil = brasil.to_crs(epsg=4326)
    
    norm = mcolors.Normalize(vmin=500, vmax=brasil["nota_media_estado"].max())

    # Criar o mapa
    fig, ax = plt.subplots(1, 1, figsize=(12, 12), dpi=300)
    brasil.plot(column="nota_media_estado", cmap="coolwarm", linewidth=0.8, edgecolor="black",
                legend=True, norm=norm, legend_kwds={"label": "Nota Média", "orientation": "horizontal"}, ax=ax)
    ax.set_title("Notas Médias por Estado", fontsize=18)
    ax.axis("off")  
    
    # Cria o diretório se não existir
    os.makedirs("graficos", exist_ok=True)
    
    # Gera um nome único para o PDF e imagem
    filenamePDF = f"{uuid.uuid4()}.pdf"
    filenameIMG = f"{uuid.uuid4()}.png"
    
    filepathPDF = os.path.join("graficos", filenamePDF)
    filepathIMG = os.path.join("graficos", filenameIMG)
    
    plt.savefig(filepathIMG, dpi=300)
    plt.close()

    c = canvas.Canvas(filepathPDF)
    c.drawString(100, 800, "")
    c.drawImage(ImageReader(filepathIMG), 50, 300, width=500, height=500)
    c.save()
    
    return FileResponse(filepathPDF, media_type="application/pdf", filename=filenamePDF)
    
  except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ProdutoRequest(BaseModel):
    nomeProduto: str

@app.get("/")
async def home():
    return {"message": "API online"}

@app.post("/buscar-produtos")
async def buscar_produtos(request: ProdutoRequest):
    return {"mensagem": f"Você pesquisou por: {request.nomeProduto}"}

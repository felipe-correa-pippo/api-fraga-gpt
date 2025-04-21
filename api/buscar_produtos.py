
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class ProdutoRequest(BaseModel):
    nomeProduto: str

CLIENT_ID = "catalog-api"
CLIENT_SECRET = "aecda5581b43d08ee7235e2f9795a764"
TOKEN_URL = "https://accounts.fraga.com.br/realms/cat_teste/protocol/openid-connect/token"
GRAPHQL_URL = "https://apiv2.catalogofraga.com.br/graphql"

@app.post("/buscar-produtos")  # <- Muito importante ser POST
async def buscar_produtos(request: ProdutoRequest):
    try:
        auth_response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        auth_response.raise_for_status()
        access_token = auth_response.json()["access_token"]

        graphql_query = {
            "query": f"""
                query {{
                    produtos(filtro: {{ nome: \\"{request.nomeProduto}\\" }}) {{
                        id
                        nome
                        preco
                    }}
                }}
            """
        }
        graphql_response = requests.post(
            GRAPHQL_URL,
            json=graphql_query,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        graphql_response.raise_for_status()
        data = graphql_response.json()

        produtos = data.get("data", {}).get("produtos", [])

        return {"produtos": produtos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


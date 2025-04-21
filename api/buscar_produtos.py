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

@app.get("/")
async def home():
    return {"message": "API online"}

@app.post("/buscar-produtos")
async def buscar_produtos(request: ProdutoRequest):
    try:
        # 1. Obter o token de acesso
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

        # 2. Fazer a consulta GraphQL
        graphql_query = {
            "query": f"""
                query {{
                    catalogSearch(query: "{request.nomeProduto}", take: 50) {{
                        pageInfo {{
                            total
                            skip
                            take
                        }}
                        nodes {{
                            product {{
                                id
                                partNumber
                                brand {{
                                    id
                                    name
                                }}
                                summaryApplication
                                applicationDescription
                            }}
                        }}
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

        # 3. Extrair e formatar os produtos
        produtos_brutos = data.get("data", {}).get("catalogSearch", {}).get("nodes", [])

        produtos_formatados = []
        for item in produtos_brutos:
            produto = item.get("product", {})
            if produto:
                produtos_formatados.append({
                    "id": produto.get("id", ""),
                    "partNumber": produto.get("partNumber", ""),
                    "brandName": produto.get("brand", {}).get("name", ""),
                    "summaryApplication": produto.get("summaryApplication", ""),
                    "applicationDescription": produto.get("applicationDescription", "")
                })

        return {"produtos": produtos_formatados}

    except Exception as e:
        print(f"🚨 Erro interno: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

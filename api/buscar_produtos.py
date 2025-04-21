
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

        # 3. Formatar a resposta conforme esperado pelo GPT Actions
        produtos_brutos = data.get("data", {}).get("catalogSearch", {}).get("nodes", [])

        produtos_formatados = []
        for item in produtos_brutos:
            produto = item.get("product", {})
            if produto:
                produtos_formatados.append({
                    "product": {
                        "id": produto.get("id", ""),
                        "partNumber": produto.get("partNumber", ""),
                        "brand": {
                            "id": produto.get("brand", {}).get("id", ""),
                            "name": produto.get("brand", {}).get("name", "")
                        }
                    }
                })

        return {"produtos": produtos_formatados}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

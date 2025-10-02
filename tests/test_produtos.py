def test_criar_produto(client):
    resp = client.post("/api/v1/produtos/", json={
        "nome": "Caneta",
        "estoque_minimo": 5,
        "ativo": True
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome"] == "Caneta"
    assert data["estoque_minimo"] == 5
    assert data["ativo"] is True

def test_listar_produtos(client):
    resp = client.get("/api/v1/produtos/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
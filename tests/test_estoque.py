from app.core.config import settings

def test_movimentacoes_e_saldo(client):
    # cria produto
    p = client.post("/api/v1/produtos/", json={
        "nome": "Parafuso",
        "estoque_minimo": 10,
        "ativo": True
    }).json()

    pid = p["id"]

    # entrada de 20
    resp = client.post("/api/v1/estoque/movimentos", json={
        "produto_id": pid,
        "tipo": "ENTRADA",
        "quantidade": 20
    })
    assert resp.status_code == 201

    # verificar saldo
    saldo = client.get(f"/api/v1/estoque/saldo/{pid}").json()
    assert saldo["saldo"] == 20

    # saída de 5
    resp = client.post("/api/v1/estoque/movimentos", json={
        "produto_id": pid,
        "tipo": "SAIDA",
        "quantidade": 5
    })
    assert resp.status_code == 201

    saldo = client.get(f"/api/v1/estoque/saldo/{pid}").json()
    assert saldo["saldo"] == 15

def test_saldo_insuficiente(client):
    # cria produto
    p = client.post("/api/v1/produtos/", json={
        "nome": "Notebook",
        "estoque_minimo": 2,
        "ativo": True
    }).json()
    pid = p["id"]

    # entrada de 1
    client.post("/api/v1/estoque/movimentos", json={
        "produto_id": pid,
        "tipo": "ENTRADA",
        "quantidade": 1
    })

    # saída de 3 → deve falhar (saldo insuficiente)
    resp = client.post("/api/v1/estoque/movimentos", json={
        "produto_id": pid,
        "tipo": "SAIDA",
        "quantidade": 3
    })
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Saldo insuficiente para saída"

def test_produtos_abaixo_minimo(client):
    # cria produto
    p = client.post("/api/v1/produtos/", json={
        "nome": "Caderno",
        "estoque_minimo": 5,
        "ativo": True
    }).json()
    pid = p["id"]

    # entrada de 2 (saldo abaixo do mínimo)
    client.post("/api/v1/estoque/movimentos", json={
        "produto_id": pid,
        "tipo": "ENTRADA",
        "quantidade": 2
    })

    resp = client.get("/api/v1/produtos/abaixo-minimo")
    assert resp.status_code == 200
    data = resp.json()
    assert any(item["produto_id"] == pid for item in data)
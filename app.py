from flask import Flask, request, jsonify
import os
import requests

# 🔥 IMPORTANTE: app primeiro!
app = Flask(__name__)

# 🔐 CONFIG
ASAAS_TOKEN = os.getenv("ASAAS_TOKEN")
ASAAS_URL = "https://api.asaas.com/v3"


# 🟢 TESTE API
@app.route("/")
def home():
    return {"status": "API rodando 🚀"}


# 🔎 BUSCAR CLIENTE POR CPF
@app.route("/buscar-cliente", methods=["GET"])
def buscar_cliente():
    try:
        cpf = request.args.get("cpf")

        if not cpf:
            return jsonify({"erro": "cpf obrigatório"}), 400

        headers = {
            "access_token": ASAAS_TOKEN
        }

        params = {
            "cpfCnpj": cpf
        }

        response = requests.get(
            f"{ASAAS_URL}/customers",
            headers=headers,
            params=params
        )

        data = response.json()

        if data.get("data"):
            cliente = data["data"][0]

            return jsonify({
                "id": cliente.get("id"),
                "nome": cliente.get("name")
            })

        return jsonify({"erro": "cliente não encontrado"}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# 💰 BUSCAR COBRANÇAS
@app.route("/buscar-cobrancas", methods=["GET"])
def buscar_cobrancas():
    try:
        customer_id = request.args.get("customer")

        if not customer_id:
            return jsonify({"erro": "customer obrigatório"}), 400

        headers = {
            "access_token": ASAAS_TOKEN
        }

        params = {
            "customer": customer_id
            # pode adicionar:
            # "status": "OVERDUE"
        }

        response = requests.get(
            f"{ASAAS_URL}/payments",
            headers=headers,
            params=params
        )

        data = response.json()

        cobrancas = []

        for c in data.get("data", []):
            cobrancas.append({
                "id": c.get("id"),
                "valor": c.get("value"),
                "vencimento": c.get("dueDate"),
                "link_pagamento": c.get("invoiceUrl")
            })

        return jsonify({
            "total": len(cobrancas),
            "cobrancas": cobrancas
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# 🤖 GERAR MENSAGEM AUTOMÁTICA
@app.route("/gerar-mensagem", methods=["GET"])
def gerar_mensagem():
    try:
        cpf = request.args.get("cpf")

        if not cpf:
            return {"erro": "cpf obrigatório"}, 400

        headers = {
            "access_token": ASAAS_TOKEN
        }

        # 🔎 cliente
        cliente_resp = requests.get(
            f"{ASAAS_URL}/customers",
            headers=headers,
            params={"cpfCnpj": cpf}
        ).json()

        if not cliente_resp.get("data"):
            return {"mensagem": "Cliente não encontrado 😕"}

        cliente = cliente_resp["data"][0]
        customer_id = cliente.get("id")
        nome = cliente.get("name")

        # 💰 cobranças
        cobrancas_resp = requests.get(
            f"{ASAAS_URL}/payments",
            headers=headers,
            params={"customer": customer_id}
        ).json()

        if not cobrancas_resp.get("data"):
            return {
                "mensagem": f"Lara - Aptrack 🤖💚\n\nOlá {nome}, não encontramos débitos em aberto ✅"
            }

        c = cobrancas_resp["data"][0]

        valor = c.get("value")
        vencimento = c.get("dueDate")
        link = c.get("invoiceUrl")

        mensagem = f"""Lara - Aptrack 🤖💚

Olá {nome} 😊

Identificamos uma cobrança em aberto:

💰 Valor: R${valor}
📅 Vencimento: {vencimento}

👉 Pague agora:
{link}

Se precisar de ajuda, é só me chamar 💬"""

        return {"mensagem": mensagem}

    except Exception as e:
        return {"erro": str(e)}, 500


# 🔔 WEBHOOK ASAAS
@app.route("/webhook/asaas", methods=["POST"])
def webhook_asaas():
    try:
        token_recebido = request.headers.get("asaas-access-token")

        if ASAAS_TOKEN and token_recebido != ASAAS_TOKEN:
            return jsonify({"erro": "não autorizado"}), 403

        data = request.json

        print("Evento recebido:", data)

        return jsonify({"ok": True}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# 🚀 START LOCAL
if __name__ == "__main__":
    app.run()

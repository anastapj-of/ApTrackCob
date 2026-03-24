from flask import Flask, request, jsonify
import os
import requests

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


# 💰 BUSCAR COBRANÇAS EM ATRASO
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
            "customer": customer_id,
            "status": "OVERDUE"
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


# 🔔 WEBHOOK ASAAS (opcional)
@app.route("/webhook/asaas", methods=["POST"])
def webhook_asaas():
    try:
        token_recebido = request.headers.get("asaas-access-token")

        # 🔐 validação
        if ASAAS_TOKEN and token_recebido != ASAAS_TOKEN:
            return jsonify({"erro": "não autorizado"}), 403

        data = request.json

        evento = data.get("event")
        pagamento = data.get("payment", {})

        print("Evento:", evento)
        print("Pagamento:", pagamento)

        return jsonify({"ok": True}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# 🚀 START LOCAL
if __name__ == "__main__":
    app.run()

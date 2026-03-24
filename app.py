from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

ASAAS_TOKEN = os.getenv("ASAAS_TOKEN")
ASAAS_URL = "https://api.asaas.com/v3"


# 🔎 Buscar cobranças em atraso
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
            "status": "OVERDUE"  # pode usar PENDING também
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

from flask import Flask, request, jsonify, Response
import os
import requests
import json

app = Flask(__name__)

# 🔥 UTF-8 (acentos corretos)
app.config['JSON_AS_ASCII'] = False

# 🔐 CONFIG
ASAAS_TOKEN = os.getenv("ASAAS_TOKEN")
ASAAS_URL = "https://api.asaas.com/v3"


# 🟢 TESTE API
@app.route("/")
def home():
    return jsonify({"status": "API rodando"})


# 🔎 BUSCAR CLIENTE POR CPF
@app.route("/buscar-cliente", methods=["GET"])
def buscar_cliente():
    try:
        cpf = request.args.get("cpf")

        if not cpf:
            return jsonify({"erro": "cpf obrigatório"}), 400

        headers = {"access_token": ASAAS_TOKEN}

        response = requests.get(
            f"{ASAAS_URL}/customers",
            headers=headers,
            params={"cpfCnpj": cpf}
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

        headers = {"access_token": ASAAS_TOKEN}

        response = requests.get(
            f"{ASAAS_URL}/payments",
            headers=headers,
            params={"customer": customer_id}
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


# 📄 GERAR MENSAGEM FORMATADA (PADRÃO BR)
@app.route("/gerar-mensagem", methods=["GET"])
def gerar_mensagem():
    try:
        cpf = request.args.get("cpf")

        if not cpf:
            return jsonify({"erro": "cpf obrigatório"}), 400

        headers = {"access_token": ASAAS_TOKEN}

        # 🔎 BUSCAR CLIENTE
        cliente_resp = requests.get(
            f"{ASAAS_URL}/customers",
            headers=headers,
            params={"cpfCnpj": cpf}
        ).json()

        if not cliente_resp.get("data"):
            return jsonify({"mensagem": "Cliente não encontrado"})

        cliente = cliente_resp["data"][0]
        customer_id = cliente.get("id")
        nome = cliente.get("name")

        # 💰 BUSCAR COBRANÇAS
        cobrancas_resp = requests.get(
            f"{ASAAS_URL}/payments",
            headers=headers,
            params={"customer": customer_id}
        ).json()

        if not cobrancas_resp.get("data"):
            mensagem = f"Olá {nome}, não há débitos em aberto."
        else:
            c = cobrancas_resp["data"][0]

            # 💰 FORMATAR VALOR BR
            valor = c.get("value", 0)
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # 📅 FORMATAR DATA BR
            vencimento = c.get("dueDate")
            ano, mes, dia = vencimento.split("-")
            data_formatada = f"{dia}/{mes}/{ano}"

            link = c.get("invoiceUrl")

            mensagem = f"""Olá {nome},

Identificamos uma cobrança em aberto:

Valor: R$ {valor_formatado}
Vencimento: {data_formatada}

Acesse o link para pagamento:
{link}

Caso o pagamento já tenha sido realizado, desconsidere esta mensagem."""

        # 🔥 GARANTE UTF-8
        return Response(
            json.dumps({"mensagem": mensagem}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


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


if __name__ == "__main__":
    app.run()

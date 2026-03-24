from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# 🔐 Token do Asaas (configurar no Render depois)
ASAAS_TOKEN = os.getenv("ASAAS_TOKEN")

# 🔗 Webhook do Umbler Talk (se quiser usar depois)
UMBLER_WEBHOOK = os.getenv("UMBLER_WEBHOOK")


@app.route("/")
def home():
    return {"status": "API rodando 🚀"}


@app.route("/webhook/asaas", methods=["POST"])
def webhook_asaas():
    try:
        # 🔐 Validação de segurança
        token_recebido = request.headers.get("asaas-access-token")
        if ASAAS_TOKEN and token_recebido != ASAAS_TOKEN:
            return jsonify({"erro": "não autorizado"}), 403

        data = request.json

        evento = data.get("event")
        pagamento = data.get("payment", {})

        valor = pagamento.get("value")
        cliente = pagamento.get("customer")

        print("Evento recebido:", evento)
        print("Valor:", valor)
        print("Cliente:", cliente)

        # 🤖 Exemplo de envio para Umbler (opcional)
        if UMBLER_WEBHOOK:
            mensagem = f"💰 Evento: {evento}\nValor: R${valor}"

            requests.post(UMBLER_WEBHOOK, json={
                "text": mensagem,
                "customer": cliente
            })

        return jsonify({"ok": True}), 200

    except Exception as e:
        print("Erro:", str(e))
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run()

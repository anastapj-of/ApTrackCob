@app.route("/gerar-mensagem", methods=["GET"])
def gerar_mensagem():
    try:
        cpf = request.args.get("cpf")

        if not cpf:
            return {"erro": "cpf obrigatório"}, 400

        headers = {
            "access_token": ASAAS_TOKEN
        }

        # 🔎 Busca cliente
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

        # 💰 Busca cobranças
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

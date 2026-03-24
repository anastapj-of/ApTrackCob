@app.route("/gerar-mensagem", methods=["GET"])
def gerar_mensagem():
    try:
        cpf = request.args.get("cpf")

        if not cpf:
            return jsonify({"erro": "cpf obrigatório"}), 400

        headers = {"access_token": ASAAS_TOKEN}

        # 🔎 CLIENTE
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

        # 💰 COBRANÇAS
        cobrancas_resp = requests.get(
            f"{ASAAS_URL}/payments",
            headers=headers,
            params={"customer": customer_id}
        ).json()

        cobrancas = cobrancas_resp.get("data", [])

        if not cobrancas:
            mensagem = f"Olá {nome}, não há débitos em aberto."
        else:
            # 🔥 ORDENA POR DATA (mais próxima primeiro)
            cobrancas_ordenadas = sorted(cobrancas, key=lambda x: x.get("dueDate"))

            mensagem = f"Olá {nome},\n\nIdentificamos {len(cobrancas_ordenadas)} cobrança(s) em aberto:\n"

            for i, c in enumerate(cobrancas_ordenadas, start=1):
                # 💰 VALOR
                valor = c.get("value", 0)
                valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                # 📅 DATA
                vencimento = c.get("dueDate")
                ano, mes, dia = vencimento.split("-")
                data_formatada = f"{dia}/{mes}/{ano}"

                link = c.get("invoiceUrl")

                mensagem += f"""
{i}️⃣ Valor: R$ {valor_formatado}
Vencimento: {data_formatada}
Link: {link}
"""

            mensagem += "\nCaso o pagamento já tenha sido realizado, desconsidere esta mensagem."

        return Response(
            json.dumps({"mensagem": mensagem}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

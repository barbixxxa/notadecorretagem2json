import pdfplumber

with pdfplumber.open("notadecorretagem.pdf", password="XXX") as pdf:
    pagina = pdf.pages[0]
    pagina_texto = pagina.extract_text()

    # print(pagina_texto)

    for linha in pagina_texto.split("\n"):
        if linha.startswith("1-BOVESPA"):
            linha_elementos = (linha.split())

            #print(linha_elementos)

            tipo_transacao = linha_elementos[1]
            nome_ativo = linha_elementos[3]

            for i in range(6, len(linha_elementos)):
                try:
                    int(linha_elementos[i])
                except:
                    continue
                qtd_transacao = linha_elementos[i]
                preco_transacao = linha_elementos[i+1]

            print(
                f"Transação: {tipo_transacao} --- Ativo: {nome_ativo} --- Quantidade: {qtd_transacao} --- Preço: {preco_transacao}")

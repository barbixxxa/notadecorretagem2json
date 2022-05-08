#!/bin/python3
# Adicionar operações BR ao Organizze

import pdfplumber
import requests
import re
import argparse
import organizze

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

parser = argparse.ArgumentParser()
parser.add_argument("arquivo", help="Nome do arquivo PDF a ser convertido")
parser.add_argument("--arqSenha", dest="arqSenha",
                    help="Senha do arquivo PDF a ser convertido")
args = parser.parse_args()


def addTransacao(data_transacao, ativos):

    for ativo in ativos:
        if (ativo["nome"] == 'TAXAS'):
            requisicaoTaxas(data_transacao, ativo["valor"])

        else:
            requisicao(data_transacao, ativo["tipo"], ativo["nome"],
                       ativo["qtd"], ativo["preco"])


def requisicaoTaxas(data_transacao, preco_ativo):

    tag_uuid = organizze.tags['despesa_impostoTaxas']

    data = '{\"transaction\": {\"amount\": '+preco_ativo+', \"activity_type\": 0, \"done\": 1, \"times\": 2, \"date\": \"'+data_transacao+'\", \"finite_periodicity\": \"monthly\", \"infinite_periodicity\": \"monthly\", \"attachments_attributes\": {}, \"account_uuid\": \"'+organizze.account_uuid['corretora_br']+'\", \"description\": \"TAXAS\", \"tag_uuid\": \"' + \
        tag_uuid + '\", \"observation\": \"\", \"joined_tags\": \"\", \"finite\": false, \"infinite\": false}, \"installmentValue\": \"R$ 0, 61\", \"isCreditCardSelected\": false}'

    response = requests.post(
        organizze.url, headers=organizze.headers, data=data, verify=False)
    response_dictionary = response.json()
    print(response_dictionary)


def requisicao(data_transacao, activity_type, nome_ativo, qtd_ativo, preco_ativo,):

    preco_transacao = str(float(qtd_ativo) * float(preco_ativo))

    tag_uuid = organizze.tags['despesa_acoesBR']

    if activity_type == 'V':
        activity_type = organizze.activity_type['receita']
        tag_uuid = organizze.tags['receita_acoesBR']
    else:
        activity_type = organizze.activity_type['despesa']

    data = '{\"transaction\": {\"amount\": '+preco_transacao+', \"activity_type\": '+activity_type+', \"done\": 1, \"times\": 2, \"date\": \"'+data_transacao+'\", \"finite_periodicity\": \"monthly\", \"infinite_periodicity\": \"monthly\", \"attachments_attributes\": {}, \"account_uuid\": \"'+organizze.account_uuid['corretora_br']+'\", \"description\": \"' + \
        nome_ativo+' - '+qtd_ativo + \
        ' ['+preco_ativo+']\", \"tag_uuid\": \"'+tag_uuid + \
        '\", \"observation\": \"\", \"joined_tags\": \"\", \"finite\": false, \"infinite\": false}, \"installmentValue\": \"R$ 0, 61\", \"isCreditCardSelected\": false}'

    response = requests.post(
        organizze.url, headers=organizze.headers, data=data, verify=False)
    response_dictionary = response.json()
    print(response_dictionary)


def main():

    with pdfplumber.open(args.arquivo, password=args.arqSenha) as pdf:

        for pagina in pdf.pages:

            pagina_texto = pagina.extract_text()

            data_transacao = ''
            valor_com_taxas = ''
            valor_sem_taxas = ''
            ativos = []

            for linha in pagina_texto.split("\n"):

                ativo = {}

                if linha.find('/') == 13:
                    match = re.search(r'\d{2}\/\d{2}\/\d{4}', linha)
                    try:
                        datas = match.group().split("/")
                        data_transacao = "-".join(datas[::-1])
                    except:
                        continue

                if linha.startswith("Líquido"):
                    match = re.search(r'\d*\.*\d+\,\d{2}', linha)
                    valor_com_taxas = float(
                        match.group().replace(".", "").replace(",", "."))

                if linha.startswith("Vendas à vista"):
                    match = re.findall(r'\d*\.*\d+\,\d{2}', linha)
                    valor_sem_taxas = float(
                        match[1].replace(".", "").replace(",", "."))

                if linha.startswith("1-BOVESPA"):
                    linha_elementos = (linha.split())

                    # print(linha_elementos)
                    #print(' --- '+str(len(linha_elementos)))

                    tipo_transacao = linha_elementos[1]

                    if (linha_elementos[3] == 'FII'):
                        nome_ativo = linha_elementos[4] + '_' + \
                            linha_elementos[5] + '_' + linha_elementos[6]
                    elif (linha_elementos[3] == 'TREND'):
                        nome_ativo = linha_elementos[4]
                    else:
                        if (len(linha_elementos) > 10):
                            nome_ativo = linha_elementos[3] + \
                                '_' + linha_elementos[4]
                        else:
                            nome_ativo = linha_elementos[3]

                    ativo["tipo"] = tipo_transacao
                    ativo["nome"] = nome_ativo

                    for i in range(5, len(linha_elementos)): # varre da 6 coluna em diante procurando pela quantidade
                        try:
                            int(linha_elementos[i])
                        except:
                            continue

                        qtd_ativo = linha_elementos[i]
                        preco_ativo = linha_elementos[i+1].replace(",", ".")
                        ativo["qtd"] = qtd_ativo
                        ativo["preco"] = preco_ativo

                if (ativo.keys()):
                    ativos.append(ativo)

            taxa = {"nome": "TAXAS", "valor": format(
                abs(valor_com_taxas - valor_sem_taxas), '.2f')}
            ativos.append(taxa)

            addTransacao(data_transacao, ativos)
            print(data_transacao, ativos)


if __name__ == "__main__":
    main()

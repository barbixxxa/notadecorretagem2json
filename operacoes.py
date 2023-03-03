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
parser.add_argument('--test', dest='test', action='store_true',
                    help='Apenas para teste, não realiza requisições')

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

    if(args.test):
        print(data)
    else:
        response = requests.post(
            organizze.url['transacoes'], headers=organizze.headers, data=data, verify=False)
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

    if(args.test):
        print(data)
    else:
        response = requests.post(
            organizze.url['transacoes'], headers=organizze.headers, data=data, verify=False)
        response_dictionary = response.json()
        print(response_dictionary)


def main():

    with pdfplumber.open(args.arquivo, password=args.arqSenha) as pdf:

        for pagina in pdf.pages:

            pagina_texto = pagina.extract_text()

            # print(pagina_texto)

            data_transacao = ''
            taxa_liquidacao = ''
            taxa_emolumentos = ''
            valor_sem_taxas = ''
            ativos = []

            for linha in pagina_texto.split("\n"):

                ativo = {}

                # print(linha)

                # procura pela linha com barra para pegar a data das transacoes
                if linha.find('/') >= 70:
                    # print(linha)
                    match = re.search(r'\d{2}\/\d{2}\/\d{4}', linha)
                    try:
                        datas = match.group().split("/")
                        data_transacao = "-".join(datas[::-1])
                        # print(data_transacao)
                    except:
                        print('Data não encontrada!')
                        continue

                # pegar o valor da taxa de liquidicao
                if linha.startswith("Compras"):
                    # print(linha)
                    match = re.findall(r'\d*\.*\d+\,\d{2}', linha)
                    taxa_liquidacao = float(
                        match[1].replace(".", "").replace(",", "."))
                    # print(taxa_liquidacao)

                # pegar o valor da taxa de emolumento
                if linha.startswith("EEssppeecciiffiiccaaççõõeess"):
                    # print(linha)
                    match = re.search(r'\d*\.*\d+\,\d{2}', linha)
                    taxa_emolumentos = float(
                        match.group().replace(".", "").replace(",", "."))
                    # print(taxa_emolumentos)

                if linha.startswith("BOVESPA"):  # pegar as operacoes
                    linha_elementos = (linha.split())

                    # print(linha_elementos)
                    # print(' --- '+str(len(linha_elementos)))

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

                    # varre da 6 coluna em diante procurando pela quantidade
                    for i in range(5, len(linha_elementos)):
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

            if(taxa_liquidacao):
                taxa = {"nome": "TAXAS", "valor": format(
                    abs(taxa_liquidacao + taxa_emolumentos), '.2f')}
                ativos.append(taxa)

            addTransacao(data_transacao, ativos)
            print(data_transacao, ativos)


if __name__ == "__main__":
    main()

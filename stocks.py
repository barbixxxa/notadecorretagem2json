#!/bin/python3

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


def addTransacao(ativos):
    for ativo in ativos:
        requisicao(ativo["data"], ativo["tipo"], ativo["nome"],
                   ativo["qtd"], ativo["preco"], ativo["corretagem"], ativo["total"], ativo["dolar"])


def requisicao(data_transacao, activity_type, nome_ativo, qtd_ativo, preco_ativo, taxa_corretagem, total_transacao, dolar):

    preco_transacao = str(
        format(abs(((float(total_transacao)+float(taxa_corretagem))*float(dolar))), '.2f'))

    tag_uuid = organizze.tags['despesa_stocks']

    if activity_type == 'V' or activity_type == 'S':
        activity_type = organizze.activity_type['receita']
        tag_uuid = organizze.tags['receita_stocks']
    else:
        activity_type = organizze.activity_type['despesa']

    data = '{\"transaction\": {\"amount\": '+preco_transacao+', \"activity_type\": '+activity_type+', \"done\": 1, \"times\": 2, \"date\": \"'+data_transacao+'\", \"finite_periodicity\": \"monthly\", \"infinite_periodicity\": \"monthly\", \"attachments_attributes\": {}, \"account_uuid\": \"'+organizze.account_uuid+'\", \"description\": \"' + \
        nome_ativo+' - '+qtd_ativo + \
        ' ['+preco_ativo+']'+' {'+dolar+'}'+'\", \"tag_uuid\": \"'+tag_uuid + \
        '\", \"observation\": \"\", \"joined_tags\": \"\", \"finite\": false, \"infinite\": false}, \"installmentValue\": \"R$ 0, 61\", \"isCreditCardSelected\": false}'

    print(data)

    response = requests.post(
        organizze.url, headers=organizze.headers, data=data, verify=False)
    response_dictionary = response.json()
    print(response_dictionary)


def main():

    with pdfplumber.open(args.arquivo, password=args.arqSenha) as pdf:

        for pagina in pdf.pages:

            pagina_texto = pagina.extract_text()

            ativos = []
            dolar = {}

            for linha in pagina_texto.split("\n"):

                ativo = {}

                if linha.find('/') == 6:
                    # pega as linhas que começam com data, trade date e coloca no formato correto
                    match = re.search(r'\d{2}\/\d{2}\/\d{2}', linha)
                    if(match != None):
                        datas = match.group().split("/")
                        if len(datas[2]) < 4:  # verifica se o ano tem 4 digitos
                            datas[2] = '20'+datas[2]
                        data_transacao = datas[2] + \
                            "-" + datas[0] + "-" + datas[1]
                        #print('data da transacao --- ' + data_transacao)

                        # pega o tipo de transacao, no local 2, B/S
                        tipo_transacao = linha[2]
                        #print('tipo de transacao --- ' + tipo_transacao)

                        # pega a quantidade transacionada, preço e valor total
                        match_value = re.findall(r'\d+\.\d+', linha)
                        qtd_ativo = match_value[0]
                        #print('quantidade --- ' + qtd_ativo)
                        preco_ativo = match_value[1]
                        #print('preço do ativo --- ' + preco_ativo)
                        total_transacao = match_value[2]
                        #print('total da transacao --- ' + total_transacao)
                        taxa_corretagem = match_value[3]
                        #print('taxa de corretagem --- ' + taxa_corretagem)

                        # pega o nome do ativo
                        match_nomeAtivo = re.search(r'[aA-zZ]{2,10}', linha)
                        nome_ativo = match_nomeAtivo.group()
                        #print('nome do ativo --- ' + nome_ativo)

                        ativo["data"] = data_transacao
                        ativo["tipo"] = tipo_transacao
                        ativo["qtd"] = qtd_ativo
                        ativo["preco"] = preco_ativo
                        ativo["total"] = total_transacao
                        ativo["corretagem"] = taxa_corretagem
                        ativo["nome"] = nome_ativo

                        if data_transacao not in dolar:  # verifica se a cotacao ja existe
                            dolar[data_transacao] = input(
                                'Valor do dólar no dia ' + data_transacao + ' em R$: ')

                            if (',' in dolar[data_transacao]):  # tratamento da cotacao
                                dolar[data_transacao] = dolar[data_transacao].replace(
                                    ',', '.')

                        ativo["dolar"] = dolar[data_transacao]

                        # print(ativo)

                        if (ativo.keys()):
                            ativos.append(ativo)

            addTransacao(ativos)
            # print(ativos)


if __name__ == "__main__":
    main()

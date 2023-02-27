#!/bin/python3
# Adicionar dividendos BR, U$ ou JCP ao Organizze
# TODO JCP

import requests
import organizze
import csv
import re
import argparse
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

parser = argparse.ArgumentParser()
parser.add_argument("arquivo", help="Nome do arquivo a ser lido")
parser.add_argument('--html', dest='html', action='store_true',
                    help='Indica se o arquivo é HTML')
parser.add_argument('--test', dest='test', action='store_true',
                    help='Apenas para teste, não realiza requisições')
args = parser.parse_args()


def addDividendo(tipo, nome_ativo, unidades, valor, data_transacao):

    preco_unidade = str(round(float(valor)/float(unidades), 2))

    activity_type = organizze.activity_type['receita']
    account_uuid = organizze.account_uuid['corretora_br']

    if tipo == '0':
        tag_uuid = organizze.tags['receita_dividendosBr']
    elif tipo == '1':
        tag_uuid = organizze.tags['receita_jcp']
    elif tipo == '2':
        tag_uuid = organizze.tags['receita_dividendosUs']
        account_uuid = organizze.account_uuid['corretora_us']
    else:
        print('Tipo inválido!')
        return

    data = '{\"transaction\": {\"amount\": '+str(valor)+', \"activity_type\": '+activity_type+', \"done\": 1, \"times\": 2, \"date\": \"'+data_transacao+'\", \"finite_periodicity\": \"monthly\", \"infinite_periodicity\": \"monthly\", \"attachments_attributes\": {}, \"account_uuid\": \"'+account_uuid+'\", \"description\": \"' + \
        nome_ativo+' - '+unidades + \
        ' ['+preco_unidade+']\", \"tag_uuid\": \"'+tag_uuid + \
        '\", \"observation\": \"\", \"joined_tags\": \"\", \"finite\": false, \"infinite\": false}, \"installmentValue\": \"R$ 0, 61\", \"isCreditCardSelected\": false}'

    if(args.test):
        print(data)
    else:
        response = requests.post(
            organizze.url, headers=organizze.headers, data=data, verify=False)
        response_dictionary = response.json()
        print(response_dictionary)


def pegarData(linha, posicao):
    if linha.find('/') == posicao:
        # print(linha)
        match = re.search(r'\d{2}\/\d{2}\/\d{4}', linha)
        try:
            datas = match.group().split("/")
            data_transacao = "-".join(datas[::-1])
            # print(data_transacao)
            return data_transacao
        except:
            print('Data não encontrada!')


def pegarTipoUnidadeseNome(linha):
    retorno = {}
    linha = linha.split(" ")
    linha = list(filter(None, linha))
    retorno["tipo"] = 0
    retorno["unidades"] = linha[2].replace(',', '.')
    retorno["nome_ativo"] = linha[3]
    return retorno


def lerHTML():
    with open(args.arquivo, 'r') as arquivo_HTML:
        html = arquivo_HTML.read()

        soup = BeautifulSoup(html, 'html.parser')

        tables = soup.find_all('table', class_='ui striped very basic table')

        dados = []
        for linha in tables[1].tbody.find_all('tr'):
            coluna = linha.find_all('td')
            if coluna:
                dados.append({
                    'Data': coluna[0].text.strip(),
                    'Ativo': coluna[1].text.strip(),
                    'Rendimento Bruto U$': coluna[2].text.strip(),
                    'Imposto no Exterior': coluna[3].text.strip(),
                    'Rendimento Bruto R$': coluna[4].text.strip(),
                    'Imposto Pago no Exterior': coluna[5].text.strip(),
                })

        for linha in dados:

            datas = linha['Data'].split("/")
            data_transacao = "-".join(datas[::-1])
            tipo = '2'
            unidades = '1'

            impost_pago = linha['Imposto Pago no Exterior'].replace(
                'R$ ', '').replace(',', '.')
            rendimento_bruto = linha['Rendimento Bruto R$'].replace(
                'R$ ', '').replace(',', '.')
            valor = str(float(rendimento_bruto) - float(impost_pago))

            nome_ativo = linha['Ativo'].upper()

            addDividendo(tipo, nome_ativo,
                         unidades, valor, data_transacao)


def menuDividendo():
    data = input('Data (31/12): ')
    data = data + '/2022'
    qtd_operacoes = input(
        'Quantas operações deseja inserir para esta mesma data?: ')
    for i in range(int(qtd_operacoes)):
        tipo = input('Tipo (0 - Dividendos BR; 1 - JCP; 2 - Dividendos US): ')
        nome_ativo = input('Nome do ativo (XXX11): ')
        valor = input('Valor Recebido (11,03): ')
        valor = valor.replace(',', '.')
        if tipo == '2':
            unidades = '1'
            impost_pago = input('Imposto Pago (1,11): ')
            impost_pago = impost_pago.replace(',', '.')
            valor = str(float(valor) - float(impost_pago))
        else:
            unidades = input('Quantidade (10): ')
            unidades = unidades.replace(',', '.')

        if (len(tipo) < 1 or len(nome_ativo) < 1 or len(unidades) < 1 or len(valor) < 1 or len(data) < 1):
            print('\n--- Valor vazio! ---\n')
            return
        else:
            addDividendo(tipo, nome_ativo.upper(), unidades, valor, data)
            print('-----------------------------------')


def main():
    if (args.html):
        lerHTML()
    else:
        menuDividendo()


if __name__ == "__main__":
    main()

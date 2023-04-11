#!/bin/python3
# Adicionar extrato CSV ao Organizze

import requests
import organizze
import csv
import re
import argparse

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

parser = argparse.ArgumentParser()
parser.add_argument("arquivo", help="Nome do arquivo a ser lido")
parser.add_argument('--test', dest='test', action='store_true',
                    help='Apenas para teste, não realiza requisições')
args = parser.parse_args()


def addTransacao(tipo, nome_ativo, unidades, valor, data_transacao):

    preco_unidade = str(round(float(valor)/float(unidades), 2))

    account_uuid = organizze.account_uuid['corretora_br']

    if tipo == '0':
        activity_type = organizze.activity_type['receita']
        tag_uuid = organizze.tags['receita_dividendosBr']
    elif tipo == '1':
        activity_type = organizze.activity_type['receita']
        tag_uuid = organizze.tags['receita_jcp']
    elif tipo == '2':
        activity_type = organizze.activity_type['despesa']
        tag_uuid = organizze.tags['despesa_acoesBR']
    elif tipo == '3':
        activity_type = organizze.activity_type['despesa']
        tag_uuid = organizze.tags['despesa_fii']
    elif tipo == '4':
        activity_type = organizze.activity_type['receita']
        tag_uuid = organizze.tags['receita_fii']
    elif tipo == '5':
        activity_type = organizze.activity_type['despesa']
        tag_uuid = organizze.tags['despesa_tesouroDireto']
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
            organizze.url['transacoes'], headers=organizze.headers, data=data, verify=False)
        response_dictionary = response.json()
        print(response_dictionary)


def addTransferencia(conta_debito, conta_credito, valor, data_transferencia):

    activity_type = organizze.activity_type['receita']
    category = organizze.category_uuid['transferencia']

    data = '{\"transference\":{\"amount\":'+str(valor)+',\"times\":2,\"activityType\":'+activity_type+',\"description\":\"Transferencia\",\"date\":\"'+data_transferencia+'\",\"finite_periodicity\":\"monthly\",\"infinite_periodicity\":\"monthly\",\"category_uuid\":\"' + \
        category+'\",\"attachments_attributes\":{},\"credit_account_uuid\":\"'+conta_credito+'\",\"debit_account_uuid\":\"' + \
        conta_debito+'\",\"joined_tags\":\"\",\"finite\":false,\"infinite\":false},\"installmentValue\":\"R$ 0,00\"}'

    if(args.test):
        print(data)
    else:
        response = requests.post(
            organizze.url['transferencias'], headers=organizze.headers, data=data, verify=False)
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


def pegarUnidadeseNome(linha):
    retorno = {}
    linha = linha.split(" ")
    linha = list(filter(None, linha))
    linha = [x.upper() for x in linha]
    # print(linha)
    index = linha.index('S/')
    retorno["unidades"] = linha[index+1].replace(',', '.')
    retorno["nome_ativo"] = linha[index+2]
    return retorno


def verificaConta(linha):
    if (linha[2] == '260'):
        conta = organizze.account_uuid['nuconta']
    elif (linha[2] == '341'):
        conta = organizze.account_uuid['iti']
    else:
        print('Conta Inválido!')

    return conta


def main():
    with open(args.arquivo, newline='', encoding='latin-1') as arquivo_CSV:
        leitor = csv.reader(arquivo_CSV, delimiter=';')
        for linha in leitor:
            if(len(linha) >= 4):
                # print(linha)
                if linha[2].find('Rendimento') == 0:
                    data = pegarData(linha[0], 2)
                    retorno = pegarUnidadeseNome(linha[2])
                    tipo = '0'
                    unidades = retorno["unidades"]
                    nome_ativo = retorno["nome_ativo"]
                    valor = float(linha[3].replace('.', '').replace(',', '.'))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data)

                elif linha[2].find('Subscricao') == 0:
                    # print(linha)
                    data = pegarData(linha[0], 2)
                    nome_ativo = 'Subscricao '
                    retorno = pegarUnidadeseNome(linha[2])
                    unidades = retorno["unidades"]
                    nome_ativo += retorno["nome_ativo"]
                    if(int(nome_ativo[-2:]) >= 11):
                        tipo = '3'
                    else:
                        tipo = '2'

                    valor = float(linha[3].replace('.', '').replace(',', '.'))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data)

                elif linha[2].find('RETRATACAO') == 0:
                    # print(linha)
                    data = pegarData(linha[0], 2)
                    nome_ativo = 'RETRATACAO '
                    retorno = pegarUnidadeseNome(linha[2])
                    unidades = retorno["unidades"]
                    nome_ativo += retorno["nome_ativo"]
                    tipo = '4'
                    valor = float(linha[3].replace('.', '').replace(',', '.'))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data)

                elif linha[2].find('Juros de capital proprio') == 0:
                    print(linha)
                    data = pegarData(linha[0], 2)

                    retorno = pegarUnidadeseNome(linha[2])
                    print(retorno)
                    tipo = '1'
                    unidades = retorno["unidades"]
                    nome_ativo = retorno["nome_ativo"]
                    valor = float(linha[3].replace('.', '').replace(',', '.'))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data)

                elif linha[2].find('TED') == 0:
                    # print(linha)
                    data = pegarData(linha[0], 2)
                    codigo = linha[5]
                    linha_conta = linha[2].split(' ')
                    valor = abs(
                        float(linha[3].replace('.', '').replace(',', '.')))
                    if (codigo == '26'):  # credito
                        conta_credito = verificaConta(linha_conta)
                        conta_debito = organizze.account_uuid['corretora_br']
                    elif (codigo == '24'):  # retirada
                        conta_debito = verificaConta(linha_conta)
                        conta_credito = organizze.account_uuid['corretora_br']
                    else:
                        print('Código Inválido!')
                    addTransferencia(conta_debito, conta_credito, valor, data)

                elif linha[2].find('Liquidacao Tesouro Direto') == 0:
                    nome_ativo = 'Tesouro Direto'
                    unidades = '1'
                    data = pegarData(linha[0], 2)
                    tipo = '5'
                    valor = abs(
                        float(linha[3].replace('.', '').replace(',', '.')))
                    addTransacao(tipo, nome_ativo,
                                 unidades, valor, data)


if __name__ == "__main__":
    main()

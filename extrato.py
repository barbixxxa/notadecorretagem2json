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
parser.add_argument('--nu', dest='nu', action='store_true',
                    help='Extrato da Nu')
parser.add_argument('--xp', dest='xp', action='store_true',
                    help='Extrato da XP')
parser.add_argument('--test', dest='test', action='store_true',
                    help='Apenas para teste, não realiza requisições')
args = parser.parse_args()


def addTransacao(tipo, nome_ativo, unidades, valor, data_transacao, corretora):

    preco_unidade = str(round(float(valor)/float(unidades), 2))

    if (corretora == 0):
        account_uuid = organizze.account_uuid['corretora_br']
    elif (corretora == 1):
        account_uuid = organizze.account_uuid['xp']
    else:
        print('[ERROR] Transacao sem valor de corretora')

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
    elif tipo == '6':
        activity_type = organizze.activity_type['receita']
        tag_uuid = organizze.tags['receita_tesouroDireto']
    elif tipo == '7':
        activity_type = organizze.activity_type['despesa']
        tag_uuid = organizze.tags['despesa_impostoTaxas']
    elif tipo == '8':
        activity_type = organizze.activity_type['receita']
        tag_uuid = organizze.tags['receita_rendaFixa']
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
        # print(response_dictionary)
        print('Add Status: ' + response.status_code)


def addTransferencia(conta_debito, conta_credito, valor, data_transferencia):

    if (conta_debito != '' and conta_credito != '' and data_transferencia != ''):

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
            print('Add Status: ' + response.status_code)
    else:
        print('[ERROR] Add transferencia')


def pegarData(linha, posicao, formato):
    if linha.find('/') == posicao:
        # print(linha)
        match = re.search(r'\d{1,2}\/\d{1,2}\/\d{4}', linha)
        try:
            datas = match.group().split("/")
            # print(datas)
            if (formato == 0):  # D/M/A
                data_transacao = "-".join(datas[::-1])
            elif (formato == 1):  # M/D/A
                data_transacao = "" + datas[2] + \
                    "-" + datas[0] + "-" + datas[1]
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


def verificaConta(linha, posicao):
    if (linha[posicao] == '260'):
        conta = organizze.account_uuid['nuconta']
    elif (linha[posicao] == '341'):
        conta = organizze.account_uuid['iti']
    else:
        conta = ''
        print('Conta Inválida!')

    return conta


def main():
    if args.nu:
        extrato_nu()
    elif args.xp:
        extrato_xp()
    else:
        print('[ERROR] Falta o parametro da corretora')


def extrato_xp():
    with open(args.arquivo, newline='', encoding='latin-1') as arquivo_CSV:
        leitor = csv.reader(arquivo_CSV, delimiter=',')
        for linha in leitor:
            if(len(linha) >= 4):
                # print(linha)
                if linha[3].upper().find('TAXA SEMESTRAL TESOURO DIRETO - CBLC') == 0:
                    # print(linha)
                    data = pegarData(linha[1], 1, 1)
                    nome_ativo = 'TAXA SEMESTRAL TESOURO DIRETO - CBLC'
                    unidades = '1'
                    tipo = '5'
                    valor = abs(
                        float(linha[5].split(' ')[1].replace('.', '').replace(',', '.')))

                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 1)

                elif linha[3].upper().find('COMPRA TESOURO DIRETO CLIENTES') == 0:
                    # print(linha)
                    data = pegarData(linha[1], 1, 1)
                    nome_ativo = 'TESOURO DIRETO'
                    unidades = '1'
                    tipo = '5'
                    valor = abs(
                        float(linha[5].split(' ')[1].replace('.', '').replace(',', '.')))

                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 1)

                elif linha[3].upper().find('REPASSE DE JUROS TESOURO DIRETO') == 0:
                    # print(linha)
                    data = pegarData(linha[1], 1, 1)
                    nome_ativo = 'REPASSE DE JUROS TESOURO DIRETO'
                    unidades = '1'
                    tipo = '6'
                    valor = abs(
                        float(linha[5].split(' ')[1].replace('.', '').replace(',', '.')))

                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 1)

                elif ((linha[3].upper().find('IRRF') == 0) or (linha[3].upper().find('IR - RESGATE') == 0)):
                    # print(linha)
                    data = pegarData(linha[1], 1, 1)
                    nome_ativo = 'IRRF'
                    unidades = '1'
                    tipo = '7'
                    valor = abs(
                        float(linha[5].split(' ')[1].replace('.', '').replace(',', '.')))

                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 1)
                elif linha[3].upper().find('RESGATE') == 0:
                    # print(linha)
                    data = pegarData(linha[1], 1, 1)
                    nome_ativo = 'RESGATE Renda Fixa'
                    unidades = '1'
                    tipo = '8'
                    valor = abs(
                        float(linha[5].split(' ')[1].replace('.', '').replace(',', '.')))

                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 1)

                elif linha[3].upper().find('TED') == 0:
                    conta_credito = conta_debito = ''
                    # print(linha)
                    data = pegarData(linha[1], 1, 1)
                    lista_linha = linha[3].split(' ')
                    # print(lista_linha)
                    transacao = lista_linha[10].upper()
                    valor = abs(
                        float(linha[5].split(' ')[1].replace('.', '').replace(',', '.')))

                    if (transacao == 'RECEBIMENTO'):  # credito
                        conta_credito = verificaConta(lista_linha, 2)
                        conta_debito = organizze.account_uuid['xp']
                    elif (transacao == 'RETIRADA'):  # retirada
                        conta_debito = verificaConta(lista_linha, 2)
                        conta_credito = organizze.account_uuid['xp']
                    else:
                        print('Transação Inválida!')
                    try:
                        addTransferencia(
                            conta_debito, conta_credito, valor, data)
                    except:
                        print('[ERROR] Transferência')


def extrato_nu():
    with open(args.arquivo, newline='', encoding='latin-1') as arquivo_CSV:
        leitor = csv.reader(arquivo_CSV, delimiter=';')
        for linha in leitor:
            if(len(linha) >= 4):
                # print(linha)
                if linha[2].upper().find('RENDIMENTO') == 0:
                    data = pegarData(linha[0], 2, 0)
                    retorno = pegarUnidadeseNome(linha[2])
                    tipo = '0'
                    unidades = retorno["unidades"]
                    nome_ativo = retorno["nome_ativo"]
                    valor = float(linha[3].replace('.', '').replace(',', '.'))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 0)

                elif linha[2].upper().find('SUBSCRICAO') == 0:
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
                                 unidades, valor, data, 0)

                elif linha[2].upper().find('RETRATACAO') == 0:
                    # print(linha)
                    data = pegarData(linha[0], 2, 0)
                    nome_ativo = 'RETRATACAO '
                    retorno = pegarUnidadeseNome(linha[2])
                    unidades = retorno["unidades"]
                    nome_ativo += retorno["nome_ativo"]
                    tipo = '4'
                    valor = float(linha[3].replace('.', '').replace(',', '.'))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 0)

                elif linha[2].upper().find('JUROS DE CAPITAL PROPRIO') == 0:
                    print(linha)
                    data = pegarData(linha[0], 2, 0)

                    retorno = pegarUnidadeseNome(linha[2])
                    print(retorno)
                    tipo = '1'
                    unidades = retorno["unidades"]
                    nome_ativo = retorno["nome_ativo"]
                    valor = float(linha[3].replace('.', '').replace(',', '.'))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 0)

                elif linha[2].upper().find('TED') == 0:
                    # print(linha)
                    data = pegarData(linha[0], 2, 0)
                    codigo = linha[5]
                    linha_conta = linha[2].split(' ')
                    valor = abs(
                        float(linha[3].replace('.', '').replace(',', '.')))
                    if (codigo == '26'):  # credito
                        conta_credito = verificaConta(linha_conta, 2)
                        conta_debito = organizze.account_uuid['corretora_br']
                    elif (codigo == '24'):  # retirada
                        conta_debito = verificaConta(linha_conta, 2)
                        conta_credito = organizze.account_uuid['corretora_br']
                    else:
                        print('Código Inválido!')
                    addTransferencia(conta_debito, conta_credito, valor, data)

                elif linha[2].upper().find('LIQUIDACAO TESOURO DIRETO') == 0:
                    nome_ativo = 'Tesouro Direto'
                    unidades = '1'
                    data = pegarData(linha[0], 2, 0)
                    tipo = '5'
                    valor = abs(
                        float(linha[3].replace('.', '').replace(',', '.')))
                    addTransacao(tipo, nome_ativo.upper(),
                                 unidades, valor, data, 0)


if __name__ == "__main__":
    main()

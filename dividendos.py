#!/bin/python3

import requests
import organizze

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'


def addDividendo(tipo, nome_ativo, unidades, valor, data_transacao):
    preco_transacao = str(float(unidades) * float(valor))

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
        return

    data = '{\"transaction\": {\"amount\": '+preco_transacao+', \"activity_type\": '+activity_type+', \"done\": 1, \"times\": 2, \"date\": \"'+data_transacao+'\", \"finite_periodicity\": \"monthly\", \"infinite_periodicity\": \"monthly\", \"attachments_attributes\": {}, \"account_uuid\": \"'+account_uuid+'\", \"description\": \"' + \
        nome_ativo+' - '+unidades + \
        ' ['+valor+']\", \"tag_uuid\": \"'+tag_uuid + \
        '\", \"observation\": \"\", \"joined_tags\": \"\", \"finite\": false, \"infinite\": false}, \"installmentValue\": \"R$ 0, 61\", \"isCreditCardSelected\": false}'

    response = requests.post(
        organizze.url, headers=organizze.headers, data=data, verify=False)
    response_dictionary = response.json()
    print(response_dictionary)
    # print(data)


def menuDividendo():
    data = input('Data (31/12): ')
    data = data + '/2022'
    qtd_operacoes = input(
        'Quantas operações deseja inserir para esta mesma data?: ')
    for i in range(int(qtd_operacoes)):
        tipo = input('Tipo (0 - Dividendos BR; 1 - JCP; 2 - Dividendos US): ')
        nome_ativo = input('Nome do ativo (XXX11): ')
        valor = input('Valor por cota (11,03): ')
        valor = valor.replace(',', '.')
        unidades = input('Quantidade (10): ')
        unidades = unidades.replace(',', '.')

        if (len(tipo) < 1 or len(nome_ativo) < 1 or len(unidades) < 1 or len(valor) < 1 or len(data) < 1):
            print('\n--- Valor vazio! ---\n')
            return
        else:
            addDividendo(tipo, nome_ativo.upper(), unidades, valor, data)
            print('-----------------------------------')


def main():
    while True:
        menuDividendo()


if __name__ == "__main__":
    main()

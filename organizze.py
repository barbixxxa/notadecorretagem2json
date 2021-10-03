'''
Execute para não commitar as credenciais: git update-index --assume-unchanged organizze.py
Variáveis contendo as informações para poder autenticar no Organizze

X-Auth-Token: token de acesso após autenticação
account_uuid: uuid da conta
tags: uuid de categorias para inserir a despesa ou receita
url: url para inserir a transação
headers: cabeçalhos da requisição
'''

xAuthToken = 'ey...'

account_uuid = 'UUID'

tags = {'despesa': 'UUID',
        'receita': 'UUID'}

activity_type = {'despesa': '0', 'receita': '1'}

url = 'https://app.organizze.com.br/zze_front/transactions'

headers = {"X-Auth-Token": xAuthToken,
           "Current-Entity-Id": "892338", "Content-Type": "application/json;charset=UTF-8"}

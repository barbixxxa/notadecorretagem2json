# Organizze

[![python](https://img.shields.io/badge/python-3.8-blue)](https://github.com/barbixxxa/organizze)

Inserir dados de nota de corretagem na plataforma [organizze](http://organizze.com.br/)

## Dependências

1. [PDF Plumber](https://pypi.org/project/pdfplumber/) - `pip3 install pdfplumber` or `pip3 install -r requirements.txt`

## Como executar
### Adicionar operações BR ao Organizze

1. Modifique o valor das variáveis presentes no arquivo organizze.py
2. Execute o seguinte comando informando o nome do arquivo pdf e a senha (caso exista)

`./operacoes.py [-h] [--arqSenha ARQSENHA] arquivo`

### Adicionar dividendos ou JCP ao Organizze

1. Modifique o valor das variáveis presentes no arquivo organizze.py
2. Execute o arquivo dividendos.py

`./dividendos.py`

3. Insira as seguintes informações:

```
Tipo (0 - Dividendo; 1 - JCP): 
Nome do ativo (XXX11): 
Quantidade (10): 
Valor por cota (11,03): 
Data (31/12): 
```
### Adicionar operações USA ao Organizze

1. Modifique o valor das variáveis presentes no arquivo organizze.py
2. Execute o seguinte comando informando o nome do arquivo pdf e a senha (caso exista)

`./stocks.py [-h] [--arqSenha ARQSENHA] arquivo`

3. Insira a cotação do dólar em reais para os dias solicitados

### Adicionar operações CRIPTO ao Organizze

1. Modifique o valor das variáveis presentes no arquivo organizze.py
2. Execute o arquivo cripto.py

`./cripto.py`

3. Insira as seguintes informações:

```
Tipo (0 - Compra; 1 - Venda):
Nome do ativo (BTC):
Quantidade (0,1234):
Cotação (235140,96):
Data (31/12):
```

## Melhorias a serem feitas

- [ ] Integrar em um só arquivo operações BR e USA --- `stocks.py` e `operacoes.py`
- [ ] Consumir cotação do dólar via API --- `stocks.py`
- [ ] Permitir dividendos USA --- `dividendos.py` (wtf?)
- [ ] Permitir Conversão de Ativos Cripto --- `cripto.py`
- [ ] Log
- [ ] Subscrição de ativos via extrato csv --- `dividendos.py`
- [ ] JCP --- `dividendos.py`
- [ ] Extrato total via CSV


## Bugs

- [ ] Stocks não reconhece quantidades inteiras. Valores não decimais
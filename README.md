# Organizze
Inserir dados de nota de corretagem na plataforma [organizze](http://organizze.com.br/)

## Dependências

1. [PDF Plumber](https://pypi.org/project/pdfplumber/) - `pip install pdfplumber`

## Como executar
### Adicionar operações ao Organizze

1. Modifique o valor das variáveis presentes no arquivo organizze.py
2. Execute o seguinte comando informando o nome do arquivo pdf e a senha (caso exista)

`operacoes.py [-h] [--arqSenha ARQSENHA] arquivo`

### Adicionar dividendos ou JCP ao Organizze

1. Modifique o valor das variáveis presentes no arquivo organizze.py
2. Execute o arquivo dividendos.py

`dividendos.py`

3. Insira as seguintes informações:

```
Tipo (0 - Dividendo; 1 - JCP): 
Nome do ativo (XXX11): 
Quantidade (10): 
Valor por cota (11,03): 
Data (31/12): 
```

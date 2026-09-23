# Mysql2dbf

Ferramenta para exportar uma tabela MySQL para o formato DBF.

## Visão geral

O Mysql2dbf conecta-se a um banco MySQL, lê a estrutura da tabela, converte os tipos de dados para um formato compatível com DBF e grava os registros em um arquivo `.dbf`.

É útil para integração com sistemas que dependem do formato DBF.

## Funcionalidades

- Conecta-se diretamente ao MySQL.
- Lê os nomes e tipos das colunas da tabela.
- Converte valores para tipos suportados pelo DBF.
- Normaliza nomes de campos para o limite de 10 caracteres do DBF.
- Exporta todos os registros para um arquivo `.dbf`.
- Registra erros e eventos em um arquivo de log.

## Requisitos

- Python 3.10+
- MySQL acessível pela máquina em que o script será executado
- Usuário com permissão de leitura na tabela alvo

## Instalação

Clone o repositório e entre na pasta do projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd mysql2dbf
```

Crie e ative um ambiente virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

## Configuração

Crie um arquivo `config.json` na raiz do projeto com a seguinte estrutura:

```json
{
  "db": {
    "host": "localhost",
    "port": 3306,
    "user": "usuario",
    "password": "senha",
    "database": "nome_do_banco"
  },
  "table_name": "nome_da_tabela",
  "dbf_file": "output.dbf"
}
```

### Campos

- `host`: endereço do servidor MySQL
- `port`: porta do servidor MySQL (`3306` normalmente)
- `user`: usuário de acesso ao banco
- `password`: senha do usuário
- `database`: nome do banco que contém a tabela
- `table_name`: tabela a ser exportada
- `dbf_file`: caminho do arquivo DBF de saída

O caminho `dbf_file` pode ser relativo à pasta do projeto ou absoluto:

```json
"dbf_file": "C:/Exportacoes/dados.dbf"
```

Se o caminho for relativo, ele será resolvido a partir da pasta onde o script está localizado. A pasta de destino precisa existir antes da execução.

## Execução

Na pasta do projeto, execute:

```powershell
python mysql2dbf.py
```

Ou, com o ambiente virtual ativado:

```powershell
python mysql2dbf.py
```

Ao final, o programa exibe:

- o arquivo gerado
- a quantidade de linhas exportadas
- a quantidade de colunas

Em caso de erro, verifique também o arquivo de log gerado pelo programa.

## Build do executável Windows

O projeto inclui um script para gerar um executável com PyInstaller:

```powershell
build_exe.bat
```

Esse processo cria um executável empacotado e pode ser usado em ambiente Windows sem instalar Python manualmente. O arquivo final costuma ser gerado em uma pasta de distribuição do projeto.

## Segurança

Para repositórios públicos:

- não versionar credenciais reais
- manter um `config.json` local apenas no ambiente de execução
- usar um arquivo de exemplo sem senha, como `config.example.json`, quando necessário

## Limitações

- a versão atual suporta MySQL
- o formato DBF limita os nomes dos campos a 10 caracteres
- tipos de dados não reconhecidos podem ser convertidos para texto

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
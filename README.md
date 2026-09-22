# Mysql2dbf

Ferramenta Python para exportar uma tabela MySQL para o formato DBF.

O projeto foi desenvolvido com o auxílio do assistente GPT Luna.

## Recursos

- Consulta a estrutura da tabela diretamente no MySQL.
- Exporta todos os registros para DBF.
- Converte texto, números e datas para tipos compatíveis com DBF.
- Normaliza os nomes dos campos para o limite de 10 caracteres do formato DBF.
- Registra a execução e os erros em `Mysql2dbf.log`.

## Requisitos

- Python 3.10 ou superior.
- MySQL acessível pelo computador.
- Usuário MySQL com permissão de leitura na tabela.

## Instalação

Clone o repositório e entre na pasta do projeto:

```bash
git clone <URL_DO_REPOSITORIO>/mysql2dbf.git
cd mysql2dbf
```

Crie e ative um ambiente virtual no Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

## Configuração

Edite `config.json` com os dados da conexão:

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
  "dbf_file": "saida/output.dbf"
}
```

- `host`: endereço do servidor MySQL.
- `port`: porta do MySQL, normalmente `3306`.
- `user`: usuário usado na conexão.
- `password`: senha do usuário.
- `database`: banco que contém a tabela.
- `table_name`: tabela que será exportada.
- `dbf_file`: caminho do arquivo DBF de saída.

O programa usa somente `database` e `table_name`; não é necessário informar `table_schema`.

`dbf_file` pode ser relativo à pasta do script ou absoluto:

```json
"dbf_file": "C:/Exportacoes/dados.dbf"
```

A pasta de destino deve existir antes da execução. Não publique credenciais reais no repositório.

## Execução

Com o ambiente virtual ativado, execute:

```powershell
python mysql2dbf.py
```

Ao concluir, o programa informa o arquivo criado, a quantidade de linhas e a quantidade de colunas. Em caso de erro, consulte `Mysql2dbf.log`.

## Arquivos versionados

- `mysql2dbf.py`: código principal da aplicação.
- `config.json`: configuração da conexão e da exportação.
- `requirements.txt`: dependências Python.
- `README.md`: documentação do projeto.

## Arquivos ignorados

Arquivos temporários e gerados localmente não fazem parte do repositório, incluindo `.venv/`, `build/`, `dist/`, logs, DBFs, caches Python e arquivos de teste. O executável Windows e os arquivos de build não são distribuídos pelo GitHub nesta configuração.

## Limitações

- A versão atual suporta MySQL.
- O formato DBF limita os nomes dos campos a 10 caracteres.
- Tipos de dados não reconhecidos são convertidos para texto.

## Segurança

Para um repositório público, prefira manter um arquivo `config.example.json` sem senha e adicionar o `config.json` real ao `.gitignore` antes de publicar credenciais.

## Licença

Adicione um arquivo `LICENSE` ao repositório antes de publicar uma licença para o projeto.

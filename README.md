# Mysql2dbf

Ferramenta Python para exportar uma tabela MySQL para o formato DBF.

## Recursos

- Lê a estrutura da tabela diretamente no MySQL.
- Exporta todos os registros para DBF.
- Converte textos, números e datas para tipos compatíveis com DBF.
- Normaliza nomes de campos para o limite de 10 caracteres do formato DBF.
- Registra execução e erros em `Mysql2dbf.log`.

## Requisitos

- Python 3.10 ou superior.
- MySQL acessível no ambiente.
- Usuário MySQL com permissões de leitura na tabela.

## Configuração local

Edite o arquivo `config.json` na raiz do projeto:

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

- `host`: endereço do servidor MySQL.
- `port`: porta do MySQL, normalmente `3306`.
- `user`: usuário usado na conexão.
- `password`: senha do usuário.
- `database`: banco que contém a tabela.
- `table_name`: tabela que será exportada.
- `dbf_file`: arquivo DBF de saída.

A propriedade `dbf_file` aceita caminho relativo à pasta do projeto ou caminho absoluto:

```json
"dbf_file": "C:/Exportacoes/dados.dbf"
```

Se usar um caminho relativo, ele é resolvido a partir da pasta do script, isto é, a raiz do projeto. A pasta de destino precisa existir antes da execução.

## Execução

Entre na pasta do projeto e execute:

```powershell
cd c:\Projects\MS\Tabnet\scripts\mysql2dbf
python mysql2dbf.py
```

Ou, com ambiente virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python mysql2dbf.py
```

Ao concluir, o programa exibe o arquivo criado, a quantidade de linhas e a quantidade de colunas. Em caso de falha, consulte `Mysql2dbf.log`.

## Build do executável

O script `build_exe.bat` gera um executável com PyInstaller e coloca o resultado no diretório `dist`.

```powershell
build_exe.bat
```

Esse comando cria um executável em `dist\Mysql2dbf.exe` e copia `config.json` para a pasta de distribuição. Mantenha o `config.json` ao lado do executável e ajuste os valores conforme o ambiente de destino.

## Pastas importantes

- `build/`: artefatos intermediários gerados pelo PyInstaller.
- `csv/`: arquivos CSV locais e dados auxiliares do projeto.
- `dist/`: executável empacotado e arquivos de distribuição.
- `output.dbf`: DBF padrão gerado em execução local.

## Limitações

- A versão atual suporta MySQL.
- O formato DBF limita os nomes dos campos a 10 caracteres.
- Tipos de dados não reconhecidos são convertidos para texto.

## Segurança

Para repositórios públicos, prefira manter um arquivo de exemplo sem senha, como `config.example.json`, e não versionar o `config.json` real com credenciais.

## Licença

Adicione um arquivo `LICENSE` ao repositório antes de publicar uma licença para o projeto.

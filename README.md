# Mysql2dbf

## Descrição

O `Mysql2dbf.exe` consulta uma tabela MySQL e exporta seus dados para um arquivo no formato DBF.

O programa foi desenvolvido com o auxílio do assistente GPT Luna.

## Pré-requisitos

- Windows.
- MySQL em execução e acessível.
- Usuário MySQL com permissão para consultar a tabela.
- Arquivo `config.json` na mesma pasta do executável.

## Configuração

Edite o `config.json` antes de executar o programa:

```json
{
  "db": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "test"
  },
  "table_name": "pnsn",
  "dbf_file": "output.dbf"
}
```

- `host`: endereço do servidor MySQL.
- `port`: porta do MySQL, normalmente `3306`.
- `user`: usuário do banco.
- `password`: senha do usuário.
- `database`: banco de dados.
- `table_name`: tabela a exportar.
- `dbf_file`: nome do arquivo DBF de saída.

Não compartilhe o arquivo de configuração se ele contiver uma senha real.

## Execução

1. Coloque `Mysql2dbf.exe` e `config.json` na mesma pasta.
2. Confirme que o MySQL está em execução.
3. Ajuste o `config.json`.
4. Execute por duplo clique ou pelo Prompt de Comando:

```bat
Mysql2dbf.exe
```

Ao concluir, o programa informa a quantidade de linhas e colunas exportadas.

## Arquivos gerados

- Arquivo DBF definido em `dbf_file`, normalmente `output.dbf`.
- `convert_schema_mysql_dbf.log`, com o registro da execução e dos erros.

Se o arquivo DBF já existir, poderá ser substituído em uma nova exportação.

## Conversão de dados

Tipos de texto são convertidos para campos de texto DBF; tipos inteiros e decimais, para campos numéricos; e `DATE`, para campo de data. Outros tipos são convertidos para texto. Os nomes dos campos são normalizados para respeitar o limite de 10 caracteres do formato DBF.

## Problemas comuns

- **Configuração não encontrada:** verifique se `config.json` está ao lado do executável.
- **Falha na conexão:** confira host, porta, usuário, senha e banco.
- **Tabela não encontrada:** confirme `database` e `table_name`.
- **Erro na execução:** consulte `convert_schema_mysql_dbf.log`.

## Compilação

Para gerar o executável, execute `build_exe.bat` na raiz do projeto. O executável será criado em `dist` com o nome `Mysql2dbf.exe`.

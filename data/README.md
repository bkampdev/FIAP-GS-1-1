# Base de ocorrências do Jardim Horizonte

`dados.csv` usa UTF-8, vírgula como separador e uma primeira linha com os nomes das colunas na ordem abaixo. Use uma linha por ocorrência. Todos os campos são obrigatórios. Campos de texto com vírgula são delimitados por aspas duplas.

| Campo | Conteúdo |
| --- | --- |
| `codigo` | Identificador único em texto, como `001`, preservando zeros à esquerda. |
| `categoria` | `iluminação`, `acessibilidade`, `limpeza` ou `conservação de espaços coletivos`. |
| `descricao` | Descrição breve da demanda. |
| `bairro` | Bairro da ocorrência. A base simula o Jardim Horizonte. |
| `local` | Referência genérica, como praça, alameda ou parque. |
| `dia_abertura` | Dia simulado de abertura, escrito em algarismos decimais, a partir de 1. |
| `situacao` | `aberta` para demanda registrada e ainda não examinada, `em análise` durante a avaliação ou `concluída` após o encerramento simulado. |

Os registros são fictícios e usam locais genéricos. Os códigos `001` a `012` começam em `aberta`. O código `013` está livre para a demonstração do cadastro. O acompanhamento aplica os eventos simulados à mesma ocorrência que aparece na lista e no índice do cadastro. A lista preserva a ordem de registro, o índice permite buscar diretamente por código e a hierarquia agrupa as ocorrências por bairro e categoria.

A linha 14, de código `099`, tem a categoria vazia para demonstrar a validação. O carregamento devolve essa rejeição com o número da linha e o motivo, preservando as 12 ocorrências válidas. Um cabeçalho fora do esquema impede o carregamento. Cadastros e alterações feitos durante a sessão ficam em memória.

Para integrar uma consulta, `buscar_por_codigo` devolve `None` se o código estiver ausente. `filtrar` devolve uma lista e exige que cada registro satisfaça os dois filtros quando ambos são informados. Valores de filtro inválidos geram `ValueError`.

Execute os testes na raiz do repositório com `PYTHONPATH=src python3 -B -m unittest discover -s tests`.

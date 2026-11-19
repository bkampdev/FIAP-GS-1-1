# Roteiro de demonstração

## Sequência para a gravação

Grave em uma sessão nova na raiz do repositório integrado. Use `python src/sistema.py` e mostre as entradas e as saídas reais do terminal. Os resultados abaixo são as expectativas da base simulada e devem ser conferidos em um ensaio antes de gravar.

| Etapa | Ação no menu | O que mostrar |
| --- | --- | --- |
| Contexto | Apresente o Jardim Horizonte e o público beneficiado. | Explique como o painel reúne e acompanha relatos do bairro. |
| Inicialização | Abra a aplicação e escolha `8` para indicadores e `1` para listar. | Mostre a rejeição da linha com categoria vazia, o total de 12, as situações `5 / 4 / 3`, as 9 pendências e a média de 6 dias. |
| Consulta e validação | Use `4` com `iluminação` e `aberta`, depois `3` com `999`. Em `2`, tente repetir o código `001` com os campos do próximo passo. Veja a fila em `6`. | Mostre o filtro com `003`, a mensagem de código ausente, a rejeição do cadastro duplicado e a fila inicial `003, 006, 009, 011, 012`. |
| Cadastro | Escolha `2`. Use código `013`, categoria `iluminação`, descrição `Poste com lâmpada apagada`, bairro `Jardim Horizonte`, local `Praça das Amoreiras` e dia `17`. | Em `3`, busque `013` para mostrar que começa aberta. Em `6`, confirme que entrou no fim da fila. |
| Regra e atualização | Em `5`, tente mudar `013` diretamente de aberta para concluída no dia `18`. Em seguida, atualize `013` para `em análise` no dia `18`. | Mostre a rejeição do salto e a confirmação da transição permitida. |
| Acompanhamento | Use `6`, `7` e `9`. | Confira que `013` saiu da fila e que o evento `aberta → em análise` de `013`, dia `18`, está no topo do histórico. Na hierarquia, localize `013` em Jardim Horizonte → iluminação. |
| Comparação | Abra `8`. | Confira 13 ocorrências, 5 abertas, 5 em análise, 3 concluídas, 10 pendências e média de 6 dias. |
| Encerramento | Explique os limites, depois selecione `0`. | A base é fictícia, as mudanças duram uma sessão e os indicadores descrevem apenas o cenário do exercício. |

Na narração, relacione o dicionário à busca por código, a fila aos registros ainda abertos, a pilha à consulta de eventos recentes e a matriz ao cruzamento das categorias com as situações. Apresente os rótulos por extenso ao interpretar números como `5 / 4 / 3`.

## Checklist de publicação

- [ ] Ensaiar a sequência completa na versão integrada e conferir as saídas contra o relatório.
- [ ] Conferir se entradas, mensagens e indicadores estão legíveis na gravação.
- [ ] Revisar narração e legendas em português e conferir se a captura usa somente os dados fictícios do projeto.
- [ ] Publicar no YouTube com visibilidade **Não listado**.
- [ ] Abrir o link em uma sessão sem login e conferir a reprodução.
- [ ] Registrar a URL completa do vídeo no README e, como única linha, em `docs/link_video.txt`.
- [ ] Abrir o GitHub sem login e conferir os arquivos de entrega, incluindo `docs/relatorio.pdf` com 4 a 8 páginas.
- [ ] Enviar ao FIAP ON um arquivo `.TXT` contendo exatamente as duas URLs, uma por linha, sem rótulos ou texto adicional.

## Links para o TXT do FIAP ON

1. Repositório público [Neighborhood Action Dashboard](https://github.com/bkampdev/FIAP-GS-1-1).
2. URL completa do vídeo no YouTube, pendente de publicação como **Não listado**. Use a URL confirmada de `docs/link_video.txt` antes de enviar o TXT.

A participação na competição permanece pendente de decisão da equipe.

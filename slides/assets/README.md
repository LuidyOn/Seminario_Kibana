# Capturas da demonstração

O gerador usa as imagens abaixo quando elas existem. Salve apenas a área relevante da janela, com as informações pessoais e as mensagens de eventos ocultas.

| Arquivo | Slide | Enquadramento recomendado |
|---|---:|---|
| `visualizador-eventos.png` | 2 | PNG com cerca de 1.400 × 800 px. Em **Logs do Windows → Aplicativo**, enquadre o cabeçalho e a lista com **Nível**, **Data e Hora**, **Fonte** e **Identificação do Evento**. Oculte o painel de visualização da mensagem. |
| `discover.png` | 5 | PNG com cerca de 1.680 × 750 px. Inclua o Data View **Eventos do Windows**, o filtro KQL, o histograma e a tabela com `@timestamp`, `log.level` e `event.code`. Mantenha as linhas recolhidas. |
| `eventos-do-windows.png` | 9 | PNG com cerca de 1.680 × 900 px. Inclua o título, **Last 7 days** e os quatro painéis originais sem filtro ativo. |

Após substituir uma captura, gere o PPTX de novo a partir da raiz com `py -3 .\slides\gerar_slides.py` em um ambiente com `python-pptx`.

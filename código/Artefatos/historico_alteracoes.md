# Histórico de Alterações (Changelog)

Este documento registra todas as alterações feitas no Extrator de Provas e no Guia de Estudos, bem como decisões de design tomadas ao longo do projeto.

---

## [2026-05-21] Sessão Atual (ID: 527455db-c0aa-4e79-aaf5-55f6cdb25b95)

### Início dos Trabalhos: Integração e Refatoração Completa
* **Objetivo Geral**: Executar o planejamento da última conversa (`f4033a32-68d8-4095-a85f-ece7261b9e76`), dando continuidade ao plano de estudos da primeira conversa (`9b21ec99-b59d-477b-8607-c0601aa45b72`/`042b1f7d-5511-4696-8e90-a741eaf93f34`).
* **Novidade/Alteração Solicitada**: Ajustar o mecanismo de estimativa de tempo do enriquecimento via IA. O tempo total restante passa a ser estimado com base no tempo real decorrido da **primeira requisição à API**, multiplicado pela quantidade de requisições restantes (levando em conta também a pausa obrigatória de 4.5 segundos).
* **Estrutura dos Arquivos**:
  * Importação e criação do Guia de Estudos local (`guia_estudo.md`).
  * Criação do registro de alterações (`historico_alteracoes.md`).

---

## [2026-05-21] Sessão Atual (ID: 56629adb-9887-473c-8214-0163c6f0a2a7)

### Conclusão e Consolidação do Plano de Implementação
* **Migração Definitiva para a Raiz**: Todos os módulos otimizados (`extractor.py`, `models.py`, `processor.py`, `saver.py`, `main.py`, `test_runner.py`) foram consolidados na raiz do workspace, eliminando a redundância da pasta `Teste/`.
* **Limpeza Completa do Workspace (Declutter)**: Exclusão total da pasta `Teste/`, do arquivo temporário `texto para o gemini.txt`, e de diretórios órfãos na raiz.
* **Processamento Otimizado em Lotes de 20**: Conforme sugestão aprovada pelo usuário, o agrupamento foi configurado para lotes de exatamente 20 questões por requisição (`tamanho_lote = 20`), maximizando o aproveitamento do contexto e reduzindo os custos de chamadas de API em 95%.
* **Estimativa de Tempo Dinâmica**: Implementação de cronometragem da primeira requisição à API para projetar de forma realista o tempo restante de processamento dos lotes subsequentes, somado ao pacing sleep obrigatório de 4.5 segundos.
* **Dupla Defesa (Double-Defense) de Tags**:
  - Filtro programático complementar nativo em Python (`TAG_BLACKLIST` com termos como *unicamp*, *física*, *matemática*, etc.) para barrar tags genéricas.
  - Alinhamento rigoroso nas diretivas do prompt do Gemini para retornar exclusivamente tópicos teóricos (ex: *Termodinâmica*, *Citologia*).
* **Manutenção de Enunciados Limpos**: O texto complementar de apoio é injetado dinamicamente apenas na chamada de IA e não é gravado fisicamente dentro do enunciado da questão no JSON, mantendo a integridade original dos dados.
* **Persistência Windows-Compatible e Nomes Limpos**: O módulo `saver.py` foi ajustado para substituir caracteres proibidos no Windows (como `/` em `"Q/X"`) por hífen `-`, salvar diretamente nas subpastas dinâmicas correspondentes (`{edital}_{ano}/`), e adotar o nome limpo simplificado para os textos complementares: `{edital}_{ano}_{tipo_ou_cor_limpo}_COMP_{idx}.json` (sem o prefixo redundante "Texto Complementar").
* **Validação de Sucesso**: Executado com êxito o `test_runner.py` usando o interpretador correto, validando a extração impecável de 72 questões, 3 textos complementares e 57 imagens da prova Unicamp 2026.
* **Portabilidade de Imagens (Caminhos Relativos)**: Implementação de caminhos de imagem 100% relativos (`./imgs/...` em vez de `unicamp_2026/imgs/...`) no JSON (`url_img`) e nas referências markdown dos enunciados (`![figura]`), tornando a pasta de saída do vestibular totalmente autônoma e portátil.
* **Segurança e Versionamento (`.gitignore`)**: Criação do arquivo `.gitignore` na raiz para impedir o rastreamento acidental do arquivo sensível `.env` (contendo a chave do Gemini), compilados de Python (`__pycache__`) e arquivos temporários no GitHub.
* **Melhorias de Usabilidade e UX Gráfica (`main.py`)**:
  - Exibição de aviso popup informativo orientando o usuário antes de abrir a janela de seleção do PDF.
  - Pergunta explícita via popup Sim/Não para autorizar o enriquecimento das questões com IA.
  - Se a IA for selecionada mas nenhuma chave Gemini for encontrada no `.env`, o programa apresenta um tutorial passo-a-passo e confirmação, recarregando dinamicamente o arquivo `.env` caso o usuário conclua as instruções no momento.
  - **Correção de Usabilidade da IA Gráfica**: Corrigido um bug crítico de recuo (indentação) no qual o fluxo de enriquecimento da IA estava acidentalmente aninhado no bloco `except` de tratamento de erro do Gabarito. Isso fazia com que a interface nunca solicitasse o enriquecimento por IA quando o fluxo de gabarito terminava com sucesso. O bloco foi movido para o nível do módulo e agora funciona perfeitamente.
* **Atualização dos Artefatos de Estudo**:
  - Guia de Estudos (`guia_estudo.md`) estendido para explicar o processamento em lote de 20, dupla defesa de tags, estimativa de tempo dinâmica e caminhos portáveis relativos de imagens.
  - Registro de Alterações (`historico_alteracoes.md`) atualizado para documentar cada evolução do código nesta sessão.
* **Padronização de Nomenclatura**: O usuário removeu manualmente o prefixo `"Questões-"` dos arquivos gerados (`saver.py`). O `test_runner.py` foi atualizado para alinhar sua verificação automática a essa nova regra, identificando e testando as questões corretamente sem o prefixo.
* **Nomenclatura Única de Imagens**: Implementação de nomenclatura exclusiva para imagens extraídas em `extractor.py`, aplicando o prefixo do vestibular `{edital}_{ano}_{tipo_prova}_` (ex: `unicamp_2026_Q-X_p2_img0.jpeg`). Isso evita colisões de nomes caso imagens de provas ou edições diferentes sejam reunidas no mesmo repositório, mantendo a compatibilidade automática com a associação de questões no JSON e Markdown.
* **Lista de Imagens em `url_img`**: Alterado o esquema da propriedade `url_img` nos modelos Pydantic (`Conteudo` e `AlternativaItem`) de `Optional[str]` para uma lista de strings (`List[str]`). Ajustada a função `enriquecer` em `processor.py` para mapear todos os recursos gráficos (imagens e desenhos vetoriais) associados a uma mesma questão na lista (em vez de reter apenas a primeira), e adaptado o `test_runner.py` para reportar essa lista de forma legível.
* **Associação Robusta de Imagens via Regex (Column-Proof)**: Em vez de realizar uma associação geométrica baseada em coordenadas `y` brutas (que falha em páginas com duas colunas), implementamos uma extração por Regex (`re.findall`) diretamente no texto do enunciado e das alternativas de cada questão. Como o motor `extrair_texto` já insere as referências markdown `![figura](...)` respeitando a divisão inteligente de colunas, conseguimos extrair as imagens de forma 100% fiel e sem falsos-positivos de outras questões.


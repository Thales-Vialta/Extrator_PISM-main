# Tarefas de Execução: Otimização Geral e Refatoração na Raiz (Unicamp)

Este documento rastreia o progresso do desenvolvimento das otimizações aprovadas, incluindo a migração do código da subpasta `Teste/` para a raiz, a alteração para processamento em lotes de 20 questões por IA, estimativa dinâmica de tempo e a limpeza do workspace.

## Checklist de Implementação

- `[x]` **Fase 1: Preparação e Migração de Arquivos**
  - `[x]` Mover e mesclar os arquivos aprimorados da pasta `Teste/` para a raiz (`extractor.py`, `models.py`, `processor.py`, `saver.py`, `main.py`, `test_runner.py`).
  - `[x]` Criar arquivo `.env.example` na raiz com exemplo da chave API.
  - `[x]` Verificar integridade das importações no novo código na raiz.

- `[x]` **Fase 2: Ajuste dos Modelos de Dados (`models.py`)**
  - `[x]` Adicionar classes Pydantic para estruturar a análise em lote do Gemini (`AnaliseQuestaoIA` e `LoteAnaliseQuestaoIA`).

- `[x]` **Fase 3: Otimização e Processamento IA (`processor.py`)**
  - `[x]` Implementar o enriquecimento por IA em lotes de 20 questões.
  - `[x]` Implementar estimativa dinâmica de tempo medindo a duração da primeira requisição à API e aplicando-a sobre as restantes.
  - `[x]` Adicionar o filtro programático complementar (blacklist em Python) para remover tags inválidas (por exemplo, nomes de matérias genéricas ou vestibulares).
  - `[x]` Ajustar o prompt do Gemini de forma a instruí-lo severamente a retornar exclusivamente tópicos conceituais nas tags.
  - `[x]` Garantir que o enunciado no JSON da questão permaneça limpo (sem texto complementar anexado fisicamente na gravação), passando o texto complementar à IA puramente através do prompt de forma externa.

- `[x]` **Fase 4: Ajuste de Persistência (`saver.py`)**
  - `[x]` Configurar gravação compatível com Windows substituindo `/` por `-` no tipo/cor para compor os nomes dos arquivos.
  - `[x]` Formatar nomes de arquivos de questões: `Questões-{edital}_{ano}_{tipo_ou_cor}_{numero}.json`.
  - `[x]` Formatar nomes de arquivos de textos complementares: `Texto Complementar {edital}_{ano}_{tipo_ou_cor}_COMP_{contador}.json` (contador sequencial iniciando em 1).
  - `[x]` Salvar os resultados estruturados diretamente na pasta dinâmica `{edital}_{ano}/` e imagens na subpasta `{edital}_{ano}/imgs/`.

- `[x]` **Fase 5: Interface Principal e Fluxo (`main.py`)**
  - `[x]` Ajustar `main.py` na raiz para coordenar todos os novos passos, incluindo compatibilidade no Windows e processamento em lote.

- `[x]` **Fase 6: Limpeza do Workspace (Declutter)**
  - `[x]` Remover pasta `Teste/` e subdiretórios redundantes.
  - `[x]` Remover `texto para o gemini.txt`.
  - `[x]` Limpar pastas órfãs geradas anteriormente na raiz (`questoes_json/`, `textos_json/`, `imgs/`).

- `[x]` **Fase 7: Verificação e Validação**
  - `[x]` Executar `test_runner.py` na raiz para garantir pleno funcionamento da extração geométrica, gabaritos e enriquecimento por IA.
  - `[x]` Validar que os JSONs gerados estão com enunciados limpos e nomes de arquivos 100% corretos no Windows.
  - `[x]` Atualizar o Guia de Estudos (`guia_estudo.md`) documentando os novos recursos de lote de 20, estimativa dinâmica e filtros de tag.
  - `[x]` Adicionar nova entrada no Log de Alterações (`historico_alteracoes.md`).

- `[x]` **Fase 8: Conversão de `url_img` para Lista de Strings (`List[str]`)**
  - `[x]` Modificar `models.py` para definir `url_img: List[str] = []` em `Conteudo` e `AlternativaItem`.
  - `[x]` Modificar `processor.py` para mapear todas as imagens na lista `q.conteudo.url_img`.
  - `[x]` Modificar `test_runner.py` para exibir e verificar corretamente o campo lista de imagens.
  - `[x]` Executar testes locais para validar o novo formato de arquivo e gerar cópias legíveis atualizadas na pasta `Artefatos/`.

- `[x]` **Fase 9: Associação Robusta de Imagens via Regex (Column-Proof)**
  - `[x]` Modificar `enriquecer` em `processor.py` para extrair imagens via regex do enunciado e alternativas.
  - `[x]` Testar e validar com `test_runner.py` que a Questão 1 tem exatamente 2 imagens, a Questão 2 tem 3 imagens e a Questão 3 tem 1 imagem.
  - `[x]` Sincronizar todos os artefatos (`guia_estudo.md`, `walkthrough.md`, `historico_alteracoes.md` e `task.md`) com a pasta `Artefatos/`.


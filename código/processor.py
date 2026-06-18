import re

from models import *

def extrair_textos_comp(texto):
    # Usando a expressão regular ancorada e limitada a 350 caracteres para textos complementares do PISM
    padrao = r"((?:^|\n)[ \t]*(?:Leia|A\s+seguir|O\s+Texto\s+[IVX\d]+)\b.{1,350}?quest[õo\u02dcea\s]+s?\s+(\d+(?:\s+e\s+\d+|\s*,\s*\d+)*)\.?\n)(.*?)(?=(?:Quest[\u02dcaã\~]+o|QUESTÃO)\s+\d+\.)"
    resultados = []
    for match in re.finditer(padrao, texto, re.DOTALL | re.IGNORECASE):
        numeros = re.findall(r"\d+", match.group(2))
        conteudo = match.group(3).strip()
        resultados.append(
            TextoComplementar(
                metadadosComp=MetadadosComp(codigos_questoes=numeros),
                conteudoComp=ConteudoComp(enunciado=conteudo)
            )
        )
    return resultados

def detectar_edital_ano(pdf_path):
    """
    Detecta dinamicamente o edital (pism), o ano e a especificação do PISM (módulo e dia) a partir do nome do arquivo ou do texto.
    """
    nome_arquivo = os.path.basename(pdf_path).lower()
    edital = "pism"
    
    # Extrai o ano do nome do arquivo ou do texto do PDF
    ano = None
    match_ano = re.search(r"\b(20[0-9]{2})\b", nome_arquivo)
    if match_ano:
        ano = int(match_ano.group(1))
    
    # Extrai módulo e dia do nome do arquivo
    modulo = None
    dia = None
    
    match_filename = re.search(r"pism[-_\s]*([1-3i]+)[-_\s]*dia[-_\s]*([1-2]+)", nome_arquivo)
    if match_filename:
        mod_str = match_filename.group(1).lower()
        if mod_str in ["1", "i"]:
            modulo = 1
        elif mod_str in ["2", "ii"]:
            modulo = 2
        elif mod_str in ["3", "iii"]:
            modulo = 3
        dia = int(match_filename.group(2))
    
    # Tenta ler o primeiro slide para complementar informações se necessário
    try:
        import fitz
        doc = fitz.open(pdf_path)
        first_page_text = doc[0].get_text()
        
        if not ano:
            match_text_ano = re.search(r"pism\s*-\s*programa\s+de\s+ingresso\s+(20[0-9]{2})", first_page_text, re.IGNORECASE)
            if match_text_ano:
                ano = int(match_text_ano.group(1))
            else:
                match_text_ano_gen = re.search(r"\b(20[0-9]{2})\b", first_page_text)
                if match_text_ano_gen:
                    ano = int(match_text_ano_gen.group(1))
        
        if not modulo:
            match_mod = re.search(r"pism\s+([ivx]+)", first_page_text, re.IGNORECASE)
            if match_mod:
                roman = match_mod.group(1).upper()
                if roman == "I":
                    modulo = 1
                elif roman == "II":
                    modulo = 2
                elif roman == "III":
                    modulo = 3
            else:
                match_mod_2 = re.search(r"m[oó´o]+dulo\s*(\d+)", first_page_text, re.IGNORECASE)
                if match_mod_2:
                    modulo = int(match_mod_2.group(1))
        
        if not dia:
            match_dia = re.search(r"(\d+)[ººo]?\s*dia", first_page_text, re.IGNORECASE)
            if match_dia:
                dia = int(match_dia.group(1))
            else:
                match_dia_2 = re.search(r"dia\s*(\d+)", first_page_text, re.IGNORECASE)
                if match_dia_2:
                    dia = int(match_dia_2.group(1))
    except Exception as e:
        print(f"Aviso ao ler primeiro slide do PDF para detecção: {e}")
        
    if not ano:
        ano = 2025 # Default fallback
    if not modulo:
        modulo = 1
    if not dia:
        dia = 1
        
    tipo_prova = f"modulo_{modulo}_dia_{dia}"
    return edital, ano, tipo_prova

def extrair_questoes(texto, edital="unicamp", ano=2026, tipo_prova="Q-X"):
    # Expressão regular para capturar "Quest˜ao X." ou "Questão X." (com til pequeno \u02dc ou normal)
    padrao = r"((?:Quest[\u02dcaã\~]+o|QUESTÃO)\s+(\d+)\.?)(.*?)(?=(?:Quest[\u02dcaã\~]+o|QUESTÃO)\s+\d+\.?|\Z)"
    questoes = []

    for match in re.finditer(padrao, texto, re.DOTALL | re.IGNORECASE):
        numero = int(match.group(2))
        bloco = match.group(3).strip()
        
        # Filtro de segurança: no PISM as objetivas vão de 1 a 20
        if numero < 1 or numero > 20:
            continue
            
        # PISM usa alternativas entre parênteses como (A) ou (a)
        partes = re.split(r"\n\s*\(([A-Ea-e])\)\s*", bloco)
        enunciado = partes[0].strip()

        alt_dict = {}
        for i in range(1, len(partes), 2):
            if i + 1 < len(partes):
                letra = partes[i].lower()
                texto_alt = partes[i+1].strip()
                alt_dict[letra] = AlternativaItem(texto=texto_alt)

        questoes.append(
            Questao(
                metadados=Metadados(
                    codigo=f"{edital}_{ano}_q{numero}",
                    edital=edital,
                    numero=numero,
                    tipo_ou_cor=tipo_prova,
                    ano=ano
                ),
                conteudo=Conteudo(enunciado=enunciado),
                especificacao=Especificacao(materia="desconhecida", tags=[]),
                alternativas=Alternativas(
                    a=alt_dict.get("a", AlternativaItem()),
                    b=alt_dict.get("b", AlternativaItem()),
                    c=alt_dict.get("c", AlternativaItem()),
                    d=alt_dict.get("d", AlternativaItem()),
                    e=alt_dict.get("e")
                )
            )
        )

    return questoes

def mapear_textos_comp(textos_comp):

    mapa = {}

    for t in textos_comp:

        for cod in t.metadadosComp.codigos_questoes:

            mapa[int(cod)] = t

    return mapa

def localizar_questoes(paginas):
    posicoes = []
    for p in paginas:
        for b in p["blocks"]:
            # Reconhece PISM "Quest˜ao \d+" de forma flexível e case-insensitive
            match = re.search(r"(?:Quest[\u02dcaã\~]+o|QUESTÃO)\s+(\d+)", b[4], re.IGNORECASE)
            if match:
                numero = int(match.group(1))
                if 1 <= numero <= 20: # Limita às objetivas do PISM
                    posicoes.append({
                        "numero": numero,
                        "pagina": p["numero"],
                        "y": b[1]
                    })
    posicoes.sort(key=lambda x: (x["pagina"], x["y"]))
    return posicoes

def associar_imagens(questoes_pos, imagens):

    mapa = {q["numero"]: [] for q in questoes_pos}

    for img in imagens:

        img_pos = (img["pagina"], img["y"])

        melhor_q = None

        for q in questoes_pos:

            q_pos = (q["pagina"], q["y"])

            if q_pos <= img_pos:

                melhor_q = q["numero"]

            else:

                break

        if melhor_q:

            mapa[melhor_q].append(img["arquivo"])

    return mapa

def enriquecer(questoes, mapa_textos, mapa_imgs):

    for q in questoes:

        # Extrai imagens do enunciado via regex (evita problemas com duas colunas)
        q.conteudo.url_img = re.findall(r"!\[.*?\]\((.*?)\)", q.conteudo.enunciado)

        # Extrai imagens das alternativas, se houver
        for letra in ["a", "b", "c", "d", "e"]:

            alt = getattr(q.alternativas, letra)

            if alt and alt.texto:

                alt.url_img = re.findall(r"!\[.*?\]\((.*?)\)", alt.texto)

    return questoes

import fitz

def extrair_gabarito(gabarito_path):
    doc = fitz.open(gabarito_path)
    texto = ""
    for page in doc:
        texto += page.get_text()

    # Padrão robusto para PISM (ex: "01 A", "01 - A", "01: A", "01\nA")
    pares = re.findall(r"\b(0?[1-9]|[1-3]\d|40)\b\s*[\s\-:\n]\s*\b([A-Ea-e])\b", texto)
    respostas = {}
    for num_str, letra in pares:
        respostas[int(num_str)] = letra.lower()

    # Detecta módulo e dia no gabarito
    tipo_gabarito = "PISM"
    mod_match = re.search(r"m[oó´o]+dulo\s+([i|ii|iii\d]+)", texto, re.IGNORECASE)
    dia_match = re.search(r"(\d+)[ºo]?\s+dia|dia\s+(\d+)", texto, re.IGNORECASE)
    
    if mod_match:
        tipo_gabarito += f" Módulo {mod_match.group(1).upper()}"
    if dia_match:
        d = dia_match.group(1) or dia_match.group(2)
        tipo_gabarito += f" Dia {d}"

    return respostas, tipo_gabarito

def aplicar_gabarito(questoes, respostas):

    for q in questoes:

        num = q.metadados.numero

        if num in respostas:

            resp_correta = respostas[num]

            if q.alternativas.a:

                q.alternativas.a.correta = (resp_correta == "a")

            if q.alternativas.b:

                q.alternativas.b.correta = (resp_correta == "b")

            if q.alternativas.c:

                q.alternativas.c.correta = (resp_correta == "c")

            if q.alternativas.d:

                q.alternativas.d.correta = (resp_correta == "d")

            if q.alternativas.e:

                q.alternativas.e.correta = (resp_correta == "e")

    return questoes

import os

def carregar_env(caminho_env=".env"):

    """
    Leitor nativo e seguro para arquivos .env (sem dependências externas)
    """

    if not os.path.exists(caminho_env):

        pasta_script = os.path.dirname(os.path.abspath(__file__))

        caminho_env = os.path.join(pasta_script, ".env")

    if os.path.exists(caminho_env):

        with open(caminho_env, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if line and not line.startswith("#") and "=" in line:

                    chave, valor = line.split("=", 1)

                    val = valor.strip().strip('"').strip("'")

                    os.environ[chave.strip()] = val

try:

    import google.generativeai as genai

    HAS_GEMINI = True

except ImportError:

    HAS_GEMINI = False

def enriquecer_questoes_com_ia(questoes, api_key, mapa_textos=None, max_questoes=None):
    """
    Enriquece as questões da prova com resoluções, dicas, matéria e tags geradas por IA.
    Processa as questões em lotes de 20 para otimizar custos e velocidade.
    A estimativa de tempo restante é dinâmica, baseada no tempo real medido da primeira chamada.
    Aplica filtro programático complementar (blacklist) nas tags retornadas.
    """
    if not HAS_GEMINI:
        print("\n[IA Gemini] A biblioteca 'google-generativeai' não está instalada.")
        print("Para ativar enriquecimento automático por IA, instale rodando:")
        print("  pip install google-generativeai")
        return questoes

    if not api_key or api_key == "INSIRA_SUA_CHAVE_GEMINI_AQUI":
        print("\n[IA Gemini] Chave de API do Gemini não configurada no arquivo '.env'.")
        print("Insira sua chave no arquivo '.env' local para habilitar o preenchimento automático por IA.")
        return questoes

    questoes_para_processar = questoes[:max_questoes] if max_questoes is not None else questoes
    total = len(questoes_para_processar)
    if total == 0:
        return questoes

    tamanho_lote = 20
    lotes = [questoes_para_processar[x:x+tamanho_lote] for x in range(0, total, tamanho_lote)]
    total_lotes = len(lotes)

    print(f"\nIniciando enriquecimento de {total} questões em {total_lotes} lotes (limite de 20 por lote) via IA (Google Gemini)...")
    print("Aviso: Chamadas espaçadas em 4.5 segundos para respeitar o limite de 15 RPM da API.")

    def formatar_tempo(segundos):
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        if minutos > 0:
            return f"{minutos} min {segs} s"
        return f"{segs} s"

    TAG_BLACKLIST = {
        "pism", "unicamp", "fuvest", "enem", "vestibular", "prova", "questão", "questao", "questoes", "questões",
        "matemática", "matematica", "física", "fisica", "química", "quimica", "biologia", "história", "historia",
        "geografia", "português", "portugues", "literatura", "inglês", "ingles", "filosofia", "sociologia", 
        "espanhol", "humanas", "exatas", "ciências", "ciencias", "ciências da natureza", "ciências humanas",
        "geral", "materia", "disciplina", "desconhecida", "desconhecido"
    }

    import time
    tempo_primeira_req = None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Dicionário auxiliar para localizar as questões pelo número
        mapa_questoes_obj = {q.metadados.numero: q for q in questoes_para_processar}

        for idx, lote in enumerate(lotes):
            if idx > 0:
                time.sleep(4.5)

            print(f"\n[IA Gemini] Processando lote {idx+1} de {total_lotes} (Questões: {', '.join(str(q.metadados.numero) for q in lote)})...")

            # Construção do prompt em lote
            prompt = """Você é um professor especialista no vestibular PISM (Programa de Ingresso Seletivo Misto da UFJF).
Analise as seguintes questões do vestibular e forneça de maneira estruturada:
1. Matéria (ex: "História", "Física", "Biologia", etc.)
2. Tags conceituais: Retorne exclusivamente tópicos teóricos ou subtemas do assunto da questão (ex: "Termodinâmica", "Segunda Guerra Mundial", "Citologia"). É expressamente PROIBIDO incluir o nome do vestibular ("pism", "unicamp", "enem", etc.) ou matérias gerais ("física", "história", etc.) nas tags.
3. Resolução detalhada passo a passo em português.
4. Dica de estudo específica relacionada a este assunto.

Abaixo estão listadas as questões a analisar:
"""
            for q in lote:
                prompt += f"\n--- QUESTÃO {q.metadados.numero} ---\n"
                if mapa_textos and q.metadados.numero in mapa_textos:
                    texto_comp = mapa_textos[q.metadados.numero].conteudoComp.enunciado
                    prompt += f"[TEXTO COMPLEMENTAR DE APOIO]:\n{texto_comp}\n\n"
                
                prompt += f"ENUNCIADO:\n{q.conteudo.enunciado}\n"
                prompt += "ALTERNATIVAS:\n"
                prompt += f"A) {q.alternativas.a.texto if q.alternativas.a else ''}\n"
                prompt += f"B) {q.alternativas.b.texto if q.alternativas.b else ''}\n"
                prompt += f"C) {q.alternativas.c.texto if q.alternativas.c else ''}\n"
                prompt += f"D) {q.alternativas.d.texto if q.alternativas.d else ''}\n"
                if q.alternativas.e:
                    prompt += f"E) {q.alternativas.e.texto}\n"

            try:
                t_start = time.time()
                resposta = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=LoteAnaliseQuestaoIA
                    )
                )
                t_end = time.time()
                duracao_chamada = t_end - t_start

                if idx == 0:
                    tempo_primeira_req = duracao_chamada
                    print(f"[IA Gemini] Primeira requisição durou {duracao_chamada:.1f} s.")

                dados_lote = LoteAnaliseQuestaoIA.model_validate_json(resposta.text)

                # Processar os dados recebidos para cada questão
                for analise in dados_lote.questoes:
                    num = analise.numero
                    if num in mapa_questoes_obj:
                        q_obj = mapa_questoes_obj[num]
                        q_obj.especificacao.materia = analise.materia
                        q_obj.conteudo.resolucao = analise.resolucao
                        q_obj.conteudo.dica = analise.dica

                        # Filtro programático complementar nas tags (double-defense)
                        tags_filtradas = []
                        for tag in analise.tags:
                            tag_clean = tag.strip().lower()
                            if (tag_clean not in TAG_BLACKLIST and 
                                len(tag_clean) > 1 and 
                                not any(b in tag_clean for b in ["pism", "unicamp", "fuvest", "enem", "vestibular"])):
                                tags_filtradas.append(tag.strip())
                        
                        q_obj.especificacao.tags = tags_filtradas

                lotes_restantes = total_lotes - (idx + 1)
                tempo_medido = tempo_primeira_req if tempo_primeira_req is not None else 8.0
                tempo_restante = lotes_restantes * (tempo_medido + 4.5)
                tempo_restante_str = formatar_tempo(tempo_restante)
                print(f"Lote {idx+1} de {total_lotes} enriquecido com sucesso. Tempo restante estimado: {tempo_restante_str}")

            except Exception as inner_e:
                print(f"Erro ao processar lote {idx+1} com IA: {inner_e}")

    except Exception as e:
        print(f"Falha crítica na conexão ou inicialização da API do Gemini: {e}")

    return questoes


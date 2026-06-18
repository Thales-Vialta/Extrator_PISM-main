import os

import sys

from extractor import *

from processor import *

from saver import *

carregar_env()

pdf_path = r"C:\Users\thale\OneDrive\Documentos\Pism-1-Dia-1.pdf"

if not os.path.exists(pdf_path):

    print(f"Erro: PDF não encontrado em {pdf_path}")

    sys.exit(1)

print(f"Iniciando o teste com o PDF: {pdf_path}")

edital, ano, tipo_prova = detectar_edital_ano(pdf_path)

nome_base = os.path.splitext(os.path.basename(pdf_path))[0]
pasta_saida = nome_base

print("Extraindo PDF...")

paginas, doc = extrair_pdf(pdf_path)

print(f"Total de páginas: {len(paginas)}")

print("Extraindo imagens...")

prefixo_img = f"{nome_base}_{tipo_prova.replace('/', '-')}"
imagens = extrair_imagens(doc, output_dir=f"{pasta_saida}/imgs", prefixo=prefixo_img)

print(f"Total de imagens válidas extraídas (fora de cabeçalho/rodapé): {len(imagens)}")

print("Extraindo texto...")

texto = extrair_texto(paginas, imagens)

print("Processando textos complementares...")

textos_comp = extrair_textos_comp(texto)

print(f"Total de textos complementares: {len(textos_comp)}")

print("Processando questões...")

questoes = extrair_questoes(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)

print(f"Total de questões encontradas: {len(questoes)}")

print("Mapeando e associando componentes...")

mapa_textos = mapear_textos_comp(textos_comp)

questoes_pos = localizar_questoes(paginas)

mapa_imgs = associar_imagens(questoes_pos, imagens)

questoes = enriquecer(questoes, mapa_textos, mapa_imgs)

gabarito_path = r"C:\Users\thale\OneDrive\Documentos\gabarito-pism-1-dia-1.pdf"

if os.path.exists(gabarito_path):

    print(f"Aplicando gabarito automático de teste: {gabarito_path} ...")

    respostas, tipo_gabarito = extrair_gabarito(gabarito_path)

    questoes = aplicar_gabarito(questoes, respostas)

    print(f"Gabarito para PROVAS {tipo_gabarito} aplicado com sucesso!")

else:

    # Como não temos o arquivo de gabarito físico, vamos aplicar os resultados conhecidos
    # Português (1-5): A, D, C, B, A; Geografia (6-10): A, E, C, D, D;
    # Matemática (11-15): B, C, D, A, D; Química (16-20): B, C, D, E, A.
    respostas_mock = {
        1: "a", 2: "d", 3: "c", 4: "b", 5: "a",
        6: "a", 7: "e", 8: "c", 9: "d", 10: "d",
        11: "b", 12: "c", 13: "d", 14: "a", 15: "d",
        16: "b", 17: "c", 18: "d", 19: "e", 20: "a"
    }
    print("Aplicando gabarito mockado conhecido para o PISM I Dia 1...")
    questoes = aplicar_gabarito(questoes, respostas_mock)

api_key = os.getenv("GEMINI_API_KEY")

questoes = enriquecer_questoes_com_ia(questoes, api_key, mapa_textos=mapa_textos, max_questoes=2)

print("Salvando resultados...")

tipo_cor = questoes[0].metadados.tipo_ou_cor if questoes else "Q-X"

salvar_questoes(questoes, pasta=pasta_saida)

salvar_textos(textos_comp, pasta=pasta_saida, edital=edital, ano=ano, tipo_ou_cor=tipo_cor)

print("\n--- Verificações Rápidas de Qualidade ---")

imgs_dir = f"{pasta_saida}/imgs"

if os.path.exists(imgs_dir):

    arquivos_img = os.listdir(imgs_dir)

    print(f"Imagens salvas na pasta '{imgs_dir}': {len(arquivos_img)}")

else:

    print("Nenhuma imagem salva.")

questoes_dir = pasta_saida

if os.path.exists(questoes_dir):

    questoes_geradas = [f for f in os.listdir(questoes_dir) if "_COMP" not in f and f.endswith(".json") and re.match(r".*_\d+\.json$", f)]

    print(f"Arquivos JSON de questões salvos em '{questoes_dir}': {len(questoes_geradas)}")

    questoes_verificar = sorted(questoes_geradas, key=lambda x: int(re.search(r"_(\d+)\.json$", x).group(1)))[:2]

    for q_file in questoes_verificar:

        with open(os.path.join(questoes_dir, q_file), "r", encoding="utf-8") as f:

            q_data = json.load(f)

            num = q_data["metadados"]["numero"]

            enunciado = q_data["conteudo"]["enunciado"]

            url_img = q_data["conteudo"]["url_img"]

            alt_a_txt = q_data["alternativas"]["a"]["texto"]

            alt_a_corr = q_data["alternativas"]["a"]["correta"]

            print(f"\nQuestão {num}:")

            print(f"  - Imagens associadas ({len(url_img)}): {url_img}")

            print(f"  - Início do Enunciado:\n{enunciado[:150]}...")

            print(f"  - Alternativa A correta? {alt_a_corr} (Texto: {alt_a_txt[:50]}...)")

    q1_file = f"{edital}_{ano}_{tipo_cor.replace('/', '-')}_1.json"

    if os.path.exists(os.path.join(questoes_dir, q1_file)):

        with open(os.path.join(questoes_dir, q1_file), "r", encoding="utf-8") as f:

            q_data = json.load(f)

            num = q_data["metadados"]["numero"]

            conteudo_obj = q_data["conteudo"]

            alternativas_obj = q_data["alternativas"]

            print(f"\n--- Validação da Questão {num} (Gabarito Oficial: A) ---")

            print(f"Novos campos em Conteúdo:")

            print(f"  - resolucao: {conteudo_obj.get('resolucao')}")

            print(f"  - dica: {conteudo_obj.get('dica')}")

            print("Estados das Alternativas:")

            for alt_letra in ["a", "b", "c", "d", "e"]:

                alt_data = alternativas_obj.get(alt_letra)

                if alt_data:

                    print(f"  - Alternativa {alt_letra.upper()}: correta = {alt_data['correta']}")

    else:

        print(f"\nNota: {q1_file} não processada com IA no teste rápido.")

else:

    print("Nenhuma questão salva.")

print("\nFinalizado com sucesso")



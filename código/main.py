from extractor import *

from processor import *

from saver import *

from tkinter import Tk, messagebox

from tkinter.filedialog import askopenfilename

import os

def selecionar_pdf():

    root = Tk()

    root.withdraw()

    messagebox.showinfo(

        "Selecionar Prova",

        "Por favor, na tela a seguir, selecione o arquivo PDF da Prova do vestibular que deseja extrair."

    )

    caminho = askopenfilename(

        title="Selecione o PDF da Prova",

        filetypes=[("Arquivos PDF", "*.pdf")]

    )

    return caminho

carregar_env()

pdf_path = selecionar_pdf()

if not pdf_path:

    print("Nenhum arquivo selecionado.")

else:

    print("Arquivo escolhido:", pdf_path)

edital, ano, tipo_prova = detectar_edital_ano(pdf_path)

nome_base = os.path.splitext(os.path.basename(pdf_path))[0]
pasta_saida = nome_base

paginas, doc = extrair_pdf(pdf_path)

prefixo_img = f"{nome_base}_{tipo_prova.replace('/', '-')}"
imagens = extrair_imagens(doc, output_dir=f"{pasta_saida}/imgs", prefixo=prefixo_img)

texto = extrair_texto(paginas, imagens)

textos_comp = extrair_textos_comp(texto)

questoes = extrair_questoes(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)

mapa_textos = mapear_textos_comp(textos_comp)

questoes_pos = localizar_questoes(paginas)

mapa_imgs = associar_imagens(questoes_pos, imagens)

questoes = enriquecer(questoes, mapa_textos, mapa_imgs)

try:

    importar_gabarito = messagebox.askyesno(

        "Importar Gabarito",

        "Deseja importar um gabarito correspondente a esta prova?"

    )

    if importar_gabarito:

        gabarito_path = askopenfilename(

            title="Selecione o PDF do Gabarito",

            filetypes=[("Arquivos PDF", "*.pdf")]

        )

        if gabarito_path:

            respostas, tipo_gabarito = extrair_gabarito(gabarito_path)

            nome_prova = os.path.basename(pdf_path)

            confirmado = messagebox.askyesno(

                "Confirmar Compatibilidade",

                f"Prova selecionada:\n{nome_prova}\n\n"

                f"Gabarito detectado:\nPROVAS {tipo_gabarito}\n\n"

                "Eles correspondem à mesma prova? Deseja prosseguir e aplicar as respostas?"

            )

            if confirmado:

                questoes = aplicar_gabarito(questoes, respostas)

                print("Gabarito aplicado com sucesso!")

            else:

                print("Aplicação do gabarito cancelada pelo usuário.")

except Exception as e:
    print(f"Não foi possível interagir via GUI para o gabarito ({e}). Continuando sem gabarito...")

deseja_ia = False
try:
    deseja_ia = messagebox.askyesno(
        "Enriquecimento com IA",
        "Deseja enriquecer as questões da prova com resoluções, dicas, matérias e tags geradas por Inteligência Artificial (Google Gemini)?"
    )
except Exception as e:
    print(f"Não foi possível interagir via GUI para a IA ({e}). Pulando IA...")

api_key = os.getenv("GEMINI_API_KEY")
is_valid_key = api_key and api_key.strip() != "" and api_key.strip() != "INSIRA_SUA_CHAVE_GEMINI_AQUI"

if deseja_ia:
    if not is_valid_key:
        passos = (
            "Para utilizar o enriquecimento por IA, você precisa configurar sua chave de API gratuita do Gemini.\n\n"
            "Passos para obter e configurar sua chave:\n"
            "1. Acesse o Google AI Studio (https://aistudio.google.com/)\n"
            "2. Faça login com sua conta Google e clique no botão 'Create API Key'\n"
            "3. Copie a chave gerada\n"
            "4. Crie ou abra o arquivo '.env' na pasta raiz do seu projeto\n"
            "5. Adicione a seguinte linha:\n"
            "   GEMINI_API_KEY=sua_chave_aqui\n\n"
            "Você já realizou essa configuração e salvou o arquivo '.env' agora?"
        )
        confirmou = messagebox.askyesno("Configurar Chave API Gemini", passos)
        if confirmou:
            carregar_env()
            api_key = os.getenv("GEMINI_API_KEY")
            is_valid_key = api_key and api_key.strip() != "" and api_key.strip() != "INSIRA_SUA_CHAVE_GEMINI_AQUI"
            if not is_valid_key:
                messagebox.showwarning(
                    "Chave Não Detectada",
                    "Ainda não foi possível encontrar uma chave de API válida no arquivo '.env'.\n"
                    "O processamento continuará sem o enriquecimento por IA."
                )
                deseja_ia = False
        else:
            deseja_ia = False

if deseja_ia and is_valid_key:
    questoes = enriquecer_questoes_com_ia(questoes, api_key, mapa_textos=mapa_textos)
else:
    print("\n[IA Gemini] Enriquecimento por IA pulado ou chave de API não configurada.")

tipo_cor = questoes[0].metadados.tipo_ou_cor if questoes else "Q-X"

salvar_questoes(questoes, pasta=pasta_saida)

salvar_textos(textos_comp, pasta=pasta_saida, edital=edital, ano=ano, tipo_ou_cor=tipo_cor)

print("Finalizado com sucesso")



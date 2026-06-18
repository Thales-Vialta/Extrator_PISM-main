import fitz

import os

def extrair_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    paginas = []

    for page_num, page in enumerate(doc):

        blocks = page.get_text("blocks")

        paginas.append({

            "numero": page_num,

            "blocks": blocks,

            "page": page

        })

    return paginas, doc

def extrair_texto(paginas, imagens=[]):

    texto = ""

    imgs_por_pagina = {}

    for img in imagens:

        p = img["pagina"]

        if p not in imgs_por_pagina:

            imgs_por_pagina[p] = []

        imgs_por_pagina[p].append(img)

    for p in paginas:

        page_num = p["numero"]

        blocks = p["blocks"]

        page_imgs = imgs_por_pagina.get(page_num, [])

        page = p["page"]

        page_width = page.rect.width

        mid_x = page_width / 2

        elementos_esquerda = []

        elementos_direita = []

        for b in blocks:

            centro_x = (b[0] + b[2]) / 2

            coluna = "esquerda" if centro_x < mid_x else "direita"

            el = {

                "tipo": "texto",

                "x": centro_x,

                "y": b[1],

                "conteudo": b[4]

            }

            if coluna == "esquerda":

                elementos_esquerda.append(el)

            else:

                elementos_direita.append(el)

        elementos_esquerda.sort(key=lambda x: x["y"])

        elementos_direita.sort(key=lambda x: x["y"])

        for img in page_imgs:

            img_x = img.get("x", 0)

            img_y = img["y"]

            coluna_img = "esquerda" if img_x < mid_x else "direita"

            el_img = {

                "tipo": "imagem",

                "x": img_x,

                "y": img_y,

                "conteudo": f'\n\n![figura](./imgs/{os.path.basename(img["arquivo"])})\n\n'

            }

            target_list = elementos_esquerda if coluna_img == "esquerda" else elementos_direita

            inserted = False

            for idx, el in enumerate(target_list):

                if el["y"] > img_y:

                    target_list.insert(idx, el_img)

                    inserted = True

                    break

            if not inserted:

                target_list.append(el_img)

        for el in elementos_esquerda:

            if el["tipo"] == "texto":

                texto += el["conteudo"] + "\n"

            else:

                texto += el["conteudo"]

        for el in elementos_direita:

            if el["tipo"] == "texto":

                texto += el["conteudo"] + "\n"

            else:

                texto += el["conteudo"]

    return texto

def extrair_imagens(doc, output_dir="imgs", prefixo=""):

    os.makedirs(output_dir, exist_ok=True)

    imagens = []

    for page_index in range(len(doc)):

        page = doc[page_index]

        page_height = page.rect.height

        margin_top = page_height * 0.1

        margin_bottom = page_height * 0.9

        drawings = page.get_drawings()

        rects_vetoriais = []

        for d in drawings:

            r = d["rect"]

            if r.is_empty or r.width < 5 or r.height < 5:

                continue

            if r.y1 <= margin_top or r.y0 >= margin_bottom:

                continue

            rects_vetoriais.append(r)

        grouped_drawings = []

        if rects_vetoriais:

            for r in rects_vetoriais:

                to_merge = []

                for m in grouped_drawings:

                    expanded = fitz.Rect(m.x0 - 30, m.y0 - 30, m.x1 + 30, m.y1 + 30)

                    if expanded.intersects(r):

                        to_merge.append(m)

                if to_merge:

                    union_rect = fitz.Rect(r)

                    for m in to_merge:

                        union_rect = union_rect | m

                        grouped_drawings.remove(m)

                    grouped_drawings.append(union_rect)

                else:

                    grouped_drawings.append(fitz.Rect(r))

        imgs = page.get_images(full=True)

        for i, img in enumerate(imgs):

            xref = img[0]

            rects = page.get_image_rects(xref)

            if not rects:

                continue

            valid_rects = []

            for r in rects:

                if r.y1 <= margin_top or r.y0 >= margin_bottom:

                    continue

                sobrepoe_desenho = False

                for m in grouped_drawings:

                    if m.width >= 25 and m.height >= 25:

                        intersection = r & m

                        if not intersection.is_empty:

                            overlap_ratio = intersection.get_area() / r.get_area()

                            if overlap_ratio > 0.5:

                                sobrepoe_desenho = True

                                break

                if sobrepoe_desenho:

                    continue

                valid_rects.append(r)

            if not valid_rects:

                continue

            base = doc.extract_image(xref)

            prefixo_limpo = f"{prefixo}_" if prefixo else ""
            nome = f"{output_dir}/{prefixo_limpo}p{page_index}_img{i}.{base['ext']}"

            with open(nome, "wb") as f:

                f.write(base["image"])

            for r in valid_rects:

                imagens.append({

                    "pagina": page_index,

                    "y": r.y0,

                    "x": r.x0,

                    "arquivo": nome

                })

        for idx, m in enumerate(grouped_drawings):

            if m.width >= 25 and m.height >= 25:

                padding = 5

                m_padded = fitz.Rect(

                    max(0, m.x0 - padding),

                    max(0, m.y0 - padding),

                    min(page.rect.width, m.x1 + padding),

                    min(page.rect.height, m.y1 + padding)

                )

                prefixo_limpo = f"{prefixo}_" if prefixo else ""
                nome = f"{output_dir}/{prefixo_limpo}p{page_index}_drawing{idx}.png"

                matrix = fitz.Matrix(2, 2)

                pix = page.get_pixmap(clip=m_padded, matrix=matrix)

                pix.save(nome)

                imagens.append({

                    "pagina": page_index,

                    "y": m_padded.y0,

                    "x": m_padded.x0,

                    "arquivo": nome

                })

    return imagens


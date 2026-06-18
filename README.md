# Extrator_Unicamp

Trello: https://trello.com/b/ikVkMxb4/extrator-unicamp

Este projeto busca extrair todas as questões de provas da UNICAMP que forem colocadas nele. Se o gabarito for colocado junto, irá apontar qual é a alternativa correta também.

Saídas: 1 JSON por questão, contendo:

Metadados:
    codigo: str
    edital: str
    numero: int
    tipo_ou_cor: str
    ano: int
    
Conteudo:
    enunciado: str
    url_img: Optional[str] = None
    dica: str
    resolucao: str
    
Especificacao: (ainda não implementado de maneira automática)
    materia: str
    tags: List[str]
    
Alternativas:
    Retorna todas as alternativas da questão, cada uma contendo texto, imagem(s) (se houver) e um booleano dizendo se é a correta. Se só houverem alternativas de "a" até "d", a alternativa "e" não é criada.

E, se houver texto complementar (enunciado para x questões), cria um JSON com:

Metadados:
    codigos_questoes: List[str] -> Quais questões têm esse texto complementar como enunciado.
    
Conteudo:
    enunciado: str
    img_url: Optional[str] = None



### Atualmente, consegue extrair questões da Unicamp 2026, talvez consiga de outros anos, mas ainda não foi testado.

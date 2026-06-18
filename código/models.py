from pydantic import BaseModel

from typing import Optional, List

class AlternativaItem(BaseModel):

    texto: Optional[str] = None

    url_img: List[str] = []

    correta: bool = False

class Metadados(BaseModel):

    codigo: str

    edital: str

    numero: int

    tipo_ou_cor: str

    ano: int

class Conteudo(BaseModel):

    enunciado: str

    url_img: List[str] = []

    resolucao: Optional[str] = None

    dica: Optional[str] = None

class Especificacao(BaseModel):

    materia: str

    tags: List[str]

class Alternativas(BaseModel):

    a: AlternativaItem

    b: AlternativaItem

    c: AlternativaItem

    d: AlternativaItem

    e: Optional[AlternativaItem] = None

class Questao(BaseModel):

    metadados: Metadados

    conteudo: Conteudo

    especificacao: Especificacao

    alternativas: Alternativas

class MetadadosComp(BaseModel):

    codigos_questoes: List[str]

class ConteudoComp(BaseModel):

    enunciado: str

    img_url: Optional[str] = None

class TextoComplementar(BaseModel):

    metadadosComp: MetadadosComp

    conteudoComp: ConteudoComp

class AnaliseQuestaoIA(BaseModel):

    numero: int

    materia: str

    tags: List[str]

    resolucao: str

    dica: str

class LoteAnaliseQuestaoIA(BaseModel):

    questoes: List[AnaliseQuestaoIA]



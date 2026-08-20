#!/usr/bin/env python3
"""
verificar_estilo.py — QA automatico de cadencia/estilo para pecas RDAA.

Espelha o verificar_formatacao.py do formatar-peca: em vez de confiar em
leitura estrutural de uma LLM para contar travessao, ponto-e-virgula e
tricolon de negacao (checklist-3-estilometria.md), este script CONTA.
Itens com regra objetiva entram no exit code. A peça final não pode conter
travessão explicativo recorrente, ponto-e-vírgula em cadeia, tricolon de negação,
abertura defensiva recorrente, dois-pontos ou aposto explicativo entre parênteses.
Marcadores isolados de lista
como (a), (i) e (1) são permitidos porque não são explicações.

Uso:
    python3 verificar_estilo.py caminho/para/peca.docx
    python3 verificar_estilo.py caminho/para/peca.txt

Sai com codigo 0 se nenhuma regra objetiva for violada. Sai com 1 caso
contrario. A lista de ocorrencias de dois-pontos continua sendo impressa para
facilitar o diagnóstico.
"""

import re
import sys

JANELA_PAGINA = 12  # aprox. paragrafos por pagina (nao ha paginacao real fora do Word)


def _paragraphs_from_docx(path):
    import docx
    doc = docx.Document(path)
    paragraphs = []
    seen_paragraphs = set()

    def append_paragraphs(items):
        for paragraph in items:
            marker = id(paragraph._p)
            if marker in seen_paragraphs:
                continue
            seen_paragraphs.add(marker)
            paragraphs.append(paragraph.text)

    def append_table(table):
        for row in table.rows:
            for cell in row.cells:
                append_paragraphs(cell.paragraphs)
                for nested_table in cell.tables:
                    append_table(nested_table)

    append_paragraphs(doc.paragraphs)
    for table in doc.tables:
        append_table(table)
    return paragraphs


def _paragraphs_from_txt(path):
    with open(path, encoding='utf-8') as f:
        return [l.rstrip('\n') for l in f]


def carregar_paragrafos(path):
    if path.lower().endswith('.docx'):
        return _paragraphs_from_docx(path)
    return _paragraphs_from_txt(path)


def _split_sentencas(paragrafo):
    # Split simples por . ! ? seguido de espaço/fim — nao trata abreviacoes,
    # suficiente para contar ocorrencias de ; dentro do mesmo periodo.
    return [s for s in re.split(r'(?<=[.!?])\s+', paragrafo) if s.strip()]


def checar_travessao(paragrafos):
    problemas = []
    candidatos = []
    paras_com_travessao = [i for i, p in enumerate(paragrafos) if '—' in p]
    total = sum(p.count('—') for p in paragrafos)

    for i in paras_com_travessao:
        # Travessao unico ate o fim da frase e uso legitimo (nao exige par
        # fechado) — nao contar isso como erro, so registrar como candidato.
        candidatos.append((i, paragrafos[i][:100]))

    if total >= 3:
        problemas.append(
            f"Travessao: {total} ocorrencia(s) na peca inteira (limite checklist-3, item I: 3+)."
        )

    for a, b in zip(paras_com_travessao, paras_com_travessao[1:]):
        if b == a + 1:
            problemas.append(
                f"Travessao em paragrafos consecutivos: {a} e {b}."
            )

    for i in range(0, len(paragrafos), JANELA_PAGINA):
        janela = paras_com_travessao_in_range = [
            j for j in paras_com_travessao if i <= j < i + JANELA_PAGINA
        ]
        pares_na_janela = sum(paragrafos[j].count('—') for j in janela) // 2
        if pares_na_janela > 1:
            problemas.append(
                f"Travessao: mais de um par na janela de paragrafos {i}-{i + JANELA_PAGINA - 1} "
                f"(aprox. 1 pagina) — {pares_na_janela} pares."
            )

    return problemas, candidatos


def checar_ponto_e_virgula(paragrafos):
    problemas = []
    for i, p in enumerate(paragrafos):
        for s in _split_sentencas(p):
            n = s.count(';')
            if n >= 2:
                problemas.append(
                    f"Paragrafo {i}: frase com {n} ponto(s)-e-virgula — "
                    f"provavel lista disfarcada de prosa corrida: {s[:100]!r}"
                )
    return problemas


_ABERTURA_DEFENSIVA = re.compile(
    r'^\s*(?:não\s+se\s+(?:pretende|busca|trata|ignora|desconhece|cuida|discute)|'
    r'a\s+questão\s+não\s+está\s+em|o\s+que\s+não\s+se\s+(?:pretende|busca|trata))\b',
    re.IGNORECASE,
)


def _parece_titulo(paragrafo):
    letras = [char for char in paragrafo if char.isalpha()]
    if not letras:
        return False
    return len(paragrafo.split()) <= 12 and sum(char.isupper() for char in letras) / len(letras) > 0.9


def listar_aberturas_defensivas(paragrafos):
    ocorrencias = []
    for i, paragrafo in enumerate(paragrafos):
        if _parece_titulo(paragrafo):
            continue
        primeira_frase = re.split(r'(?<=[.!?])\s+', paragrafo.strip(), maxsplit=1)[0]
        match = _ABERTURA_DEFENSIVA.match(primeira_frase)
        if match:
            formula = re.sub(r'\s+', ' ', match.group(0).strip()).lower()
            ocorrencias.append((i, formula, primeira_frase[:140]))
    return ocorrencias


def checar_aberturas_defensivas(paragrafos):
    ocorrencias = listar_aberturas_defensivas(paragrafos)
    if len(ocorrencias) < 3:
        formulas = {}
        for _, formula, _ in ocorrencias:
            formulas[formula] = formulas.get(formula, 0) + 1
        if max(formulas.values(), default=0) < 2:
            return []
    indices = [item[0] for item in ocorrencias]
    formulas = {}
    for _, formula, _ in ocorrencias:
        formulas[formula] = formulas.get(formula, 0) + 1
    repetidas = [f'{formula} ({quantidade}x)' for formula, quantidade in formulas.items() if quantidade >= 2]
    detalhe = f' fórmulas repetidas {repetidas}.' if repetidas else '.'
    return [
        f'Abertura defensiva recorrente em {len(ocorrencias)} parágrafo(s), nos parágrafos {indices}.{detalhe} '
        'Reescrever positivamente ou justificar a função argumentativa indispensável.'
    ]


def checar_tricolon_negacao(paragrafos):
    problemas = []
    padrao = re.compile(
        r'\bn[aã]o\b[^.;:]*?,\s*n[aã]o\b[^.;:]*?(?:,|\se\s)\s*n[aã]o\b|'
        r'\bnem\b[^.;:]*?\bnem\b[^.;:]*?\bnem\b',
        re.IGNORECASE,
    )
    for i, p in enumerate(paragrafos):
        for m in padrao.finditer(p):
            problemas.append(
                f"Paragrafo {i}: tricolon/tetracolon de negacao — {m.group(0)[:100]!r}"
            )
    return problemas


def checar_dois_pontos(paragrafos):
    problemas = []
    for i, p in enumerate(paragrafos):
        if ':' in p:
            problemas.append(
                f"Paragrafo {i}: dois-pontos proibido na peça final — reescrever com ponto, vírgula ou conectivo."
            )
    return problemas


_MARCADOR_PARENTESES = re.compile(r'^(?:[a-z]{1,3}|[ivxlcdm]{1,8}|\d{1,4})$', re.IGNORECASE)


def checar_aposto_explicativo(paragrafos):
    problemas = []
    padrao = re.compile(r'\(([^()\r\n]*)\)')
    for i, p in enumerate(paragrafos):
        for match in padrao.finditer(p):
            conteudo = match.group(1).strip()
            if not conteudo or _MARCADOR_PARENTESES.fullmatch(conteudo):
                continue
            problemas.append(
                f"Paragrafo {i}: aposto explicativo entre parênteses proibido — reescrever em frase própria."
            )
        if p.count('—') >= 2:
            problemas.append(
                f"Paragrafo {i}: aposto explicativo entre travessões proibido — reescrever em frase própria."
            )
    return problemas


def listar_dois_pontos(paragrafos):
    candidatos = []
    for i, p in enumerate(paragrafos):
        for s in _split_sentencas(p):
            if ':' in s:
                candidatos.append((i, s.strip()[:120]))
    return candidatos


def checar_aberturas_repetidas(paragrafos, minimo_palavras=4, limite=3):
    problemas = []
    aberturas = {}
    for i, p in enumerate(paragrafos):
        palavras = p.strip().split()
        if len(palavras) < minimo_palavras:
            continue
        chave = ' '.join(palavras[:minimo_palavras]).lower()
        aberturas.setdefault(chave, []).append(i)
    for chave, idxs in aberturas.items():
        if len(idxs) >= limite:
            problemas.append(
                f"Abertura repetida {limite}+ vezes ({chave!r}) nos paragrafos {idxs}."
            )
    return problemas


def checar(path):
    paragrafos = carregar_paragrafos(path)

    problemas = []
    trav_problemas, trav_candidatos = checar_travessao(paragrafos)
    problemas += trav_problemas
    problemas += checar_ponto_e_virgula(paragrafos)
    problemas += checar_tricolon_negacao(paragrafos)
    problemas += checar_aberturas_defensivas(paragrafos)
    problemas += checar_dois_pontos(paragrafos)
    problemas += checar_aposto_explicativo(paragrafos)
    problemas += checar_aberturas_repetidas(paragrafos)

    dois_pontos = listar_dois_pontos(paragrafos)

    return problemas, dois_pontos


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 verificar_estilo.py caminho/para/peca.docx", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    problemas, dois_pontos = checar(path)

    if problemas:
        print(f"[ERRO] {len(problemas)} problema(s) de cadencia/estilo em {path}:")
        for p in problemas:
            print(f"  - {p}")
    else:
        print(f"[OK] Nenhum item de contagem obrigatoria violado em {path}")

    aberturas_defensivas = listar_aberturas_defensivas(carregar_paragrafos(path))
    if aberturas_defensivas:
        print(f"\n[INFO] {len(aberturas_defensivas)} abertura(s) defensiva(s) identificada(s) para revisão funcional:")
        for i, formula, trecho in aberturas_defensivas:
            print(f"  - par.{i}: {formula} — {trecho}")

    print(f"\n[INFO] {len(dois_pontos)} sentenca(s) com dois-pontos encontradas:")
    for i, s in dois_pontos[:200]:
        print(f"  - par.{i}: {s}")

    sys.exit(1 if problemas else 0)


if __name__ == '__main__':
    main()

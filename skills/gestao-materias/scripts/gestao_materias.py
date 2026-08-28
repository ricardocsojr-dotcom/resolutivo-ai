#!/usr/bin/env python3
"""Organiza clientes, matérias (contencioso/consultivo) e fontes documentais
em C:\\Users\\ricar\\Resolutivo-Dados (ou RESOLUTIVO_DADOS_ROOT).

Nunca move nem apaga arquivo original: registrar-documento só copia. Não há
comando de exclusão — apagar é decisão manual do Ricardo no Explorer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

TIPOS_MATERIA = {"contencioso", "consultivo"}
RELEVANCIAS = {"alta", "media", "baixa"}
# Mesma normalização de matter_id usada em skills/revisor-rdaa/scripts/estado_rdaa.py
# (_safe_matter_id) — garante que o mesmo número de processo vire o mesmo
# identificador de pasta nos dois lados (.rdaa-run/<matter_id>/ e Resolutivo-Dados).
ID_INVALIDO = re.compile(r"[^A-Za-z0-9_.-]+")


class GestaoError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def erro(code: str, message: str) -> GestaoError:
    return GestaoError(code, message)


def root() -> Path:
    return Path(os.environ.get("RESOLUTIVO_DADOS_ROOT", r"C:\Users\ricar\OneDrive\Área de Trabalho\Resolutivo-Dados"))


def slug_cliente(nome: str) -> str:
    norm = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", norm).strip("-").lower()
    if not slug:
        raise erro("nome_cliente_invalido", f"Nome de cliente não gera um identificador válido: {nome!r}.")
    return slug


def slug_generico(texto: str) -> str:
    norm = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", norm).strip("-").lower()
    return slug or "entrega"


def sanitize_id(materia_id: str) -> str:
    limpo = ID_INVALIDO.sub("-", materia_id.strip()).strip("-")
    if not limpo:
        raise erro("id_materia_invalido", f"ID de matéria inválido: {materia_id!r}.")
    return limpo


def cliente_dir(nome_cliente: str) -> Path:
    return root() / "clientes" / slug_cliente(nome_cliente)


def materia_dir(nome_cliente: str, tipo: str, materia_id: str) -> Path:
    if tipo not in TIPOS_MATERIA:
        raise erro("tipo_invalido", f"Tipo de matéria deve ser 'contencioso' ou 'consultivo', recebido: {tipo!r}.")
    return cliente_dir(nome_cliente) / tipo / sanitize_id(materia_id)


def agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def exigir_materia(materia_path: Path) -> None:
    if not materia_path.is_dir():
        raise erro("materia_inexistente", f"Matéria não encontrada: {materia_path}. Rode nova-materia primeiro.")


def append_registro(materia_path: Path, texto: str) -> None:
    registro = materia_path / "REGISTRO.md"
    with registro.open("a", encoding="utf-8") as f:
        f.write(f"- [{agora()}] {texto}\n")


# ---------------------------------------------------------------- novo-cliente

def cmd_novo_cliente(args: argparse.Namespace) -> dict[str, Any]:
    destino = cliente_dir(args.nome)
    if destino.exists():
        raise erro("cliente_existente", f"Cliente já existe: {destino}.")
    destino.mkdir(parents=True)
    (destino / "CLIENTE.md").write_text(
        f"# Cliente: {args.nome}\n\n"
        f"Criado em: {agora()}\n\n"
        "## Contexto institucional\n\n"
        "[Preencher: natureza do negócio/relação, histórico relevante que não muda por matéria.]\n\n"
        "## Matérias\n\n"
        "(lista mantida manualmente conforme novas matérias são abertas em contencioso/ e consultivo/)\n",
        encoding="utf-8",
    )
    return {"status": "ok", "cliente": args.nome, "pasta": str(destino)}


# ---------------------------------------------------------------- nova-materia

TEMPLATE_CONTEXTO = """# Contexto — {cliente} / {tipo} / {materia_id}

Criado em: {data}

Narrativa livre da situação atual da matéria, entre peças. Fato, tese,
decisão e risco de uma peça em produção vivem em
`.rdaa-run/{materia_id}/matter_state.json` (Claude Code/Codex) — este
arquivo não duplica isso. Jurisprudência e tese consolidada vivem no
vault (ementário do Resolutivo), consultado automaticamente antes de
redigir peça B/A — este arquivo também não duplica isso.

## Situação atual

(o que mudou desde a última atualização, em prosa)

## Próximo passo

(ação concreta pendente, com responsável)
"""

TEMPLATE_PENDENCIAS = """# Pendências — {cliente} / {tipo} / {materia_id}

## Abertas

## Resolvidas
"""

TEMPLATE_REGISTRO = """# Registro — {cliente} / {tipo} / {materia_id}

Histórico cronológico factual do trabalho nesta matéria. Não editar
entradas antigas — só adicionar.

## Linha do tempo

- [{data}] Matéria criada.
"""

TEMPLATE_HANDOFF = """# Handoff — {cliente} / {tipo} / {materia_id}

Atualizado em: {data}

## Para a próxima IA que assumir esta matéria

### O que já foi feito

[preencher manualmente ou copiar pontos-chave de REGISTRO.md]

### Pendências abertas

(gerado automaticamente por `gerar-handoff` a partir de PENDENCIAS.md)

### Fontes relevantes

(gerado automaticamente por `gerar-handoff` a partir de fontes.json)

### Próximo passo

[preencher manualmente — copiar de CONTEXTO.md]

### Nível da peça e rota

(Nível C/B/A definido por Ricardo — ver CLAUDE.md do escritório para quem faz o quê)
"""


def cmd_nova_materia(args: argparse.Namespace) -> dict[str, Any]:
    if not cliente_dir(args.cliente).is_dir():
        raise erro("cliente_inexistente", f"Cliente não encontrado: {args.cliente}. Rode novo-cliente primeiro.")
    destino = materia_dir(args.cliente, args.tipo, args.id)
    if destino.exists():
        raise erro("materia_existente", f"Matéria já existe: {destino}.")
    for sub in ("documentos/01-fontes", "trabalho", "entregas"):
        (destino / sub).mkdir(parents=True)
    ctx = {"cliente": args.cliente, "tipo": args.tipo, "materia_id": args.id, "data": agora()}
    (destino / "CONTEXTO.md").write_text(TEMPLATE_CONTEXTO.format(**ctx), encoding="utf-8")
    (destino / "PENDENCIAS.md").write_text(TEMPLATE_PENDENCIAS.format(**ctx), encoding="utf-8")
    (destino / "REGISTRO.md").write_text(TEMPLATE_REGISTRO.format(**ctx), encoding="utf-8")
    (destino / "HANDOFF.md").write_text(TEMPLATE_HANDOFF.format(**ctx), encoding="utf-8")
    (destino / "FONTES.md").write_text(f"# Fontes — {args.cliente} / {args.tipo} / {args.id}\n\n(sem documentos registrados)\n", encoding="utf-8")
    (destino / "fontes.json").write_text("[]\n", encoding="utf-8")
    return {"status": "ok", "materia": args.id, "pasta": str(destino)}


# ---------------------------------------------------------------- registrar-documento

def render_fontes_md(cliente: str, tipo: str, materia_id: str, fontes: list[dict[str, Any]]) -> str:
    linhas = [f"# Fontes — {cliente} / {tipo} / {materia_id}", ""]
    if not fontes:
        linhas.append("(sem documentos registrados)")
        return "\n".join(linhas) + "\n"
    linhas.append("| ID | Arquivo | Tipo | Origem | Função | Relevância | Páginas | Tags | Registrado em |")
    linhas.append("|---|---|---|---|---|---|---|---|---|")
    for f in fontes:
        tags = ", ".join(f["tags"])
        linhas.append(
            f"| {f['id']} | {f['arquivo']} | {f['doc_tipo']} | {f['origem']} | {f['funcao']} | "
            f"{f['relevancia']} | {f['paginas']} | {tags} | {f['registrado_em']} |"
        )
    return "\n".join(linhas) + "\n"


def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def cmd_registrar_documento(args: argparse.Namespace) -> dict[str, Any]:
    m_dir = materia_dir(args.cliente, args.tipo, args.id)
    exigir_materia(m_dir)

    origem_arquivo = Path(args.arquivo).resolve()
    if not origem_arquivo.is_file():
        raise erro("arquivo_inexistente", f"Arquivo não encontrado: {origem_arquivo}.")

    fontes_json = m_dir / "fontes.json"
    fontes = json.loads(fontes_json.read_text(encoding="utf-8"))
    novo_num = len(fontes) + 1
    doc_id = f"DOC-{novo_num:03d}"

    doc_dir = m_dir / "documentos" / "01-fontes"
    try:
        dentro_da_pasta = origem_arquivo.is_relative_to(doc_dir.resolve())
    except AttributeError:  # Python < 3.9 fallback, não deve ocorrer aqui
        dentro_da_pasta = str(origem_arquivo).startswith(str(doc_dir.resolve()))

    if dentro_da_pasta:
        nome_relativo = origem_arquivo.name
    else:
        nome_relativo = f"{doc_id}__{origem_arquivo.name}"
        shutil.copy2(origem_arquivo, doc_dir / nome_relativo)

    caminho_final = doc_dir / nome_relativo
    registro = {
        "id": doc_id,
        "arquivo": nome_relativo,
        "doc_tipo": args.doc_tipo,
        "origem": args.origem,
        "funcao": args.funcao,
        "relevancia": args.relevancia or "",
        "paginas": args.paginas or "",
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else [],
        "sha256": sha256_arquivo(caminho_final),
        "tamanho_bytes": caminho_final.stat().st_size,
        "registrado_em": agora(),
    }
    fontes.append(registro)
    fontes_json.write_text(json.dumps(fontes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (m_dir / "FONTES.md").write_text(render_fontes_md(args.cliente, args.tipo, args.id, fontes), encoding="utf-8")
    append_registro(m_dir, f"Documento {doc_id} registrado ({nome_relativo}).")
    return {"status": "ok", "id": doc_id, "arquivo": nome_relativo, "sha256": registro["sha256"]}


# ---------------------------------------------------------------- verificar-documentos

def cmd_verificar_documentos(args: argparse.Namespace) -> dict[str, Any]:
    m_dir = materia_dir(args.cliente, args.tipo, args.id)
    exigir_materia(m_dir)
    fontes = json.loads((m_dir / "fontes.json").read_text(encoding="utf-8"))
    doc_dir = m_dir / "documentos" / "01-fontes"
    ok, alterados, ausentes = [], [], []
    for f in fontes:
        caminho = doc_dir / f["arquivo"]
        if not caminho.is_file():
            ausentes.append(f["id"])
            continue
        if sha256_arquivo(caminho) != f["sha256"]:
            alterados.append(f["id"])
        else:
            ok.append(f["id"])
    status = "ok" if not alterados and not ausentes else "divergencia"
    return {"status": status, "ok": ok, "alterados": alterados, "ausentes": ausentes}


# ---------------------------------------------------------------- pendências

def cmd_abrir_pendencia(args: argparse.Namespace) -> dict[str, Any]:
    m_dir = materia_dir(args.cliente, args.tipo, args.id)
    exigir_materia(m_dir)
    pend_path = m_dir / "PENDENCIAS.md"
    texto = pend_path.read_text(encoding="utf-8")
    existentes = re.findall(r"PEND-(\d+)", texto)
    pend_id = f"PEND-{(max(int(n) for n in existentes) + 1) if existentes else 1:03d}"
    linha = f"- [ ] **{pend_id}** ({agora()}): {args.descricao}\n"
    texto = texto.replace("## Abertas\n", f"## Abertas\n{linha}", 1) if "## Abertas\n" in texto else texto + linha
    pend_path.write_text(texto, encoding="utf-8")
    append_registro(m_dir, f"Pendência {pend_id} aberta: {args.descricao}")
    return {"status": "ok", "id": pend_id}


def cmd_resolver_pendencia(args: argparse.Namespace) -> dict[str, Any]:
    m_dir = materia_dir(args.cliente, args.tipo, args.id)
    exigir_materia(m_dir)
    pend_path = m_dir / "PENDENCIAS.md"
    texto = pend_path.read_text(encoding="utf-8")
    padrao = re.compile(rf"- \[ \] \*\*{re.escape(args.pendencia)}\*\*.*")
    match = padrao.search(texto)
    if not match:
        raise erro("pendencia_nao_encontrada", f"Pendência aberta não encontrada: {args.pendencia}.")
    linha_original = match.group(0)
    linha_resolvida = linha_original.replace("- [ ]", "- [x]", 1) + f" → Resolução ({agora()}): {args.resolucao}"
    texto = texto.replace(linha_original, "", 1)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    if "## Resolvidas\n" in texto:
        texto = texto.replace("## Resolvidas\n", f"## Resolvidas\n{linha_resolvida}\n", 1)
    else:
        texto += f"\n## Resolvidas\n{linha_resolvida}\n"
    pend_path.write_text(texto, encoding="utf-8")
    append_registro(m_dir, f"Pendência {args.pendencia} resolvida: {args.resolucao}")
    return {"status": "ok", "id": args.pendencia}


# ---------------------------------------------------------------- gerar-handoff

def substituir_secao(texto: str, cabecalho: str, novo_conteudo: str) -> str:
    padrao = re.compile(rf"(### {re.escape(cabecalho)}\n)(.*?)(?=\n### |\Z)", re.DOTALL)
    if not padrao.search(texto):
        raise erro("secao_nao_encontrada", f"Seção '### {cabecalho}' não encontrada em HANDOFF.md.")
    return padrao.sub(lambda m: m.group(1) + novo_conteudo + "\n", texto, count=1)


def cmd_gerar_handoff(args: argparse.Namespace) -> dict[str, Any]:
    m_dir = materia_dir(args.cliente, args.tipo, args.id)
    exigir_materia(m_dir)

    pend_texto = (m_dir / "PENDENCIAS.md").read_text(encoding="utf-8")
    abertas = re.findall(r"- \[ \] \*\*PEND-\d+\*\*.*", pend_texto)
    bloco_pendencias = "\n".join(abertas) if abertas else "(nenhuma pendência aberta)"

    fontes = json.loads((m_dir / "fontes.json").read_text(encoding="utf-8"))
    relevantes = [f for f in fontes if f["relevancia"] == "alta"] or fontes  # sem classificação: lista tudo
    bloco_fontes = "\n".join(f"- {f['id']}: {f['arquivo']} ({f['funcao']}, p.{f['paginas'] or '?'})" for f in relevantes) or "(sem documentos registrados)"

    handoff_path = m_dir / "HANDOFF.md"
    texto = handoff_path.read_text(encoding="utf-8")
    texto = re.sub(r"Atualizado em: .*", f"Atualizado em: {agora()}", texto, count=1)
    texto = substituir_secao(texto, "Pendências abertas", bloco_pendencias)
    texto = substituir_secao(texto, "Fontes relevantes", bloco_fontes)
    handoff_path.write_text(texto, encoding="utf-8")
    append_registro(m_dir, "HANDOFF.md atualizado (pendências e fontes).")
    return {"status": "ok", "pendencias_abertas": len(abertas), "fontes_listadas": len(relevantes)}


# ---------------------------------------------------------------- montar-entrega

def cmd_montar_entrega(args: argparse.Namespace) -> dict[str, Any]:
    m_dir = materia_dir(args.cliente, args.tipo, args.id)
    exigir_materia(m_dir)

    peca = Path(args.arquivo).resolve()
    if not peca.is_file():
        raise erro("arquivo_inexistente", f"Arquivo da entrega não encontrado: {peca}.")

    fontes = json.loads((m_dir / "fontes.json").read_text(encoding="utf-8"))
    fontes_por_id = {f["id"]: f for f in fontes}
    anexo_ids = [a.strip() for a in args.anexos.split(",") if a.strip()] if args.anexos else []
    faltando = [a for a in anexo_ids if a not in fontes_por_id]
    if faltando:
        raise erro("documento_nao_encontrado", f"Anexo(s) não registrado(s) em fontes.json: {', '.join(faltando)}.")

    rotulo = slug_generico(args.rotulo or peca.stem)
    entregas_dir = m_dir / "entregas"
    data_pasta = datetime.now().strftime("%Y-%m-%d")
    nome_pasta = f"{data_pasta}_{rotulo}"
    destino = entregas_dir / nome_pasta
    sufixo = 2
    while destino.exists():
        destino = entregas_dir / f"{nome_pasta}-{sufixo}"
        sufixo += 1
    destino.mkdir(parents=True)

    shutil.copy2(peca, destino / peca.name)
    peca_sha = sha256_arquivo(destino / peca.name)

    anexos_info: list[dict[str, str]] = []
    if anexo_ids:
        anexos_dir = destino / "anexos"
        anexos_dir.mkdir()
        doc_dir = m_dir / "documentos" / "01-fontes"
        for doc_id in anexo_ids:
            f = fontes_por_id[doc_id]
            origem_anexo = doc_dir / f["arquivo"]
            if not origem_anexo.is_file():
                raise erro("anexo_ausente_no_disco", f"Documento {doc_id} está registrado mas o arquivo não existe em disco: {origem_anexo}.")
            shutil.copy2(origem_anexo, anexos_dir / f["arquivo"])
            anexos_info.append({"id": doc_id, "arquivo": f["arquivo"], "funcao": f["funcao"]})

    manifesto = [
        f"# Entrega — {args.cliente} / {args.tipo} / {args.id}",
        "",
        f"Montada em: {agora()}",
        f"Rótulo: {args.rotulo or peca.stem}",
        "",
        "## Peça final",
        "",
        f"- Arquivo: {peca.name}",
        f"- SHA-256: {peca_sha}",
        "",
        "## Anexos",
        "",
    ]
    if anexos_info:
        manifesto += [f"- {a['id']}: {a['arquivo']} ({a['funcao']})" for a in anexos_info]
    else:
        manifesto.append("(nenhum anexo incluído)")
    manifesto.append("")
    (destino / "MANIFESTO.md").write_text("\n".join(manifesto), encoding="utf-8")

    append_registro(
        m_dir,
        f"Entrega montada: {args.rotulo or peca.stem} → entregas/{destino.name} "
        f"(peça + {len(anexos_info)} anexo(s)).",
    )
    return {
        "status": "ok",
        "pasta": str(destino),
        "peca": peca.name,
        "sha256": peca_sha,
        "anexos": anexos_info,
    }


# ---------------------------------------------------------------- limpar-trabalho

def cmd_limpar_trabalho(args: argparse.Namespace) -> dict[str, Any]:
    m_dir = materia_dir(args.cliente, args.tipo, args.id)
    exigir_materia(m_dir)

    trabalho_dir = m_dir / "trabalho"
    itens = sorted(trabalho_dir.rglob("*"))
    arquivos = [p for p in itens if p.is_file()]
    tamanho_total = sum(p.stat().st_size for p in arquivos)

    if not args.confirmar:
        return {
            "status": "confirmacao_necessaria",
            "arquivos": [str(p.relative_to(trabalho_dir)) for p in arquivos],
            "total_arquivos": len(arquivos),
            "tamanho_bytes": tamanho_total,
            "mensagem": "Nada foi apagado. Rode de novo com --confirmar para limpar de fato.",
        }

    aviso = None
    entregas_dir = m_dir / "entregas"
    if not any(entregas_dir.iterdir()):
        aviso = "trabalho limpo sem nenhuma entrega registrada ainda em entregas/ — confirme que isso era intencional."

    for item in sorted(trabalho_dir.iterdir()):
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    append_registro(m_dir, f"Trabalho limpo: {len(arquivos)} arquivo(s) removido(s) ({tamanho_total} bytes).")
    resultado: dict[str, Any] = {
        "status": "ok",
        "arquivos_removidos": len(arquivos),
        "tamanho_bytes": tamanho_total,
    }
    if aviso:
        resultado["aviso"] = aviso
    return resultado


# ---------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Gestão de clientes e matérias em Resolutivo-Dados")
    sub = p.add_subparsers(dest="comando", required=True)

    sp = sub.add_parser("novo-cliente")
    sp.add_argument("--nome", required=True)
    sp.set_defaults(func=cmd_novo_cliente)

    sp = sub.add_parser("nova-materia")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True, help="Número do processo (contencioso) ou ID do projeto (consultivo)")
    sp.set_defaults(func=cmd_nova_materia)

    sp = sub.add_parser("registrar-documento")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True)
    sp.add_argument("--arquivo", required=True)
    sp.add_argument("--doc-tipo", required=True, help="ex.: peticao-inicial, contrato, laudo, print, ata")
    sp.add_argument("--origem", required=True, help="ex.: cliente, autos, terceiro, interno")
    sp.add_argument("--funcao", required=True, help="ex.: prova, fundamentacao, referencia")
    sp.add_argument("--relevancia", required=False, default=None, choices=sorted(RELEVANCIAS))
    sp.add_argument("--tags", default="", help="lista separada por vírgula")
    sp.add_argument("--paginas", default="", help="ex.: 1-4,7")
    sp.set_defaults(func=cmd_registrar_documento)

    sp = sub.add_parser("verificar-documentos")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True)
    sp.set_defaults(func=cmd_verificar_documentos)

    sp = sub.add_parser("abrir-pendencia")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True)
    sp.add_argument("--descricao", required=True)
    sp.set_defaults(func=cmd_abrir_pendencia)

    sp = sub.add_parser("resolver-pendencia")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True)
    sp.add_argument("--pendencia", required=True, help="ID no formato PEND-XXX")
    sp.add_argument("--resolucao", required=True)
    sp.set_defaults(func=cmd_resolver_pendencia)

    sp = sub.add_parser("gerar-handoff")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True)
    sp.set_defaults(func=cmd_gerar_handoff)

    sp = sub.add_parser("montar-entrega")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True)
    sp.add_argument("--arquivo", required=True, help="Peça/documento final já pronto para entrega")
    sp.add_argument("--rotulo", default="", help="Nome curto da entrega (ex.: recurso-apelacao); default: nome do arquivo")
    sp.add_argument("--anexos", default="", help="Lista de DOC-XXX de fontes.json a incluir junto, separada por vírgula")
    sp.set_defaults(func=cmd_montar_entrega)

    sp = sub.add_parser("limpar-trabalho")
    sp.add_argument("--cliente", required=True)
    sp.add_argument("--tipo", required=True, choices=sorted(TIPOS_MATERIA))
    sp.add_argument("--id", required=True)
    sp.add_argument("--confirmar", action="store_true", help="Sem isso, só lista o que seria apagado (dry-run)")
    sp.set_defaults(func=cmd_limpar_trabalho)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        resultado = args.func(args)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0 if resultado.get("status") in ("ok",) else 1
    except GestaoError as exc:
        print(json.dumps({"status": "erro", "codigo": exc.code, "mensagem": exc.message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Self-check do fluxo completo. Rodar: python test_gestao_materias.py
Usa uma pasta temporária via RESOLUTIVO_DADOS_ROOT — não toca dados reais.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import gestao_materias as gm


def run() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        gm.os.environ["RESOLUTIVO_DADOS_ROOT"] = tmp
        parser = gm.build_parser()

        def call(argv: list[str]) -> dict:
            return parser.parse_args(argv).func(parser.parse_args(argv))

        r = call(["novo-cliente", "--nome", "Cliente Teste"])
        assert r["status"] == "ok", r
        cliente_dir = Path(r["pasta"])
        assert (cliente_dir / "CLIENTE.md").is_file()

        r = call(["nova-materia", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste"])
        assert r["status"] == "ok", r
        materia_dir = Path(r["pasta"])
        for nome in ("CONTEXTO.md", "PENDENCIAS.md", "REGISTRO.md", "HANDOFF.md", "FONTES.md", "fontes.json"):
            assert (materia_dir / nome).is_file(), nome

        origem = Path(tmp) / "peticao.txt"
        origem.write_text("conteudo original", encoding="utf-8")
        r = call([
            "registrar-documento", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste",
            "--arquivo", str(origem), "--doc-tipo", "peticao-inicial", "--origem", "autos",
            "--funcao", "prova", "--tags", "chave,contrato", "--paginas", "1-3",
        ])
        assert r["status"] == "ok" and r["id"] == "DOC-001", r
        assert origem.is_file(), "arquivo original não pode ser removido"
        fontes = json.loads((materia_dir / "fontes.json").read_text(encoding="utf-8"))
        assert fontes[0]["relevancia"] == "", "sem --relevancia deve gravar vazio, não erro"
        assert len(fontes) == 1 and fontes[0]["id"] == "DOC-001"

        r = call(["verificar-documentos", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste"])
        assert r["status"] == "ok" and r["ok"] == ["DOC-001"], r

        copiado = materia_dir / "documentos" / "01-fontes" / "DOC-001__peticao.txt"
        copiado.write_text("alterado!", encoding="utf-8")
        r = call(["verificar-documentos", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste"])
        assert r["status"] == "divergencia" and r["alterados"] == ["DOC-001"], r

        r = call(["abrir-pendencia", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste", "--descricao", "confirmar valor da causa"])
        assert r["status"] == "ok" and r["id"] == "PEND-001", r
        pend_texto = (materia_dir / "PENDENCIAS.md").read_text(encoding="utf-8")
        assert "PEND-001" in pend_texto and "confirmar valor da causa" in pend_texto

        r = call(["resolver-pendencia", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste", "--pendencia", "PEND-001", "--resolucao", "confirmado com o cliente"])
        assert r["status"] == "ok", r
        pend_texto = (materia_dir / "PENDENCIAS.md").read_text(encoding="utf-8")
        assert "- [x] **PEND-001**" in pend_texto
        assert "## Abertas\n\n## Resolvidas" in pend_texto or "## Abertas\n## Resolvidas" not in pend_texto

        r = call(["gerar-handoff", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste"])
        assert r["status"] == "ok" and r["fontes_listadas"] == 1, r
        handoff = (materia_dir / "HANDOFF.md").read_text(encoding="utf-8")
        assert "DOC-001" in handoff
        assert "nenhuma pendência aberta" in handoff

        peca_final = Path(tmp) / "recurso.txt"
        peca_final.write_text("peça final pronta", encoding="utf-8")
        r = call([
            "montar-entrega", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste",
            "--arquivo", str(peca_final), "--rotulo", "recurso-apelacao", "--anexos", "DOC-001",
        ])
        assert r["status"] == "ok" and r["peca"] == "recurso.txt" and len(r["anexos"]) == 1, r
        entrega_dir = Path(r["pasta"])
        assert (entrega_dir / "recurso.txt").is_file()
        assert (entrega_dir / "anexos" / "DOC-001__peticao.txt").is_file()
        assert (entrega_dir / "MANIFESTO.md").is_file()
        assert peca_final.is_file(), "arquivo de origem da entrega não pode ser removido"

        try:
            call([
                "montar-entrega", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste",
                "--arquivo", str(peca_final), "--anexos", "DOC-999",
            ])
            raise AssertionError("anexo inexistente deveria falhar")
        except gm.GestaoError as exc:
            assert exc.code == "documento_nao_encontrado", exc.code

        r = call(["limpar-trabalho", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste"])
        assert r["status"] == "confirmacao_necessaria" and r["arquivos"] == [], r

        rascunho = materia_dir / "trabalho" / "minuta-v1.txt"
        rascunho.write_text("rascunho", encoding="utf-8")
        r = call(["limpar-trabalho", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste"])
        assert r["status"] == "confirmacao_necessaria" and r["arquivos"] == ["minuta-v1.txt"], r
        assert rascunho.is_file(), "dry-run não pode apagar nada"

        r = call(["limpar-trabalho", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0001-teste", "--confirmar"])
        assert r["status"] == "ok" and r["arquivos_removidos"] == 1, r
        assert "aviso" not in r, "já existe entrega montada, não deveria avisar"
        assert not rascunho.is_file()
        assert (materia_dir / "trabalho").is_dir(), "a pasta trabalho/ em si deve continuar existindo"

        r = call(["nova-materia", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0002-sem-entrega"])
        materia_dir_2 = Path(r["pasta"])
        (materia_dir_2 / "trabalho" / "algo.txt").write_text("x", encoding="utf-8")
        r = call(["limpar-trabalho", "--cliente", "Cliente Teste", "--tipo", "contencioso", "--id", "0002-sem-entrega", "--confirmar"])
        assert r["status"] == "ok" and "aviso" in r, r

    print("ok — todos os checks passaram")


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""Self-check com relatório sintético mínimo, cobrindo os dois formatos de
bloco (Workspace e Matéria) e a extração de tamanho/alertas.
Rodar: python test_gerar_planilha_importacao.py
"""

from __future__ import annotations

from gerar_planilha_importacao import dividir_blocos, parse_bloco

RELATORIO_FALSO = """\
## 2. PROJETOS

### 2.1 Workspace: `Caso Teste`
- **Cliente Identificado**: `CLIENTE TESTE LTDA`
- **Grau de Confiança**: Alto (motivo)
- **Classificação Resolutivo-Dados**: `CLIENTE TESTE LTDA > contencioso > 0001234-56.2024.8.13.0000`
- **Tipo de Matéria**: Contestação | **Fase**: Fase de Conhecimento
- **Peça Principal Escolhida**: `peticao.pdf`
- **Total de Arquivos**: 12
- Anexo: `laudo.pdf` (Laudo Técnico - 1500.0 KB)
- Anexo: `volume.pdf` (23.50 MB)
- *[PONTO A CONFERIR]* Procuração não localizada.

## 3. LOTES

##### Matéria: `Agosto\\Manifestação Simples`
- **Cliente Identificado**: `OUTRO CLIENTE`
- **Grau de Confiança**: Médio (motivo)
- **Processo / Projeto**: `Sem número CNJ identificado nos documentos locais`
- **Classificação Sugerida**: `OUTRO CLIENTE > consultivo > Sem número CNJ identificado nos documentos locais`
- **Tipo de Matéria**: Manifestação Processual | **Fase**: Fase de Conhecimento
- **Peça Principal**: `manifestacao.docx`
- **Total de Arquivos**: 2
"""


def run() -> None:
    blocos = dividir_blocos(RELATORIO_FALSO)
    assert len(blocos) == 2, f"esperado 2 blocos, veio {len(blocos)}"

    r1 = parse_bloco(blocos[0])
    assert r1["origem"] == "Caso Teste", r1
    assert r1["cliente_sugerido"] == "CLIENTE TESTE LTDA", r1
    assert r1["confianca"] == "alta", r1
    assert r1["tipo_sugerido"] == "contencioso", r1
    assert r1["id_sugerido"] == "0001234-56.2024.8.13.0000", r1
    assert r1["tipo_de_peca"] == "Contestação", r1
    assert r1["peca_principal"] == "peticao.pdf", r1
    assert r1["total_arquivos"] == "12", r1
    assert r1["maior_anexo_mb"] == "23.50", r1  # 23.50 MB > 1500 KB (1.46 MB)
    assert "Procuração não localizada" in r1["alertas_do_relatorio"], r1
    assert r1["cliente_final"] == r1["cliente_sugerido"], r1
    assert r1["importar"] == "", r1

    r2 = parse_bloco(blocos[1])
    assert r2["origem"] == "Agosto\\Manifestação Simples", r2
    assert r2["cliente_sugerido"] == "OUTRO CLIENTE", r2
    assert r2["confianca"] == "media", r2
    assert r2["tipo_sugerido"] == "consultivo", r2
    assert r2["id_sugerido"] == "Sem número CNJ identificado nos documentos locais", r2
    assert r2["maior_anexo_mb"] == "", r2
    assert r2["alertas_do_relatorio"] == "", r2

    print("ok — todos os checks passaram")


if __name__ == "__main__":
    run()

"""Registro de Recursos (MCP Resources) para disponibilização de normas, manuais e checklists."""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def _read_file_or_fallback(rel_path: str, fallback_text: str = "") -> str:
    path = PROJECT_ROOT / rel_path
    if path.is_file():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            pass
    return fallback_text

def register_resources(mcp: FastMCP) -> None:
    """Registra os recursos estáticos e normativos do Resolutivo.AI no FastMCP."""

    @mcp.resource("rdaa://perfil/escritorio")
    def get_perfil_escritorio() -> str:
        """Perfil, identidade institucional e governança do escritório RDAA."""
        return _read_file_or_fallback("CLAUDE.md", "Perfil do escritório Romano Donadel Advogados Associados (RDAA).")

    @mcp.resource("rdaa://regras/redacao")
    def get_regras_redacao() -> str:
        """Núcleo Único de Escrita e normas canônicas de redação forense do RDAA."""
        return _read_file_or_fallback(
            "skills/contencioso-rdaa/references/redacao-rdaa.md",
            "Diretrizes de redação forense: linguagem direta, sem arcaísmos, tese na primeira frase."
        )

    @mcp.resource("rdaa://checklists/revisao/juridico")
    def get_checklist_juridico() -> str:
        """Checklist 1 — Critérios Jurídicos, Estratégicos e Processuais."""
        return _read_file_or_fallback(
            "skills/revisor-rdaa/references/checklist-1-juridico.md",
            "Checklist de conformidade jurídica, tempestividade e pedidos em cascata."
        )

    @mcp.resource("rdaa://checklists/revisao/visual")
    def get_checklist_visual() -> str:
        """Checklist 2 — Padrões Visuais, Formatação e Visual Law."""
        return _read_file_or_fallback(
            "skills/revisor-rdaa/references/checklist-2-visual.md",
            "Checklist de formatação visual, tipografia e títulos sem preposições."
        )

    @mcp.resource("rdaa://checklists/revisao/estilometria")
    def get_checklist_estilometria() -> str:
        """Checklist 3 — Estilometria, Cadência e Eliminação de Vícios de Linguagem."""
        return _read_file_or_fallback(
            "skills/revisor-rdaa/references/checklist-3-estilometria.md",
            "Checklist estilométrico: proibição de travessões, controle de pontuação e aberturas defensivas."
        )

    @mcp.resource("rdaa://provisao/metodologia")
    def get_metodologia_provisao() -> str:
        """Metodologia de análise de risco e provisionamento contábil (CPC 25 / NBC TG 25)."""
        return _read_file_or_fallback(
            "skills/analise-provisao-rdaa/references/metodologia-provisao.md",
            "Metodologia da árvore de risco (Provável, Possível, Remoto) e double-check de contingência."
        )

    @mcp.resource("rdaa://indices/manifest")
    def get_manifesto_indices() -> str:
        """Manifesto oficial com índices de correção monetária aprovados no motor de cálculo."""
        return _read_file_or_fallback(
            "skills/calculo-judicial/references/index_manifest.json",
            "{}"
        )

    @mcp.resource("rdaa://slide-style/guia")
    def get_guia_slides() -> str:
        """Guia de estilo e identidade visual de apresentações do RDAA."""
        return _read_file_or_fallback(
            "skills/romano-donadel-slide-style/references/identidade-visual-extraida.md",
            "Identidade visual, paleta de cores institucional e tipografia para slides."
        )

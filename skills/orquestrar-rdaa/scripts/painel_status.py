#!/usr/bin/env python3
"""Gera um painel HTML local e estático para uma matéria RDAA."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


ENGINE_NAMES = {"codex": "Codex", "claude": "Claude", "antigravity": "Antigravity"}


def _text(value: Any) -> str:
    return html.escape(str(value if value is not None else "—"))


def _duration(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "—"
    seconds = value / 1000
    return f"{seconds:.2f}".replace(".", ",") + " s"


def _items(items: list[dict[str, Any]], renderer) -> str:
    if not items:
        return '<li class="muted">Nenhum registro.</li>'
    return "".join(renderer(item) for item in items)


def _execution_item(item: dict[str, Any]) -> str:
    models = item.get("model_ids") or []
    model_text = ", ".join(str(model) for model in models) if models else "modelo não informado"
    return (
        f'<li><strong>{_text(item.get("role"))}</strong> · '
        f'{_text(ENGINE_NAMES.get(item.get("motor"), item.get("motor")))} · '
        f'{_text(model_text)} · {_duration(item.get("duration_ms"))}</li>'
    )


def _vault_lookup_item(item: dict[str, Any]) -> str:
    return (
        f'<li><strong>{_text(item.get("vault"))}</strong> · domínio {_text(item.get("domain"))} · '
        f'{_text(item.get("documents_count"))} documentos · {_text(item.get("status"))}</li>'
    )


def _vault_sync_item(item: dict[str, Any]) -> str:
    return f'<li><strong>{_text(item.get("vault"))}</strong> · {_text(item.get("status"))} · {_text(item.get("recorded_at"))}</li>'


def render_panel(manifest: dict[str, Any]) -> str:
    route = manifest.get("route") or {}
    approvals = manifest.get("approvals") or []
    executions = manifest.get("executions") or []
    transitions = manifest.get("transitions") or []
    vault = manifest.get("vault") or {}

    approval_html = _items(
        approvals,
        lambda item: f'<li><strong>{_text(item.get("gate"))}</strong> · {_text(item.get("approved_by"))} · {_text(item.get("approved_at"))}</li>',
    )
    execution_html = _items(executions, _execution_item)
    vault_lookup_html = _items(vault.get("lookups") or [], _vault_lookup_item)
    vault_sync_html = _items(vault.get("syncs") or [], _vault_sync_item)
    transition_html = _items(
        transitions,
        lambda item: f'<li><strong>{_text(item.get("to"))}</strong> · {_text(item.get("at"))}</li>',
    )

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>RDAA · {_text(manifest.get('matter_id'))}</title>
<style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
body {{ max-width: 980px; margin: 28px auto; padding: 0 22px; color: CanvasText; background: Canvas; }}
h1 {{ margin-bottom: 4px; }} .muted {{ color: GrayText; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin:20px 0; }}
.card {{ border:1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius:12px; padding:14px; }}
.label {{ color:GrayText; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em; }}
.value {{ font-size:1.1rem; font-weight:700; margin-top:5px; word-break:break-word; }}
section {{ margin-top:26px; }} ul {{ line-height:1.7; padding-left:20px; }}
</style></head><body>
<h1>Matéria {_text(manifest.get('matter_id'))}</h1>
<p class="muted">Atualizado: {_text(manifest.get('updated_at'))}</p>
<div class="grid">
  <div class="card"><div class="label">Etapa</div><div class="value">{_text(manifest.get('phase'))}</div></div>
  <div class="card"><div class="label">Estado</div><div class="value">{_text(manifest.get('status'))}</div></div>
  <div class="card"><div class="label">Nível</div><div class="value">{_text(route.get('declared_piece_level'))} → {_text(route.get('effective_piece_level'))}</div></div>
  <div class="card"><div class="label">Risco</div><div class="value">{_text(route.get('risk_level'))}</div></div>
</div>
<section><h2>Aprovações</h2><ul>{approval_html}</ul></section>
<section><h2>Execuções</h2><ul>{execution_html}</ul></section>
<section><h2>Ementário / Obsidian</h2><h3>Consulta read-only</h3><ul>{vault_lookup_html}</ul><h3>Registros pós-publicação</h3><ul>{vault_sync_html}</ul></section>
<section><h2>Histórico</h2><ul>{transition_html}</ul></section>
</body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera painel HTML da matéria RDAA")
    parser.add_argument("state_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.state_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_panel(manifest), encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

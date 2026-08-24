#!/usr/bin/env python3
"""Operações locais de backup e rollback para artefatos RDAA.

Não usa rede nem serviço externo. A substituição só ocorre depois que o
arquivo novo existe; o backup anterior permanece disponível para restauração.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def criar_backup(arquivo: Path, pasta_backup: Path) -> Path:
    arquivo = Path(arquivo)
    pasta_backup = Path(pasta_backup)
    if not arquivo.is_file():
        raise FileNotFoundError(f"Arquivo estável não encontrado: {arquivo}")
    pasta_backup.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destino = pasta_backup / f"{arquivo.name}.{stamp}.bak"
    shutil.copy2(arquivo, destino)
    return destino


def _copiar_atomico(origem: Path, destino: Path) -> None:
    """Copia origem para destino via arquivo temporário + replace atômico,
    para que uma interrupção no meio da cópia nunca deixe destino truncado."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{destino.name}.",
        suffix=".tmp",
        dir=destino.parent,
        delete=False,
    ) as tmp:
        temporario = Path(tmp.name)
    try:
        shutil.copy2(origem, temporario)
        temporario.replace(destino)
    except Exception:
        temporario.unlink(missing_ok=True)
        raise


def substituir_com_backup(novo: Path, destino: Path, pasta_backup: Path) -> Path | None:
    novo = Path(novo)
    destino = Path(destino)
    if not novo.is_file():
        raise FileNotFoundError(f"Novo arquivo não encontrado: {novo}")

    backup = criar_backup(destino, pasta_backup) if destino.exists() else None
    _copiar_atomico(novo, destino)
    return backup


def restaurar(backup: Path, destino: Path) -> None:
    backup = Path(backup)
    destino = Path(destino)
    if not backup.is_file():
        raise FileNotFoundError(f"Backup não encontrado: {backup}")
    _copiar_atomico(backup, destino)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup e rollback local do RDAA")
    sub = parser.add_subparsers(dest="command", required=True)

    p_backup = sub.add_parser("backup")
    p_backup.add_argument("arquivo", type=Path)
    p_backup.add_argument("pasta_backup", type=Path)

    p_replace = sub.add_parser("replace")
    p_replace.add_argument("novo", type=Path)
    p_replace.add_argument("destino", type=Path)
    p_replace.add_argument("pasta_backup", type=Path)

    p_restore = sub.add_parser("restore")
    p_restore.add_argument("backup", type=Path)
    p_restore.add_argument("destino", type=Path)

    args = parser.parse_args()
    if args.command == "backup":
        print(criar_backup(args.arquivo, args.pasta_backup))
    elif args.command == "replace":
        backup = substituir_com_backup(args.novo, args.destino, args.pasta_backup)
        print(f"backup={backup or 'nenhum'}")
    else:
        restaurar(args.backup, args.destino)
        print(f"restaurado={args.destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

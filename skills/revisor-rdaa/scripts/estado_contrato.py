import json
import re
from pathlib import Path


class EstadoDirError(ValueError):
    pass


class MatterId:
    @staticmethod
    def normalize(value: str | None) -> str:
        if not value:
            return "sem-identificador"
        value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
        return value.strip("-") or "sem-identificador"


def validar_state_dir(state_dir: Path, matter_id: str | None = None) -> None:
    """Verifica se o diretorio de estado obedece ao contrato de canonicalizacao.
    
    Validacoes:
    1. Nao pode conter '.rdaa-run' mais de uma vez no caminho (aninhado).
    2. Nao pode ser um symlink externo disfarçado de diretório.
    3. Se houver matter_id e manifesto pré-existente, o matter_id do manifesto
       nao pode divergir silenciosamente do matter_id informado para a operacao.
    """
    resolved = state_dir.resolve()

    # 1. Checagem de aninhamento
    occurrences = sum(1 for part in resolved.parts if part.casefold() == ".rdaa-run")
    if occurrences > 1:
        # A mensagem MANTEM a substring 'aninhado' explicitamente exigida no contrato
        raise EstadoDirError(f"Caminho state_dir aninhado invalido ('.rdaa-run' repetido): {state_dir}")

    # 2. Symlink
    # Queremos checar o proprio state_dir antes da resolucao
    if state_dir.is_symlink():
        raise EstadoDirError(f"O state_dir nao pode ser um symlink externo: {state_dir}")

    # 3. Id divergente no manifesto existente
    if matter_id:
        manifest_path = state_dir / "run_manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                existing_id = data.get("matter_id")
                if existing_id and existing_id != matter_id:
                    raise EstadoDirError(
                        f"ID divergente: o matter_id informado '{matter_id}' conflita com "
                        f"o '{existing_id}' gravado no run_manifest.json."
                    )
            except (json.JSONDecodeError, OSError):
                # Se nao der pra ler, ignora por agora; vai quebrar nos parse reais em quem ler depoist
                pass

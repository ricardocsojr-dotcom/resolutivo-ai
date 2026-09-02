#!/usr/bin/env python3
"""Transcrição de áudio para texto — uso pontual em conversa, não reunião.

Objetivo: converter um áudio recebido (voz, WhatsApp, ditado) em texto
simples para servir de contexto/fatos numa peça. Não gera ata, não faz
diarização, não resume — apenas transcreve.

Motor: faster-whisper (já instalado no ambiente; decodifica via PyAV, não
depende de ffmpeg no PATH).

Uso:
    py -3.14 transcrever.py --audio caminho/audio.mp3
    py -3.14 transcrever.py --audio caminho/audio.mp3 --modelo small --formato srt
    py -3.14 transcrever.py --audio caminho/audio.mp3 --saida transcricao.txt
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

MODELOS_VALIDOS = {"tiny", "base", "small", "medium"}
FORMATOS_VALIDOS = {"txt", "srt", "json"}

# Vocabulário jurídico pt-BR — melhora reconhecimento de termos do domínio.
PROMPT_JURIDICO = (
    "Transcricao juridica em portugues do Brasil. Termos possiveis: processo, "
    "autos, peticao, comarca, vara, juizo, exequente, executado, autor, reu, "
    "penhora, sentenca, despacho, acordao, CPF, CNPJ, honorarios, custas."
)


def _formatar_timestamp_srt(segundos: float) -> str:
    horas, resto = divmod(int(segundos), 3600)
    minutos, segs = divmod(resto, 60)
    milissegundos = int((segundos - int(segundos)) * 1000)
    return f"{horas:02d}:{minutos:02d}:{segs:02d},{milissegundos:03d}"


def transcrever(
    audio_path: Path,
    modelo: str = "base",
    idioma: str = "pt",
    usar_vocabulario_juridico: bool = True,
) -> dict:
    """Transcreve o áudio e devolve texto + segmentos com timestamps."""
    from faster_whisper import WhisperModel

    if not audio_path.is_file():
        raise FileNotFoundError(f"áudio não encontrado: {audio_path}")

    inicio = time.perf_counter()
    model = WhisperModel(modelo, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(audio_path),
        language=idioma or None,
        vad_filter=True,
        initial_prompt=PROMPT_JURIDICO if usar_vocabulario_juridico else None,
    )

    segmentos = []
    for seg in segments:
        texto = seg.text.strip()
        if not texto:
            continue
        segmentos.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": texto})

    duracao_processamento = round(time.perf_counter() - inicio, 2)
    texto_corrido = " ".join(s["text"] for s in segmentos).strip()

    return {
        "audio": str(audio_path),
        "idioma_detectado": info.language,
        "confianca_idioma": round(info.language_probability, 2),
        "duracao_audio_s": round(info.duration, 2),
        "tempo_processamento_s": duracao_processamento,
        "modelo": modelo,
        "texto": texto_corrido,
        "segmentos": segmentos,
    }


def formatar_saida(resultado: dict, formato: str) -> str:
    if formato == "txt":
        return resultado["texto"]
    if formato == "json":
        return json.dumps(resultado, ensure_ascii=False, indent=2)
    if formato == "srt":
        linhas = []
        for i, seg in enumerate(resultado["segmentos"], start=1):
            linhas.append(str(i))
            linhas.append(f"{_formatar_timestamp_srt(seg['start'])} --> {_formatar_timestamp_srt(seg['end'])}")
            linhas.append(seg["text"])
            linhas.append("")
        return "\n".join(linhas)
    raise ValueError(f"formato desconhecido: {formato}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcrição pontual de áudio (não é ata de reunião)")
    parser.add_argument("--audio", required=True, type=Path, help="Caminho do arquivo de áudio")
    parser.add_argument("--modelo", default="base", choices=sorted(MODELOS_VALIDOS), help="Modelo Whisper (padrão: base)")
    parser.add_argument("--idioma", default="pt", help="Código do idioma (padrão: pt); vazio para autodetecção")
    parser.add_argument("--formato", default="txt", choices=sorted(FORMATOS_VALIDOS), help="Formato de saída (padrão: txt)")
    parser.add_argument("--saida", type=Path, default=None, help="Arquivo de saída; se omitido, imprime no stdout")
    parser.add_argument("--sem-vocabulario-juridico", action="store_true", help="Desativa o prompt de domínio jurídico")
    args = parser.parse_args()

    try:
        resultado = transcrever(
            args.audio,
            modelo=args.modelo,
            idioma=args.idioma,
            usar_vocabulario_juridico=not args.sem_vocabulario_juridico,
        )
    except FileNotFoundError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # falha do motor — não mascarar
        print(f"[ERRO] falha na transcrição: {exc}", file=sys.stderr)
        return 1

    saida = formatar_saida(resultado, args.formato)

    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(saida, encoding="utf-8")
        print(f"[OK] transcrição salva em {args.saida}")
        print(
            f"[INFO] idioma={resultado['idioma_detectado']} "
            f"duracao={resultado['duracao_audio_s']}s "
            f"processamento={resultado['tempo_processamento_s']}s",
            file=sys.stderr,
        )
    else:
        print(saida)

    return 0


if __name__ == "__main__":
    sys.exit(main())

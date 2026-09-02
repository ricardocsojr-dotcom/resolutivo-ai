#!/usr/bin/env python3
"""
validar_configuracao_modelos.py — Verifica se roteamento.json está correto.

Uso:
    python3 validar_configuracao_modelos.py
"""

import json
import sys
from pathlib import Path


def validar_roteamento():
    """Valida orquestracao/roteamento.json contra a recomendação otimizada."""
    
    roteamento_path = Path("orquestracao/roteamento.json")
    if not roteamento_path.exists():
        print("❌ Erro: orquestracao/roteamento.json não encontrado")
        return False
    
    try:
        with open(roteamento_path, "r", encoding="utf-8") as f:
            roteamento = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSON: {e}")
        return False
    
    workers = roteamento.get("workers", {})
    
    # Expectativas de configuração otimizada
    expectativas = {
        "planner": {
            "model": "claude-sonnet-5",
            "provider": "anthropic",
            "model_family": "anthropic",
        },
        "writer": {
            "model": "gpt-5.5",
            "provider": "openai",
            "model_family": "openai",
        },
        "critic": {
            "model": "gemini-3.1-pro-high",
            "provider": "google",
            "model_family": "google",
        },
        "validator": {
            "model": "claude-haiku-4.5",
            "provider": "anthropic",
            "model_family": "anthropic",
        },
    }
    
    print("=" * 70)
    print("VALIDAÇÃO DE CONFIGURAÇÃO — Modelos Otimizados RDAA")
    print("=" * 70)
    print()
    
    todas_ok = True
    
    for worker_name, esperado in expectativas.items():
        worker_config = workers.get(worker_name, {})
        
        print(f"📋 {worker_name.upper()}")
        print("-" * 70)
        
        # Verificar cada campo
        status_fields = {}
        for field, esperado_value in esperado.items():
            atual_value = worker_config.get(field)
            
            if atual_value == esperado_value:
                status = "✅"
                status_fields[field] = True
            else:
                status = "❌"
                status_fields[field] = False
                todas_ok = False
            
            print(f"  {status} {field:20} | Esperado: {esperado_value:25} | Atual: {atual_value}")
        
        # Independência de model_family
        print()
    
    print()
    print("=" * 70)
    print("VERIFICAÇÃO DE INDEPENDÊNCIA (model_family)")
    print("=" * 70)
    print()
    
    writer_family = workers.get("writer", {}).get("model_family")
    critic_family = workers.get("critic", {}).get("model_family")
    validator_family = workers.get("validator", {}).get("model_family")
    
    checks = [
        (writer_family != critic_family, f"writer ({writer_family}) ≠ critic ({critic_family})"),
        (critic_family != validator_family, f"critic ({critic_family}) ≠ validator ({validator_family})"),
        (writer_family != validator_family, f"writer ({writer_family}) ≠ validator ({validator_family})"),
    ]
    
    independencia_ok = True
    for check, descricao in checks:
        status = "✅" if check else "❌"
        if not check:
            independencia_ok = False
            todas_ok = False
        print(f"  {status} {descricao}")
    
    print()
    print("=" * 70)
    print("RESUMO")
    print("=" * 70)
    print()
    
    if todas_ok and independencia_ok:
        print("✅ TODOS OS CHECKS PASSARAM!")
        print()
        print("Configuração atual:")
        print(f"  - Planner:   {workers['planner'].get('model')} ({workers['planner'].get('provider')})")
        print(f"  - Writer:    {workers['writer'].get('model')} ({workers['writer'].get('provider')})")
        print(f"  - Critic:    {workers['critic'].get('model')} ({workers['critic'].get('provider')})")
        print(f"  - Validator: {workers['validator'].get('model')} ({workers['validator'].get('provider')})")
        print()
        print("✅ Independência garantida (3 providers diferentes)")
        print()
        return True
    else:
        print("❌ VERIFICAÇÃO FALHOU!")
        print()
        print("Próximos passos:")
        print("  1. Editar orquestracao/roteamento.json")
        print("  2. Verificar que cada worker tem o modelo correto")
        print("  3. Rodar este script novamente")
        print()
        return False


if __name__ == "__main__":
    sucesso = validar_roteamento()
    sys.exit(0 if sucesso else 1)

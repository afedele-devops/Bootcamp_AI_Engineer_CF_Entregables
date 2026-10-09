"""Reporte de llamadas al LLM a partir de logs/llm_calls.jsonl.

Uso:
    uv run scripts/report.py [ruta/al/archivo.jsonl]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter
from statistics import quantiles

DEFAULT_PATH = Path("logs/llm_calls.jsonl")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = Path(argv[0]) if argv else DEFAULT_PATH

    if not path.exists() or path.stat().st_size == 0: 
        sys.exit("No hay llamadas registradas todavía.") 

    lines = path.read_text(encoding="utf-8").splitlines()
    events = [json.loads(line) for line in lines if line.strip()]
    
    ok = [e for e in events if e["success"]] # Filtra solo las llamadas exitosas
    cost = sum(e["cost_usd"] for e in events) # Suma el costo total en USD
    fb = sum(e["fallback"] for e in ok) / len(ok) * 100 # Calcula el porcentaje de llamadas con fallback
    by = Counter((e["provider"], e["success"]) for e in events) # Cuenta el número de llamadas por proveedor
    latencies = [e["latency_ms"] for e in ok] # Filtra las latencias de las llamadas exitosas
    if latencies:
        q = quantiles(latencies, n=100, method="inclusive")
        p50, p95 = q[49], q[94] # Calcula la latencia p50 y p95      
        #q50, q95 = quantiles(latencies, n=100)[49], quantiles(latencies, n=100)[94]

    # TODO(clase-1): completa el reporte. Debe imprimir:
    #   - costo total en USD,
    #   - latencia p50 y p95 (solo llamadas exitosas; usa statistics.quantiles),
    #   - % de llamadas con fallback,
    #   - número de llamadas por proveedor.
    # Usa solo la librería estándar y maneja con un mensaje el caso de que el archivo
    # no exista o esté vacío.

    # print(f"Costo total: ${cost:.2f} USD")
    # if latencies:
    #     print(f"Latencia p50: {p50:.2f} ms")
    #     print(f"Latencia p95: {p95:.2f} ms") 
    # print(f"Porcentaje de llamadas con fallback: {fb:.2f}%")
    # print("Número de llamadas por proveedor:")
    # for (provider, success), count in by.items(): 
    #     if success:  # Solo imprime las llamadas exitosas
    #         print(f"{provider}: {count}")   

    print(f"{'Llamadas registradas:':<22} {len(events)} ({sum(1 for e in events if e['success'])} requests)") 
    print(f"{'Costo total:':<22} ${cost:.6f}")
    print(f"{'Latencia p50 / p95:':<22} {p50:.0f} ms / {p95:.0f} ms")
    print(f"{'Fallback:':<22} {fb:.1f} % ({sum(e['fallback'] for e in ok)} de {len(ok)})")
    print("")
    print(f"{'Proveedor':<15} {'éxitos':<10} {'errores':<10}") 
    providers = set(e["provider"] for e in events)
    for provider in providers:
         success_count = sum(1 for e in events if e["provider"] == provider and e["success"])
         error_count = sum(1 for e in events if e["provider"] == provider and not e["success"]) # ← 401 con llave inválida
         print(f"{provider:<15} {success_count:<10} {error_count:<10}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

"""
API Request Audit Logger.
Tracks external provider requests, endpoints, status codes, latency in ms, and cache status.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, List

AUDIT_LOGS: List[Dict[str, Any]] = []

def record_audit_entry(provider: str, endpoint: str, status_code: int, latency_ms: float, cache_hit: bool, note: str = ""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "endpoint": endpoint,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
        "cache_hit": cache_hit,
        "note": note
    }
    AUDIT_LOGS.append(entry)
    if len(AUDIT_LOGS) > 100:
        AUDIT_LOGS.pop(0)

def get_audit_log() -> List[Dict[str, Any]]:
    return AUDIT_LOGS.copy()

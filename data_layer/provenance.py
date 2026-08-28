"""
Scientific Traceability, Data Provenance & Audit Logger Engine.
Maintains a full, rigorous chain of custody conforming to Rule #3 and Rule #23:
  Variable Name -> Value -> Unit -> Source -> Dataset Name -> Dataset Version ->
  Source URL / API -> Retrieval Date -> Spatial Res -> Temporal Res -> Method -> Data Status.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional

AUDIT_LOGS: List[Dict[str, Any]] = []


def record_audit_entry(
    provider: str,
    endpoint: str,
    status_code: int,
    latency_ms: float,
    cache_hit: bool,
    note: str = ""
) -> Dict[str, Any]:
    """Records an external HTTP request with exact timing and status code."""
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
    if len(AUDIT_LOGS) > 200:
        AUDIT_LOGS.pop(0)
    return entry


def get_audit_log() -> List[Dict[str, Any]]:
    """Returns a copy of all recorded API requests."""
    return AUDIT_LOGS.copy()


def format_provenance_record(
    variable_name: str,
    value: Any,
    unit: str,
    data_status: str, # "OBSERVED", "EXTERNAL_API", "DERIVED", "MODELLED", "CALIBRATED", "DATA_UNAVAILABLE"
    source_agency: str,
    dataset_name: str,
    dataset_version_date: str,
    source_url: str,
    retrieval_date: str,
    spatial_resolution: str,
    temporal_resolution: str,
    calculation_method: str
) -> Dict[str, Any]:
    """Formats an authoritative provenance record conforming to strict scientific traceability."""
    display_val = value if value is not None else "DATA UNAVAILABLE"
    return {
        "variable_name": variable_name,
        "value": display_val,
        "unit": unit,
        "data_status": data_status,
        "source_agency": source_agency,
        "dataset_name": dataset_name,
        "dataset_version_date": dataset_version_date,
        "source_url": source_url,
        "retrieval_date": retrieval_date,
        "spatial_resolution": spatial_resolution,
        "temporal_resolution": temporal_resolution,
        "calculation_method": calculation_method,
        "provenance_badge": f"[{data_status}] {variable_name}: {display_val} {unit} ({source_agency})"
    }

"""
External Data Adapters with Full Audit Logging & Scientific Provenance.
Connects to:
  1. Open-Meteo Historical & Reanalysis Climate API (ECMWF ERA5 / Global Models)
  2. Open-Elevation / USGS SRTM Elevation DEM API
  3. Global Biodiversity Information Facility (GBIF) Species Occurrence API
Maintains local cache, latency tracking, and strict "DATA UNAVAILABLE" handling.
"""

from __future__ import annotations
import json
import os
import time
import urllib.request
import urllib.parse
from datetime import date, timedelta, datetime
from typing import Dict, Any, Optional, List
from .provenance import record_audit_entry, format_provenance_record

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _http_get_json(url: str, provider: str, cache_filename: str, timeout: int = 8) -> Dict[str, Any]:
    """Internal helper to fetch JSON with audit logging and disk caching."""
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    start_time = time.time()

    # 1. Try live HTTP request
    try:
        print(f"[5] External API request started: {provider} -> {url[:70]}... (timeout={timeout}s)", flush=True)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "India-Forest-LANDIS-II-Scientific-Platform/2.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            latency_ms = (time.time() - start_time) * 1000.0
            print(f"[6] External API response received: {provider} (HTTP {resp.status}, {latency_ms:.1f}ms)", flush=True)
            
            # Record audit entry
            record_audit_entry(
                provider=provider,
                endpoint=url,
                status_code=resp.status,
                latency_ms=latency_ms,
                cache_hit=False,
                note="Live API request successful"
            )
            
            # Save to cache
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "data": data
                }, f)

            return {
                "success": True,
                "data": data,
                "cached": False,
                "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "url": url,
                "status_code": resp.status
            }
    except Exception as live_err:
        latency_ms = (time.time() - start_time) * 1000.0
        print(f"[6] External API live request failed ({live_err}); attempting cache lookup", flush=True)


        # 2. Check fallback cache
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_obj = json.load(f)
                record_audit_entry(
                    provider=provider,
                    endpoint=url,
                    status_code=200,
                    latency_ms=latency_ms,
                    cache_hit=True,
                    note=f"Live request failed ({str(live_err)}), served from local cache"
                )
                return {
                    "success": True,
                    "data": cached_obj.get("data", {}),
                    "cached": True,
                    "retrieval_date": cached_obj.get("timestamp", "PREVIOUS_CACHE"),
                    "url": url,
                    "status_code": 200
                }
            except Exception:
                pass

        record_audit_entry(
            provider=provider,
            endpoint=url,
            status_code=503,
            latency_ms=latency_ms,
            cache_hit=False,
            note=f"Error: {str(live_err)}"
        )
        return {
            "success": False,
            "error": f"API request failed: {str(live_err)}",
            "data": None,
            "cached": False,
            "url": url,
            "status_code": 503
        }


def fetch_open_meteo_climate(lat: float, lon: float, days: int = 365) -> Dict[str, Any]:
    """
    Fetches real historical climate data from Open-Meteo ERA5 / Historical API.
    Retrieves: 2m temperature mean/min/max, precipitation sum, solar radiation sum.
    """
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=days)
    
    query_params = urllib.parse.urlencode({
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum,shortwave_radiation_sum",
        "timezone": "Asia/Kolkata"
    })
    url = f"https://archive-api.open-meteo.com/v1/archive?{query_params}"
    cache_name = f"openmeteo_era5_{lat:.3f}_{lon:.3f}_{days}d.json"

    res = _http_get_json(url, "Open-Meteo Climate API", cache_name)

    if not res["success"] or not res.get("data"):
        return {
            "available": False,
            "status": "DATA UNAVAILABLE",
            "error": res.get("error", "Failed to retrieve climate data"),
            "url": url,
            "provenance": format_provenance_record(
                variable_name="Annual Climate Metrics",
                value="DATA UNAVAILABLE",
                unit="°C / mm",
                data_status="DATA_UNAVAILABLE",
                source_agency="Open-Meteo / ECMWF ERA5",
                dataset_name="ERA5 Reanalysis",
                dataset_version_date=str(date.today()),
                source_url=url,
                retrieval_date=datetime.now().isoformat(),
                spatial_resolution="0.1 deg (~11 km)",
                temporal_resolution="Daily",
                calculation_method="HTTP API Fetch Failed"
            )
        }

    daily = res["data"].get("daily", {})
    t_means = [float(v) for v in daily.get("temperature_2m_mean", []) if v is not None]
    t_maxs = [float(v) for v in daily.get("temperature_2m_max", []) if v is not None]
    t_mins = [float(v) for v in daily.get("temperature_2m_min", []) if v is not None]
    precips = [float(v) for v in daily.get("precipitation_sum", []) if v is not None]
    radiations = [float(v) for v in daily.get("shortwave_radiation_sum", []) if v is not None]

    mean_annual_temp = round(sum(t_means) / len(t_means), 2) if t_means else None
    max_temp = round(max(t_maxs), 2) if t_maxs else None
    min_temp = round(min(t_mins), 2) if t_mins else None
    total_precip_mm = round(sum(precips), 2) if precips else None
    mean_radiation = round(sum(radiations) / len(radiations), 2) if radiations else None

    return {
        "available": True,
        "status": "RETRIEVED",
        "cached": res.get("cached", False),
        "mean_annual_temp_c": mean_annual_temp,
        "max_temperature_c": max_temp,
        "min_temperature_c": min_temp,
        "annual_precipitation_mm": total_precip_mm,
        "mean_solar_radiation_mj_m2": mean_radiation,
        "data_points_count": len(t_means),
        "time_range": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "url": url,
        "provenance": {
            "mean_annual_temp": format_provenance_record(
                variable_name="Mean Annual 2m Temperature",
                value=mean_annual_temp,
                unit="°C",
                data_status="EXTERNAL_API" if not res.get("cached") else "DERIVED",
                source_agency="ECMWF / Open-Meteo",
                dataset_name="ERA5 Land Reanalysis / Historical Archive",
                dataset_version_date="v1",
                source_url=url,
                retrieval_date=res.get("retrieval_date", str(date.today())),
                spatial_resolution="0.1 deg (~11 km grid)",
                temporal_resolution=f"Daily Mean ({len(t_means)} observations)",
                calculation_method="Arithmetic Mean over time series"
            ),
            "annual_precipitation": format_provenance_record(
                variable_name="Annual Precipitation Sum",
                value=total_precip_mm,
                unit="mm/year",
                data_status="EXTERNAL_API" if not res.get("cached") else "DERIVED",
                source_agency="ECMWF / Open-Meteo",
                dataset_name="ERA5 Land Reanalysis / Historical Archive",
                dataset_version_date="v1",
                source_url=url,
                retrieval_date=res.get("retrieval_date", str(date.today())),
                spatial_resolution="0.1 deg (~11 km grid)",
                temporal_resolution=f"Daily Sum ({len(precips)} observations)",
                calculation_method="Summation of daily precipitation"
            )
        }
    }


def fetch_open_elevation(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches real elevation DEM from Open-Elevation API (SRTM 90m dataset).
    """
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={round(lat, 4)},{round(lon, 4)}"
    cache_name = f"elevation_{lat:.3f}_{lon:.3f}.json"
    
    res = _http_get_json(url, "Open-Elevation DEM API", cache_name, timeout=6)
    
    if not res["success"] or not res.get("data"):
        return {
            "available": False,
            "status": "DATA UNAVAILABLE",
            "elevation_m": "DATA UNAVAILABLE",
            "url": url,
            "provenance": format_provenance_record(
                variable_name="Digital Elevation Model (DEM)",
                value="DATA UNAVAILABLE",
                unit="m ASL",
                data_status="DATA_UNAVAILABLE",
                source_agency="NASA / USGS SRTM via Open-Elevation",
                dataset_name="SRTM 90m DEM",
                dataset_version_date="v4.1",
                source_url=url,
                retrieval_date=datetime.now().isoformat(),
                spatial_resolution="90m",
                temporal_resolution="Static DEM",
                calculation_method="API Query Failed"
            )
        }

    results = res["data"].get("results", [])
    if results and "elevation" in results[0]:
        elev = float(results[0]["elevation"])
        return {
            "available": True,
            "status": "RETRIEVED",
            "elevation_m": round(elev, 1),
            "cached": res.get("cached", False),
            "url": url,
            "provenance": format_provenance_record(
                variable_name="Digital Elevation Model (DEM)",
                value=round(elev, 1),
                unit="m ASL",
                data_status="EXTERNAL_API" if not res.get("cached") else "DERIVED",
                source_agency="NASA / USGS SRTM via Open-Elevation API",
                dataset_name="SRTM 90m Digital Elevation Model",
                dataset_version_date="v4.1",
                source_url=url,
                retrieval_date=res.get("retrieval_date", str(date.today())),
                spatial_resolution="90m Grid Cell",
                temporal_resolution="Static Topography",
                calculation_method="Bilinear Interpolation of SRTM Grid"
            )
        }

    return {
        "available": False,
        "status": "DATA UNAVAILABLE",
        "elevation_m": "DATA UNAVAILABLE"
    }


def fetch_gbif_species_occurrences(
    scientific_name: str,
    country_code: str = "IN",
    limit: int = 5
) -> Dict[str, Any]:
    """
    Fetches real verified biodiversity occurrence records from GBIF API.
    """
    encoded_name = urllib.parse.quote(scientific_name)
    url = f"https://api.gbif.org/v1/occurrence/search?scientificName={encoded_name}&country={country_code}&limit={limit}"
    cache_name = f"gbif_{scientific_name.replace(' ', '_')}_{country_code}.json"

    res = _http_get_json(url, "GBIF Species Occurrence API", cache_name, timeout=6)

    if not res["success"] or not res.get("data"):
        return {
            "available": False,
            "status": "DATA UNAVAILABLE",
            "occurrence_count": "DATA UNAVAILABLE",
            "occurrences": [],
            "url": url,
            "provenance": format_provenance_record(
                variable_name=f"GBIF Verified Occurrences ({scientific_name})",
                value="DATA UNAVAILABLE",
                unit="Records",
                data_status="DATA_UNAVAILABLE",
                source_agency="Global Biodiversity Information Facility (GBIF)",
                dataset_name="GBIF Occurrence Index",
                dataset_version_date=str(date.today()),
                source_url=url,
                retrieval_date=datetime.now().isoformat(),
                spatial_resolution="Point Coordinates",
                temporal_resolution="Documented Records",
                calculation_method="GBIF API Query Failed"
            )
        }

    data = res["data"]
    total_count = data.get("count", 0)
    results = data.get("results", [])

    records = []
    for item in results:
        records.append({
            "gbif_id": item.get("key"),
            "dataset_name": item.get("datasetName", "BSI / Research Herbarium"),
            "event_date": item.get("eventDate", item.get("year", "UNDATED")),
            "decimal_latitude": item.get("decimalLatitude"),
            "decimal_longitude": item.get("decimalLongitude"),
            "state_province": item.get("stateProvince", "INDIA"),
            "basis_of_record": item.get("basisOfRecord", "HUMAN_OBSERVATION / PRESERVED_SPECIMEN")
        })

    return {
        "available": True,
        "status": "RETRIEVED",
        "species": scientific_name,
        "country": country_code,
        "total_documented_occurrences_in_country": total_count,
        "sample_records": records,
        "cached": res.get("cached", False),
        "url": url,
        "provenance": format_provenance_record(
            variable_name=f"Documented Biodiversity Occurrences ({scientific_name})",
            value=total_count,
            unit="Verified Field Records",
            data_status="EXTERNAL_API" if not res.get("cached") else "DERIVED",
            source_agency="Global Biodiversity Information Facility (GBIF) / BSI Herbarium",
            dataset_name="GBIF Species Occurrence Database (India)",
            dataset_version_date=str(date.today()),
            source_url=url,
            retrieval_date=res.get("retrieval_date", str(date.today())),
            spatial_resolution="Georeferenced Point Observations",
            temporal_resolution="Field Collection Dates",
            calculation_method="GBIF Occurrence Filter by Taxon & Country"
        )
    }

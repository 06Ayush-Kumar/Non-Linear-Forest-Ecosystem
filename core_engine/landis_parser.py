"""
LANDIS-II Output Parser & State Variable Extractor.
Extracts real simulation trajectories from LANDIS-II generated CSV logs and GeoTIFF rasters,
translating landscape biomass into structured inputs for our mathematical stability model.
"""

from __future__ import annotations
import os
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


def parse_biomass_succession_log(log_csv_path: str | Path) -> List[Dict[str, Any]]:
    """
    Parses Biomass-succession-log.csv.
    Columns: Time, EcoName, ActiveCount, AvgLiveB, AvgAG_NPP, AvgLitterB, AvgWoodLitterB, AvgDefoliation
    Note: AvgLiveB is in g/m² in LANDIS-II, converted to Mg/ha by multiplying by 0.01.
    """
    path = Path(log_csv_path)
    if not path.exists():
        return []

    records = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean stripped keys and values
            clean_row = {k.strip(): v.strip() for k, v in row.items() if k is not None}
            try:
                t = int(float(clean_row.get("Time", 0)))
                eco = clean_row.get("EcoName", "All")
                active = int(float(clean_row.get("ActiveCount", 0)))
                avg_live_b_g_m2 = float(clean_row.get("AvgLiveB", 0.0))
                anpp_g_m2 = float(clean_row.get("AvgAG_NPP", 0.0))
                litter_g_m2 = float(clean_row.get("AvgLitterB", 0.0))
                wood_litter_g_m2 = float(clean_row.get("AvgWoodLitterB", 0.0))

                records.append({
                    "time_year": t,
                    "ecoregion": eco,
                    "active_sites": active,
                    "biomass_g_m2": avg_live_b_g_m2,
                    "biomass_mg_ha": round(avg_live_b_g_m2 * 0.01, 2),
                    "anpp_g_m2_yr": anpp_g_m2,
                    "anpp_mg_ha_yr": round(anpp_g_m2 * 0.01, 2),
                    "litter_mg_ha": round(litter_g_m2 * 0.01, 2),
                    "dead_wood_mg_ha": round(wood_litter_g_m2 * 0.01, 2),
                    "carbon_stock_mg_c_ha": round(avg_live_b_g_m2 * 0.01 * 0.47, 2), # IPCC 2006 Factor
                    "source": "LANDIS-II Biomass Succession Engine"
                })
            except (ValueError, TypeError):
                continue

    return records


def parse_species_biomass_log(log_csv_path: str | Path) -> Dict[str, Any]:
    """
    Parses spp-biomass-log.csv.
    Extracts individual species biomass trajectories across time.
    """
    path = Path(log_csv_path)
    if not path.exists():
        return {"time_steps": [], "species_data": {}}

    time_steps = []
    species_data: Dict[str, List[float]] = {}
    time_records: List[Dict[str, Any]] = []

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k.strip(): v.strip() for k, v in row.items() if k is not None}
            try:
                t = int(float(clean_row.get("Time", 0)))
                if t not in time_steps:
                    time_steps.append(t)

                record: Dict[str, Any] = {"time_year": t, "ecoregion": clean_row.get("EcoName", "All")}
                for k, v in clean_row.items():
                    if k.startswith("AboveGroundBiomass_"):
                        sp_code = k.replace("AboveGroundBiomass_", "")
                        val_g_m2 = float(v)
                        val_mg_ha = round(val_g_m2 * 0.01, 2)
                        record[sp_code] = val_mg_ha
                        if sp_code not in species_data:
                            species_data[sp_code] = []
                        species_data[sp_code].append(val_mg_ha)

                time_records.append(record)
            except (ValueError, TypeError):
                continue

    return {
        "time_steps": time_steps,
        "species_data": species_data,
        "records": time_records
    }


def extract_three_state_variables(
    spp_log_path: str | Path,
    native_canopy_species: Optional[List[str]] = None,
    understory_species: Optional[List[str]] = None,
    invasive_species: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Extracts the 3 state variables (x: Native Canopy, y: Understory, z: Invasive)
    from LANDIS-II species biomass log.
    If species lists are not provided, uses standard classifications or defaults.
    """
    spp_info = parse_species_biomass_log(spp_log_path)
    records = spp_info.get("records", [])
    if not records:
        return []

    # Default groupings if none supplied
    canopy_keys = set(k.lower() for k in (native_canopy_species or ["tectgran", "shorrob", "dalblat", "piceglau", "pinustro", "querrubr", "acersacc"]))
    understory_keys = set(k.lower() for k in (understory_species or ["bambbam", "termelli", "betualle", "fraxamer", "acerrubr", "tiliamer"]))
    invasive_keys = set(k.lower() for k in (invasive_species or ["lantcam", "prosjul", "partnyst", "chroodo", "poputrem", "pinubank"]))

    state_trajectory = []

    for r in records:
        t = r["time_year"]
        x_biomass = 0.0
        y_biomass = 0.0
        z_biomass = 0.0
        unclassified_biomass = 0.0

        for sp, val in r.items():
            if sp in ("time_year", "ecoregion"):
                continue
            sp_lower = sp.lower()
            if any(k in sp_lower for k in canopy_keys):
                x_biomass += val
            elif any(k in sp_lower for k in understory_keys):
                y_biomass += val
            elif any(k in sp_lower for k in invasive_keys):
                z_biomass += val
            else:
                # Distribute unclassified proportionally
                unclassified_biomass += val

        if unclassified_biomass > 0:
            if (x_biomass + y_biomass + z_biomass) > 0:
                tot = x_biomass + y_biomass + z_biomass
                x_biomass += unclassified_biomass * (x_biomass / tot)
                y_biomass += unclassified_biomass * (y_biomass / tot)
                z_biomass += unclassified_biomass * (z_biomass / tot)
            else:
                x_biomass += unclassified_biomass * 0.7
                y_biomass += unclassified_biomass * 0.3

        total_b = round(x_biomass + y_biomass + z_biomass, 2)
        carbon_stock = round(total_b * 0.47, 2)

        state_trajectory.append({
            "year": t,
            "x_native_canopy_mg_ha": round(x_biomass, 2),
            "y_understory_mg_ha": round(y_biomass, 2),
            "z_invasive_mg_ha": round(z_biomass, 2),
            "total_biomass_mg_ha": total_b,
            "carbon_stock_mg_c_ha": carbon_stock,
            "provenance": {
                "biomass_source": "LANDIS-II Simulation Output (spp-biomass-log.csv)",
                "carbon_equation": "Carbon = Total Biomass * 0.47 (IPCC 2006 Good Practice Guidance; FSI Carbon Accounting Method)",
                "unit": "Mg/ha (Biomass), Mg C/ha (Carbon)"
            }
        })

    return state_trajectory


def parse_landis_output_directory(run_dir: str | Path) -> Dict[str, Any]:
    """
    Comprehensive parser for a complete LANDIS-II simulation run directory.
    Combines succession log, species log, spatial raster map list, and state variables.
    """
    path = Path(run_dir)
    if not path.exists():
        return {
            "success": False,
            "error": f"Run directory does not exist: {run_dir}",
            "biomass_log": [],
            "species_log": {},
            "state_trajectory": [],
            "raster_maps": []
        }

    biomass_log_path = path / "Biomass-succession-log.csv"
    spp_log_path = path / "spp-biomass-log.csv"

    biomass_records = parse_biomass_succession_log(biomass_log_path)
    spp_data = parse_species_biomass_log(spp_log_path)
    state_traj = extract_three_state_variables(spp_log_path)

    # Find generated raster maps
    raster_files = []
    outputs_dir = path / "outputs" / "biomass"
    if outputs_dir.exists():
        for f in outputs_dir.glob("*.tif"):
            raster_files.append({
                "filename": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size
            })

    return {
        "success": len(biomass_records) > 0 or len(state_traj) > 0,
        "run_directory": str(path),
        "biomass_log": biomass_records,
        "species_log": spp_data,
        "state_trajectory": state_traj,
        "raster_maps_count": len(raster_files),
        "raster_maps": raster_files[:20] # Sample top maps
    }

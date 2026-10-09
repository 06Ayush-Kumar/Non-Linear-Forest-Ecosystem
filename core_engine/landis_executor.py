"""
LANDIS-II Official Execution Engine.
Automates configuration file generation and execution of the compiled LANDIS-II 7
binary (Landis.Console.exe) with Biomass Succession and Output Biomass extensions.
"""

from __future__ import annotations
import os
import subprocess
import time
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build_landis"
BIN_DIR = BUILD_DIR / "bin"
LANDIS_EXE = BIN_DIR / "Landis.Console.exe"
RUNS_DIR = PROJECT_ROOT / "runs"


import sys

def is_landis_installed() -> bool:
    """Checks if the compiled LANDIS-II executable and required assemblies exist and host OS is Windows."""
    return (
        sys.platform.startswith("win")
        and LANDIS_EXE.exists()
        and (BIN_DIR / "Landis.Core.dll").exists()
        and (BIN_DIR / "Landis.Extension.Succession.Biomass-v7.dll").exists()
        and (BIN_DIR / "Landis.Extension.Output.Biomass-v4.dll").exists()
    )


def get_landis_metadata() -> Dict[str, Any]:
    """Returns technical metadata about the installed LANDIS-II engine."""
    installed = is_landis_installed()
    is_linux = not sys.platform.startswith("win")
    status_str = "OPERATIONAL" if installed else ("UNAVAILABLE_ON_LINUX" if is_linux else "NEEDS_BUILD")
    return {
        "installed": installed,
        "execution_available": installed,
        "engine_name": "LANDIS-II Forest Landscape Simulation Framework",
        "core_version": "7.0 (Release build with Roslyn C# Compiler)" if installed else "7.0 (Windows .NET Framework 4.8 Runtime Required)",
        "target_framework": ".NET Standard 2.0 / .NET Framework 4.8 Runtime",
        "executable_path": str(LANDIS_EXE) if installed else ("NOT_SUPPORTED_ON_LINUX" if is_linux else "NOT_FOUND"),
        "platform_os": sys.platform,
        "cloud_mode_active": is_linux,
        "reason": "Native Landscape Engine requires Windows runtime." if is_linux else None,
        "cloud_message": "LANDIS-II native engine unavailable in this Linux environment. (Requires Windows .NET Framework 4.8 & GDAL runtime. Layer 2 Reduced-Order Spatial Simulator active)." if is_linux else None,
        "installed_extensions": [
            {
                "name": "Biomass Succession",
                "version": "7.2",
                "type": "succession",
                "assembly": "Landis.Extension.Succession.Biomass-v7.dll",
                "class": "Landis.Extension.Succession.Biomass.PlugIn"
            },
            {
                "name": "Output Biomass",
                "version": "4.1",
                "type": "output",
                "assembly": "Landis.Extension.Output.Biomass-v4.dll",
                "class": "Landis.Extension.Output.Biomass.PlugIn"
            }
        ] if installed else [],
        "raster_io": "GDAL 2.0.2 / Gdal.Core Native Integration (GeoTIFF / GIS)" if installed else "NOT_SUPPORTED_ON_LINUX",
        "status": status_str
    }



def prepare_landis_run_directory(run_id: str) -> Path:
    """Creates a fresh isolated run directory for a LANDIS-II scenario simulation."""
    run_path = RUNS_DIR / run_id
    os.makedirs(run_path, exist_ok=True)
    os.makedirs(run_path / "outputs" / "biomass", exist_ok=True)
    return run_path


def create_fresh_scenario_directory(
    source_dir: str | Path,
    target_dir: str | Path
) -> Path:
    """
    Creates a fresh, clean simulation directory copying ONLY scenario input files.
    Strictly excludes all previous output logs, rasters, and temp metadata.
    Platform-aware: safely bypasses on Linux or when source directory does not exist.
    """
    dst = Path(target_dir).resolve()
    if not sys.platform.startswith("win"):
        return dst

    src = Path(source_dir).resolve()
    if not src.exists():
        return dst

    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst, exist_ok=True)

    input_extensions = {".txt", ".tif", ".csv", ".gis", ".xlsx", ".bat"}
    exclude_files = {
        "biomass-succession-log.csv",
        "spp-biomass-log.csv",
        "landis-climate-log.txt",
        "climate-future-annual-input-log.csv",
        "climate-future-monthly-input-log.csv",
        "climate-spinup-annual-input-log.csv",
        "climate-spinup-monthly-input-log.csv"
    }

    for item in src.iterdir():
        if item.is_file() and item.suffix.lower() in input_extensions:
            name_lower = item.name.lower()
            if name_lower not in exclude_files:
                # Exclude output raster maps generated from previous runs
                if item.suffix.lower() == ".tif" and (name_lower.startswith("bio-") or name_lower.startswith("biomass-")):
                    continue
                shutil.copy2(item, dst / item.name)

    return dst




def execute_landis_simulation(
    scenario_file: str,
    working_dir: str | Path,
    timeout_seconds: int = 240
) -> Dict[str, Any]:
    """
    Executes Landis.Console.exe on the specified scenario file within working_dir.
    Returns execution metadata, return code, logs, and execution duration.
    On Linux/cloud: Never attempts subprocess execution and returns clean UNAVAILABLE_ON_LINUX structure.
    """
    if not sys.platform.startswith("win"):
        return {
            "success": False,
            "status": "UNAVAILABLE_ON_LINUX",
            "execution_available": False,
            "reason": "Native Landscape Engine requires Windows runtime.",
            "error": "Native Landscape Engine requires Windows .NET/GDAL runtime. This Linux cloud deployment executes the Layer 2/3 Reduced-Order Spatial Simulator.",
            "return_code": None,
            "stdout": "",
            "stderr": "NATIVE_LANDSCAPE_ENGINE_UNAVAILABLE_ON_LINUX",
            "duration_seconds": None
        }

    if not is_landis_installed():
        return {
            "success": False,
            "status": "NEEDS_BUILD",
            "execution_available": False,
            "reason": "LANDIS-II executable not found in build_landis/bin.",
            "error": "LANDIS-II executable not found in build_landis/bin.",
            "return_code": -1,
            "stdout": "",
            "stderr": "LANDIS_EXE_NOT_FOUND",
            "duration_seconds": 0.0
        }

    working_path = Path(working_dir).resolve()
    scenario_path = working_path / scenario_file
    if not scenario_path.exists():
        return {
            "success": False,
            "status": "SCENARIO_NOT_FOUND",
            "execution_available": False,
            "error": f"Scenario file not found: {scenario_path}",
            "return_code": -1,
            "stdout": "",
            "stderr": "SCENARIO_FILE_NOT_FOUND",
            "duration_seconds": 0.0
        }

    env = os.environ.copy()
    env["PATH"] = f"{str(BIN_DIR)};{env.get('PATH', '')}"

    start_time = time.time()
    try:
        proc = subprocess.run(
            [str(LANDIS_EXE), str(scenario_file)],
            cwd=str(working_path),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        duration = round(time.time() - start_time, 2)
        success = proc.returncode == 0

        return {
            "success": success,
            "return_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_seconds": duration,
            "command": f"{LANDIS_EXE} {scenario_file}",
            "working_directory": str(working_path)
        }
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start_time, 2)
        return {
            "success": False,
            "error": f"LANDIS-II simulation timed out after {timeout_seconds} seconds.",
            "return_code": -99,
            "stdout": "",
            "stderr": "TIMEOUT",
            "duration_seconds": duration
        }
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        return {
            "success": False,
            "error": f"LANDIS-II execution error: {str(e)}",
            "return_code": -1,
            "stdout": "",
            "stderr": str(e),
            "duration_seconds": duration
        }

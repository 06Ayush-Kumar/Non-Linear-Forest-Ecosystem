from __future__ import annotations

import numpy as np


def normalize_environment(raw_data: dict, climate_scaling: float = 1.0, disturbance: float = 0.2) -> dict:
    ndvi = np.asarray(raw_data["vegetation"]["ndvi"], dtype=float)
    temp = float(raw_data["climate"]["temperature_c"])
    rain = float(raw_data["climate"]["precipitation_mm"])
    climate_scaling = float(np.clip(climate_scaling, 0.55, 1.55))
    disturbance = float(np.clip(disturbance, 0.0, 0.9))

    ndvi_norm = np.clip((ndvi - 0.18) / (0.88 - 0.18), 0.0, 1.0)
    moisture = np.clip(rain / 130.0, 0.15, 1.35)
    temp_suitability = np.exp(-((temp - 24.0) ** 2) / 115.0)
    environmental_factor = np.clip((0.62 * temp_suitability + 0.38 * moisture) * climate_scaling, 0.25, 1.65)

    k1 = 80.0 + 130.0 * ndvi_norm
    k2 = 45.0 + 70.0 * (0.55 * ndvi_norm + 0.45 * environmental_factor)
    k3 = 25.0 + 80.0 * (1.0 - 0.42 * ndvi_norm + 0.28 * environmental_factor)
    disturbance_grid = np.clip(disturbance + (1.0 - ndvi_norm) * 0.22, 0.0, 0.95)

    return {
        "ndvi": np.round(ndvi, 4).tolist(),
        "environmental_factor": round(float(environmental_factor), 4),
        "temperature_c": round(temp, 2),
        "precipitation_mm": round(rain, 2),
        "carrying_capacity": np.round(np.stack([k1, k2, k3], axis=-1), 3).tolist(),
        "disturbance_grid": np.round(disturbance_grid, 4).tolist(),
        "biodiversity_baseline": round(float(np.mean(ndvi_norm) * (1.0 - disturbance * 0.35)), 4),
    }

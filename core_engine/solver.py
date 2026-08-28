from __future__ import annotations

import numpy as np

from .model import ModelParameters, derivatives


def rk4_step(state: np.ndarray, carrying_capacity: np.ndarray, params: ModelParameters, dt: float) -> np.ndarray:
    k1 = derivatives(state, carrying_capacity, params)
    k2 = derivatives(state + 0.5 * dt * k1, carrying_capacity, params)
    k3 = derivatives(state + 0.5 * dt * k2, carrying_capacity, params)
    k4 = derivatives(state + dt * k3, carrying_capacity, params)
    return np.clip(state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4), 0.0, 260.0)


def simulate_cell(initial: np.ndarray, carrying_capacity: np.ndarray, params: ModelParameters, steps: int = 180, dt: float = 0.08) -> dict:
    state = np.asarray(initial, dtype=float)
    series = np.zeros((steps + 1, 3), dtype=float)
    series[0] = state
    for index in range(1, steps + 1):
        state = rk4_step(state, carrying_capacity, params, dt)
        series[index] = state
    time = np.arange(steps + 1) * dt
    return {"time": np.round(time, 3).tolist(), "series": np.round(series, 4).tolist(), "final_state": np.round(series[-1], 4)}

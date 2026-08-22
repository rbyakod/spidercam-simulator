from __future__ import annotations
import numpy as np
from config import settings

def anchors() -> np.ndarray:
    W = settings.frame_width
    H = settings.frame_height
    D = settings.frame_depth
    return np.array([
        [0.0, H, 0.0],
        [W,   H, 0.0],
        [0.0, H,  D],
        [W,   H,  D],
    ], dtype=float)

def cable_lengths(pos: np.ndarray) -> np.ndarray:
    A = anchors()
    return np.linalg.norm(A - pos, axis=1)

def inverse_kinematics(pos: np.ndarray) -> np.ndarray:
    return cable_lengths(pos)

def forward_kinematics(lengths: np.ndarray, guess=None) -> np.ndarray:
    from scipy.optimize import minimize
    A = anchors()
    if guess is None:
        guess = np.array([settings.frame_width/2, settings.frame_height/2, settings.frame_depth/2])
    def residuals(p):
        d = np.linalg.norm(A - p, axis=1) - lengths
        return float(np.dot(d, d))
    res = minimize(residuals, guess, method="Nelder-Mead",
                   options={"xatol": 1e-7, "fatol": 1e-7, "maxiter": 5000})
    return res.x

def check_tensions(pos: np.ndarray, payload_kg: float = 0.5) -> dict:
    A = anchors()
    u = (A - pos)
    norms = np.linalg.norm(u, axis=1, keepdims=True)
    u = u / norms
    g = np.array([0.0, -9.81 * payload_kg, 0.0])
    S = u.T
    tensions, *_ = np.linalg.lstsq(S, -g, rcond=None)
    return {
        "tensions": tensions.tolist(),
        "all_positive": bool(np.all(tensions > settings.min_cable_tension)),
        "within_max": bool(np.all(tensions < settings.max_cable_tension)),
    }

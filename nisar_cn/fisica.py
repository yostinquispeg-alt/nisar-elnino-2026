"""Física de la retrodispersión en banda L: rugosidad y constante dieléctrica.

- Dubois et al. (1995), σ⁰_HH(ε', ks, θ, λ) — R8 [V, fuente secundaria: implementación SENSE `dubois95._hh`,
  que cita Ulaby 2014 cap. 10.6; límites de validez en arXiv:2412.11874].
- Topp et al. (1980), ε(m_v) — R9 [V, fuente secundaria: arXiv:1006.4307].
- Frecuencia central por modo de ancho de banda — R5 [V].
- Sensibilidades e inversión de Δε — deducción algebraica propia sobre la ec. de R8 [A].
"""
import numpy as np

C_LUZ = 299_792_458.0  # m/s, valor exacto por definición del SI

# R5, tabla 1: frecuencia central de la banda A (MHz) según los dos primeros caracteres del código MODE (R2)
FREQ_A_MHZ = {"77": 1257.5, "40": 1239.0, "20": 1229.0, "05": 1221.5}


def lambda_cm(mode_code: str) -> float:
    """Longitud de onda en cm para el código MODE del nombre del producto (p. ej. '4005')."""
    return C_LUZ / (FREQ_A_MHZ[mode_code[:2]] * 1e6) * 100


def topp_eps(mv):
    """R9: ε = 3.03 + 9.3 m_v + 146.0 m_v² − 76.7 m_v³ (m_v en cm³/cm³)."""
    mv = np.asarray(mv, float)
    return 3.03 + 9.3 * mv + 146.0 * mv**2 - 76.7 * mv**3


def dubois_hh(eps, ks, theta_rad, lam_cm):
    """R8: σ⁰_HH lineal. θ en radianes, λ en cm."""
    a = 10**-2.75 * np.cos(theta_rad) ** 1.5 / np.sin(theta_rad) ** 5
    c = 10 ** (0.028 * np.real(eps) * np.tan(theta_rad))
    d = (ks * np.sin(theta_rad)) ** 1.4 * lam_cm**0.7
    return a * c * d


def dubois_valido(mv, ks, theta_rad):
    """R8 (límites vía arXiv:2412.11874): m_v < 0.35, ks < 3, θ > 30°."""
    return (np.asarray(mv) < 0.35) & (np.asarray(ks) < 3) & (np.degrees(theta_rad) > 30)


def dsigma_deps_db(theta_rad):
    """[A] ∂σ⁰_HH,dB/∂ε' = 10·0.028·tanθ (derivada de 10·log10 de R8)."""
    return 0.28 * np.tan(theta_rad)


def delta_eps(dsigma_db, theta_rad):
    """[A] Δε' = Δσ⁰_dB / (0.28·tanθ), suponiendo ks constante entre fechas (supuesto propio)."""
    return dsigma_db / dsigma_deps_db(theta_rad)


def dsigma_rugosidad_db(ks1, ks2):
    """[A] Δσ⁰_HH,dB con ε y θ fijos = 14·log10(ks2/ks1)."""
    return 14 * np.log10(np.asarray(ks2) / np.asarray(ks1))

"""Analysis module."""

from .thickness_solver import (
    theoretical_S_curve, solve_for_thickness, fit_model

)
from .sensitivity import (
    study_interface_width,
    study_diffusion_length,
    study_layer_thickness,
    monte_carlo_uncertainty
)

__all__ = [
    'theoretical_S_curve', 
    'solve_for_thickness', 
    'fit_model',
    'study_interface_width',
    'study_diffusion_length',
    'study_layer_thickness',
    'monte_carlo_uncertainty'
]
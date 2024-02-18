"""
A linearity-exploiting sparse nonlinear constrained optimization problem solver that uses the interior-point method.
"""
from __future__ import annotations
from . import autodiff
from . import optimization
__all__ = ['autodiff', 'optimization']

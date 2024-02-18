"""
mlx.metal
"""
from __future__ import annotations
__all__ = ['cache_enabled', 'is_available', 'set_cache_enabled']
def cache_enabled() -> bool:
    """
    check if metal buffer cache is enabled, default is true
    """
def is_available() -> bool:
    ...
def set_cache_enabled(arg0: bool) -> None:
    """
    enable or disable metal buffer cache
    """

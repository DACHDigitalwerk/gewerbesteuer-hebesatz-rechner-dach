# -*- coding: utf-8 -*-
"""
gewerbesteuer_dach
~~~~~~~~~~~~~~~~~~
Präziser Gewerbesteuer- & Hebesatz-Rechner 2026 für Deutschland (DACH-Raum).
Inklusive Freibeträge (§ 11 GewStG), Hinzurechnungen (§ 8 GewStG),
Kürzungen (§ 9 GewStG) und ESt-Anrechnung (§ 35 EStG Faktor 4,0).
"""

from .models import LegalForm, FinancingAdditions, Reductions, GewerbesteuerResult
from .calculator import calculate_gewerbesteuer, compare_municipalities
from .rates import CITIES_HEBESATZ, get_city_hebesatz, MIN_HEBESATZ_LEGAL

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__all__ = [
    "LegalForm",
    "FinancingAdditions",
    "Reductions",
    "GewerbesteuerResult",
    "calculate_gewerbesteuer",
    "compare_municipalities",
    "CITIES_HEBESATZ",
    "get_city_hebesatz",
    "MIN_HEBESATZ_LEGAL",
]

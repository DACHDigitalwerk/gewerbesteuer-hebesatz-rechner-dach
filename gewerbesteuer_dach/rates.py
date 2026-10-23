# -*- coding: utf-8 -*-
"""
gewerbesteuer_dach.rates
~~~~~~~~~~~~~~~~~~~~~~~~
Hebesätze deutscher Kommunen (Referenzwerte 2026) und gesetzliche Grenzwerte.
"""

from typing import Dict, List, Optional, Tuple

MIN_HEBESATZ_LEGAL = 200.0  # § 16 Abs. 4 Satz 2 GewStG (Mindesthebesatz bundesweit)
STEUERMESSZAHL = 0.035      # 3,5 % nach § 11 Abs. 2 GewStG
FREIBETRAG_PERSG = 24500.0  # 24.500 € nach § 11 Abs. 1 Satz 3 Nr. 1 GewStG
FREIBETRAG_FINANCING = 200000.0  # 200.000 € nach § 8 Nr. 1 GewStG
EST_ANRECHNUNG_FAKTOR = 4.0  # Faktor 4,0 nach § 35 EStG

# Kommunale Gewerbesteuer-Hebesätze 2026 (Auswahl wichtiger Städte & Steueroasen)
CITIES_HEBESATZ: Dict[str, float] = {
    # Metropolen & Großstädte
    "muenchen": 490.0,
    "münchen": 490.0,
    "frankfurt": 460.0,
    "frankfurt am main": 460.0,
    "koeln": 475.0,
    "köln": 475.0,
    "hamburg": 470.0,
    "berlin": 410.0,
    "stuttgart": 420.0,
    "duesseldorf": 440.0,
    "düsseldorf": 440.0,
    "leipzig": 460.0,
    "dresden": 450.0,
    "hannover": 480.0,
    "nuernberg": 447.0,
    "nürnberg": 447.0,
    "bremen": 460.0,
    "dortmund": 485.0,
    "essen": 480.0,
    "duisburg": 520.0,
    "oberhausen": 580.0,
    "muelheim": 580.0,
    "mülheim an der ruhr": 580.0,
    "bonn": 490.0,
    "mainz": 310.0,  # Mainz nach BioNTech-Senkung auf 310%
    "wiesbaden": 454.0,

    # Bekannte Gewerbesteueroasen / Niedrighebesatz-Standorte
    "gruenwald": 240.0,
    "grünwald": 240.0,
    "schoenefeld": 240.0,
    "schönefeld": 240.0,
    "leverkusen": 250.0,
    "monheim": 250.0,
    "monheim am rhein": 250.0,
    "zossen": 270.0,
    "norderfriedrichskoog": 200.0,  # Historischer Mindesthebesatz
}


def get_city_hebesatz(name: str) -> Optional[float]:
    """Sucht den Hebesatz einer Stadt (case-insensitive)."""
    norm = name.strip().lower()
    return CITIES_HEBESATZ.get(norm)


def list_benchmark_cities() -> List[Tuple[str, float]]:
    """Gibt eine sortierte Liste repräsentativer Benchmark-Kommunen zurück."""
    return [
        ("Grünwald (b. München)", 240.0),
        ("Monheim am Rhein", 250.0),
        ("Mainz (Rheinland-Pfalz)", 310.0),
        ("Berlin", 410.0),
        ("Stuttgart", 420.0),
        ("Düsseldorf", 440.0),
        ("Frankfurt am Main", 460.0),
        ("Hamburg", 470.0),
        ("Köln", 475.0),
        ("München", 490.0),
        ("Duisburg", 520.0),
        ("Oberhausen", 580.0),
    ]

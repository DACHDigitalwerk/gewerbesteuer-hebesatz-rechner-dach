# -*- coding: utf-8 -*-
"""
gewerbesteuer_dach.models
~~~~~~~~~~~~~~~~~~~~~~~~~
Datenmodelle und Datenklassen für Gewerbesteuer-Berechnung nach GewStG.
"""

from dataclasses import dataclass
from enum import Enum


class LegalForm(str, Enum):
    """Rechtsformen mit unterschiedlicher steuerlicher Behandlung."""
    EINZELUNTERNEHMEN = "einzelunternehmen"
    PERSONENGESELLSCHAFT = "personengesellschaft"  # OHG, KG, GbR, etc.
    KAPITALGESELLSCHAFT = "kapitalgesellschaft"    # GmbH, UG, AG, etc.


@dataclass
class FinancingAdditions:
    """
    Finanzierungsanteile nach § 8 Nr. 1 GewStG.
    Freibetrag: 200.000 € (seit Veranlagungszeitraum 2020/2026).
    """
    debt_interest: float = 0.0          # Schuldzinsen (25%)
    annuities_pensions: float = 0.0     # Renten & dauernde Lasten (25%)
    profit_shares_silent: float = 0.0   # Gewinnanteile stiller Gesellschafter (25%)
    rent_movable: float = 0.0           # Miet-/Pachtzinsen bewegliche Wirtschaftsgüter (20%)
    rent_immovable: float = 0.0         # Miet-/Pachtzinsen unbewegliche WG / Immobilien (50%)
    royalties_licenses: float = 0.0     # Konzessionen, Lizenzen, Markenrechte (25%)


@dataclass
class Reductions:
    """
    Kürzungen nach § 9 GewStG.
    """
    real_estate_standard: float = 0.0       # 1,2 % des Einheitswerts nach § 9 Nr. 1 Satz 1 GewStG
    profit_shares_partnerships: float = 0.0 # Anteile an PersG nach § 9 Nr. 2 GewStG
    foreign_permanent_est: float = 0.0      # Ausländische Betriebsstättengewinne nach § 9 Nr. 3 GewStG
    charitable_donations: float = 0.0       # Spenden nach § 9 Nr. 5 GewStG


@dataclass
class GewerbesteuerResult:
    """Ergebnis der normgerechten Gewerbesteuer-Berechnung."""
    profit_before_tax: float
    legal_form: LegalForm
    total_financing_raw: float
    financing_portions_sum: float
    financing_freibetrag: float
    taxable_additions: float
    total_reductions: float
    gewerbeertrag_raw: float
    gewerbeertrag_rounded: float
    freibetrag_applied: float
    gewerbeertrag_taxable: float
    steuermesszahl: float
    steuermessbetrag: float
    hebesatz_prozent: float
    gewerbesteuer_eur: float
    effective_tax_rate_prozent: float
    est_anrechnung_factor: float
    est_anrechnung_max_eur: float
    net_gewerbesteuer_after_est_eur: float

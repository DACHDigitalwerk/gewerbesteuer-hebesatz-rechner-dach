# -*- coding: utf-8 -*-
"""
gewerbesteuer_dach.calculator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Kern-Berechnungslogik für Gewerbesteuer, Freibeträge, Hinzurechnungen,
Kürzungen und die ESt-Anrechnung nach § 35 EStG.
"""

import math
from typing import List, Dict, Any, Optional
from .models import LegalForm, FinancingAdditions, Reductions, GewerbesteuerResult
from .validator import validate_inputs
from .rates import (
    STEUERMESSZAHL,
    FREIBETRAG_PERSG,
    FREIBETRAG_FINANCING,
    EST_ANRECHNUNG_FAKTOR,
    CITIES_HEBESATZ,
    list_benchmark_cities
)


def calculate_financing_additions(additions: Optional[FinancingAdditions]) -> tuple[float, float, float]:
    """
    Berechnet die Hinzurechnung nach § 8 Nr. 1 GewStG.
    Rückgabe: (Gesamter Rohaufwand, Summe der Finanzierungsanteile, Steuerpflichtige Hinzurechnung 25%)
    """
    if not additions:
        return 0.0, 0.0, 0.0

    raw_sum = (
        additions.debt_interest
        + additions.annuities_pensions
        + additions.profit_shares_silent
        + additions.rent_movable
        + additions.rent_immovable
        + additions.royalties_licenses
    )

    # Gesetzliche Anteile nach § 8 Nr. 1 Buchst. a bis f GewStG
    portion_sum = (
        1.00 * additions.debt_interest
        + 1.00 * additions.annuities_pensions
        + 1.00 * additions.profit_shares_silent
        + 0.20 * additions.rent_movable
        + 0.50 * additions.rent_immovable
        + 0.25 * additions.royalties_licenses
    )

    if portion_sum > FREIBETRAG_FINANCING:
        taxable_addition = 0.25 * (portion_sum - FREIBETRAG_FINANCING)
    else:
        taxable_addition = 0.0

    return round(raw_sum, 2), round(portion_sum, 2), round(taxable_addition, 2)


def calculate_reductions(reductions: Optional[Reductions]) -> float:
    """Berechnet die Gesamtsumme der Kürzungen nach § 9 GewStG."""
    if not reductions:
        return 0.0

    total = (
        reductions.real_estate_standard
        + reductions.profit_shares_partnerships
        + reductions.foreign_permanent_est
        + reductions.charitable_donations
    )
    return round(total, 2)


def calculate_gewerbesteuer(
    profit: float,
    legal_form: LegalForm = LegalForm.PERSONENGESELLSCHAFT,
    hebesatz: float = 400.0,
    additions: Optional[FinancingAdditions] = None,
    reductions: Optional[Reductions] = None,
) -> GewerbesteuerResult:
    """
    Vollständige Berechnung der Gewerbesteuer nach deutschem GewStG und EStG.
    """
    p_val, lf_val, heb_val = validate_inputs(profit, legal_form, hebesatz, additions, reductions)

    # 1. Hinzurechnungen (§ 8 GewStG)
    raw_fin, portion_fin, taxable_add = calculate_financing_additions(additions)

    # 2. Kürzungen (§ 9 GewStG)
    total_red = calculate_reductions(reductions)

    # 3. Vorläufiger Gewerbeertrag
    gewerbeertrag_raw = p_val + taxable_add - total_red
    if gewerbeertrag_raw < 0:
        gewerbeertrag_raw = 0.0

    # 4. Abrundung auf volle 100 Euro (§ 11 Abs. 1 Satz 3 GewStG)
    gewerbeertrag_rounded = float(math.floor(gewerbeertrag_raw / 100.0) * 100)

    # 5. Freibetrag (§ 11 Abs. 1 Satz 3 GewStG)
    if lf_val in (LegalForm.EINZELUNTERNEHMEN, LegalForm.PERSONENGESELLSCHAFT):
        freibetrag = min(FREIBETRAG_PERSG, gewerbeertrag_rounded)
    else:
        # Kapitalgesellschaften erhalten keinen Freibetrag
        freibetrag = 0.0

    gewerbeertrag_taxable = max(0.0, gewerbeertrag_rounded - freibetrag)

    # 6. Steuermessbetrag (Steuermesszahl 3,5 %)
    steuermessbetrag = round(gewerbeertrag_taxable * STEUERMESSZAHL, 2)

    # 7. Gewerbesteuer
    gewerbesteuer_eur = round(steuermessbetrag * (heb_val / 100.0), 2)

    # Effektiver Steuersatz bezogen auf Rohgewinn (falls Gewinn > 0)
    effective_rate = round((gewerbesteuer_eur / p_val * 100.0), 2) if p_val > 0 else 0.0

    # 8. ESt-Anrechnung nach § 35 EStG (Faktor 4,0 für natürliche Personen)
    if lf_val in (LegalForm.EINZELUNTERNEHMEN, LegalForm.PERSONENGESELLSCHAFT):
        est_factor = EST_ANRECHNUNG_FAKTOR
        est_anrechnung_theoretic = round(steuermessbetrag * est_factor, 2)
        # Gedeckelt auf die tatsächlich gezahlte Gewerbesteuer
        est_anrechnung_max = min(est_anrechnung_theoretic, gewerbesteuer_eur)
        net_tax = max(0.0, round(gewerbesteuer_eur - est_anrechnung_max, 2))
    else:
        # Kapitalgesellschaften können keine ESt-Ermäßigung nach § 35 EStG geltend machen
        est_factor = 0.0
        est_anrechnung_max = 0.0
        net_tax = gewerbesteuer_eur

    return GewerbesteuerResult(
        profit_before_tax=round(p_val, 2),
        legal_form=lf_val,
        total_financing_raw=raw_fin,
        financing_portions_sum=portion_fin,
        financing_freibetrag=FREIBETRAG_FINANCING,
        taxable_additions=taxable_add,
        total_reductions=total_red,
        gewerbeertrag_raw=round(gewerbeertrag_raw, 2),
        gewerbeertrag_rounded=gewerbeertrag_rounded,
        freibetrag_applied=freibetrag,
        gewerbeertrag_taxable=gewerbeertrag_taxable,
        steuermesszahl=STEUERMESSZAHL,
        steuermessbetrag=steuermessbetrag,
        hebesatz_prozent=heb_val,
        gewerbesteuer_eur=gewerbesteuer_eur,
        effective_tax_rate_prozent=effective_rate,
        est_anrechnung_factor=est_factor,
        est_anrechnung_max_eur=est_anrechnung_max,
        net_gewerbesteuer_after_est_eur=net_tax,
    )


def compare_municipalities(
    profit: float,
    legal_form: LegalForm = LegalForm.PERSONENGESELLSCHAFT,
    additions: Optional[FinancingAdditions] = None,
    reductions: Optional[Reductions] = None,
    cities: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Vergleicht die Gewerbesteuerbelastung und ESt-Anrechnung über verschiedene Kommunen.
    """
    if cities:
        city_list = []
        for c in cities:
            norm = c.strip().lower()
            heb = CITIES_HEBESATZ.get(norm, 400.0)
            city_list.append((c.title(), heb))
    else:
        city_list = list_benchmark_cities()

    results = []
    for city_name, hebesatz in city_list:
        res = calculate_gewerbesteuer(
            profit=profit,
            legal_form=legal_form,
            hebesatz=hebesatz,
            additions=additions,
            reductions=reductions,
        )
        results.append({
            "city": city_name,
            "hebesatz": hebesatz,
            "gewerbesteuer_eur": res.gewerbesteuer_eur,
            "steuermessbetrag": res.steuermessbetrag,
            "est_anrechnung_max_eur": res.est_anrechnung_max_eur,
            "net_gewerbesteuer_after_est_eur": res.net_gewerbesteuer_after_est_eur,
            "effective_tax_rate_prozent": res.effective_tax_rate_prozent,
        })

    return results

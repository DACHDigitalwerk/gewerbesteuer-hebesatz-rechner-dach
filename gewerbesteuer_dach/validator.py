# -*- coding: utf-8 -*-
"""
gewerbesteuer_dach.validator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Validierungslogik für Eingabewerte der Gewerbesteuerberechnung.
"""

from typing import Union
from .models import LegalForm, FinancingAdditions, Reductions
from .rates import MIN_HEBESATZ_LEGAL


class ValidationError(ValueError):
    """Fehler bei der Parameter-Validierung."""
    pass


def validate_inputs(
    profit: Union[int, float],
    legal_form: Union[str, LegalForm],
    hebesatz: Union[int, float],
    additions: FinancingAdditions = None,
    reductions: Reductions = None
) -> tuple[float, LegalForm, float]:
    """Validiert die grundlegenden Berechnungsparameter."""
    try:
        profit_val = float(profit)
    except (ValueError, TypeError):
        raise ValidationError(f"Ungültiger Gewinnwert: {profit}")

    if isinstance(legal_form, str):
        try:
            lf_val = LegalForm(legal_form.strip().lower())
        except ValueError:
            valid = [lf.value for lf in LegalForm]
            raise ValidationError(f"Ungültige Rechtsform: '{legal_form}'. Erlaubt: {valid}")
    elif isinstance(legal_form, LegalForm):
        lf_val = legal_form
    else:
        raise ValidationError(f"Ungültiger Rechtsform-Typ: {type(legal_form)}")

    try:
        hebesatz_val = float(hebesatz)
    except (ValueError, TypeError):
        raise ValidationError(f"Ungültiger Hebesatz: {hebesatz}")

    if hebesatz_val < MIN_HEBESATZ_LEGAL:
        raise ValidationError(
            f"Hebesatz {hebesatz_val}% liegt unter dem gesetzlichen Mindesthebesatz "
            f"von {MIN_HEBESATZ_LEGAL}% (§ 16 Abs. 4 Satz 2 GewStG)."
        )

    if additions:
        for field, val in [
            ("debt_interest", additions.debt_interest),
            ("annuities_pensions", additions.annuities_pensions),
            ("profit_shares_silent", additions.profit_shares_silent),
            ("rent_movable", additions.rent_movable),
            ("rent_immovable", additions.rent_immovable),
            ("royalties_licenses", additions.royalties_licenses),
        ]:
            if val < 0:
                raise ValidationError(f"Hinzurechnungswert '{field}' darf nicht negativ sein: {val}")

    if reductions:
        for field, val in [
            ("real_estate_standard", reductions.real_estate_standard),
            ("profit_shares_partnerships", reductions.profit_shares_partnerships),
            ("foreign_permanent_est", reductions.foreign_permanent_est),
            ("charitable_donations", reductions.charitable_donations),
        ]:
            if val < 0:
                raise ValidationError(f"Kürzungswert '{field}' darf nicht negativ sein: {val}")

    return profit_val, lf_val, hebesatz_val

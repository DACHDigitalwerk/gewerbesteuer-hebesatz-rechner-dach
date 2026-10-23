# -*- coding: utf-8 -*-
"""
Quickstart Example for gewerbesteuer_dach.
"""

from gewerbesteuer_dach import (
    calculate_gewerbesteuer,
    compare_municipalities,
    LegalForm,
    FinancingAdditions,
    Reductions
)

def main():
    print("=== Quickstart: DACH Gewerbesteuer- & Hebesatz-Rechner 2026 ===")

    # 1. Personengesellschaft in München (Hebesatz 490%)
    profit = 150000.0  # 150.000 € Gewinn
    res_m = calculate_gewerbesteuer(
        profit=profit,
        legal_form=LegalForm.PERSONENGESELLSCHAFT,
        hebesatz=490.0
    )
    print(f"\n1. Personengesellschaft (München 490%):")
    print(f"   Gewinn vor Steuern:   {res_m.profit_before_tax:,.2f} €")
    print(f"   Freibetrag (§ 11):    {res_m.freibetrag_applied:,.2f} €")
    print(f"   Steuermessbetrag:     {res_m.steuermessbetrag:,.2f} €")
    print(f"   Gewerbesteuer brutto: {res_m.gewerbesteuer_eur:,.2f} €")
    print(f"   § 35 EStG Ermäßigung: {res_m.est_anrechnung_max_eur:,.2f} €")
    print(f"   Netto-Steuerlast:     {res_m.net_gewerbesteuer_after_est_eur:,.2f} €")

    # 2. Vergleich mit Grünwald (Hebesatz 240%)
    res_g = calculate_gewerbesteuer(
        profit=profit,
        legal_form=LegalForm.PERSONENGESELLSCHAFT,
        hebesatz=240.0
    )
    print(f"\n2. Vergleich: Grünwald (Hebesatz 240%):")
    print(f"   Gewerbesteuer brutto: {res_g.gewerbesteuer_eur:,.2f} €")
    print(f"   § 35 EStG Ermäßigung: {res_g.est_anrechnung_max_eur:,.2f} €")
    print(f"   Netto-Steuerlast:     {res_g.net_gewerbesteuer_after_est_eur:,.2f} €")

    # 3. Kapitalgesellschaft (GmbH) mit § 8 Hinzurechnungen
    add = FinancingAdditions(debt_interest=300000.0) # 300.000 € Schuldzinsen
    res_gmbh = calculate_gewerbesteuer(
        profit=profit,
        legal_form=LegalForm.KAPITALGESELLSCHAFT,
        hebesatz=400.0,
        additions=add
    )
    print(f"\n3. Kapitalgesellschaft GmbH (Hebesatz 400% + § 8 Hinzurechnung):")
    print(f"   § 8 Hinzurechnung:    {res_gmbh.taxable_additions:,.2f} €")
    print(f"   Gewerbesteuer GmbH:   {res_gmbh.gewerbesteuer_eur:,.2f} €")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
gewerbesteuer_dach.cli
~~~~~~~~~~~~~~~~~~~~~~
Kommandozeilen-Interface (CLI) dach-gewerbesteuer.
Berechnet Gewerbesteuer, § 8 Hinzurechnungen, § 9 Kürzungen und § 35 EStG Entlastung.
"""

import sys
import json
import argparse
from typing import List, Optional
from .models import LegalForm, FinancingAdditions, Reductions
from .calculator import calculate_gewerbesteuer, compare_municipalities
from .rates import get_city_hebesatz, MIN_HEBESATZ_LEGAL, CITIES_HEBESATZ


def format_currency(val: float) -> str:
    """Formatiert Beträge im deutschen Währungsformat."""
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(val: float) -> str:
    """Formatiert Prozentwerte."""
    return f"{val:,.2f} %".replace(".", ",")


def generate_markdown_report(result) -> str:
    """Erzeugt einen druck- und prüffähigen DIN-A4 Markdown-Bericht."""
    md = []
    md.append("# Gewerbesteuer-Berechnungsnachweis 2026")
    md.append(f"**Rechtsform:** {result.legal_form.value.upper()} | **Hebesatz:** {format_percent(result.hebesatz_prozent)}")
    md.append("")
    md.append("## 1. Ausgangsdaten & Gewinn")
    md.append(f"- **Gewinn aus Gewerbebetrieb (§ 7 GewStG):** {format_currency(result.profit_before_tax)}")
    md.append("")
    md.append("## 2. Hinzurechnungen nach § 8 Nr. 1 GewStG")
    md.append(f"- Rohsumme aller Finanzierungsaufwendungen: {format_currency(result.total_financing_raw)}")
    md.append(f"- Gesetzliche Anteile (Zinsen 100%, Miete bew. 20%, unbew. 50%, Lizenz 25%): {format_currency(result.financing_portions_sum)}")
    md.append(f"- Gesetzlicher Freibetrag (§ 8 Nr. 1 Satz 1): {format_currency(result.financing_freibetrag)}")
    md.append(f"- **Steuerpflichtige Hinzurechnung (25 Prozent des Überhangs):** {format_currency(result.taxable_additions)}")
    md.append("")
    md.append("## 3. Kürzungen nach § 9 GewStG")
    md.append(f"- **Gesamtsumme Kürzungen:** {format_currency(result.total_reductions)}")
    md.append("")
    md.append("## 4. Ermittlung des Steuermessbetrags")
    md.append(f"- Maßgebender Gewerbeertrag (vor Abrundung): {format_currency(result.gewerbeertrag_raw)}")
    md.append(f"- Abgerundeter Gewerbeertrag (§ 11 Abs. 1 Satz 3): {format_currency(result.gewerbeertrag_rounded)}")
    md.append(f"- Freibetrag für Rechtsform (§ 11 Abs. 1): {format_currency(result.freibetrag_applied)}")
    md.append(f"- Steuerpflichtiger Gewerbeertrag: {format_currency(result.gewerbeertrag_taxable)}")
    md.append(f"- Steuermesszahl: {format_percent(result.steuermesszahl * 100)}")
    md.append(f"- **Steuermessbetrag (§ 11 Abs. 2):** {format_currency(result.steuermessbetrag)}")
    md.append("")
    md.append("## 5. Gewerbesteuer & § 35 EStG Steuerermäßigung")
    md.append(f"- **Festzusetzende Gewerbesteuer:** {format_currency(result.gewerbesteuer_eur)} (Effektiver Steuersatz: {format_percent(result.effective_tax_rate_prozent)})")
    if result.legal_form in (LegalForm.EINZELUNTERNEHMEN, LegalForm.PERSONENGESELLSCHAFT):
        md.append(f"- Anrechnungsfaktor nach § 35 EStG: {result.est_anrechnung_factor:.1f}x")
        md.append(f"- Maximaler ESt-Ermäßigungsbetrag: {format_currency(result.est_anrechnung_max_eur)}")
        md.append(f"- **Verbleibende Netto-Gewerbesteuerbelastung:** {format_currency(result.net_gewerbesteuer_after_est_eur)}")
    else:
        md.append("- *§ 35 EStG Ermäßigung entfällt für Kapitalgesellschaften (GmbH/UG).*")
    md.append("")
    md.append("---")
    md.append("*Erstellt mit DACH Digitalwerk Gewerbesteuer-Engine 2026. Rein technisches Berechnungsergebnis.*")
    return "\n".join(md)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dach-gewerbesteuer",
        description="DACH Gewerbesteuer- & Hebesatz-Rechner 2026 (100 Prozent DSGVO & Open-Source)."
    )

    parser.add_argument(
        "-p", "--profit",
        type=float,
        required=True,
        help="Vorlaeufiger Gewinn aus Gewerbebetrieb in Euro"
    )
    parser.add_argument(
        "-l", "--legal-form",
        choices=["einzelunternehmen", "personengesellschaft", "kapitalgesellschaft"],
        default="personengesellschaft",
        help="Rechtsform des Unternehmens"
    )
    parser.add_argument(
        "-H", "--hebesatz",
        type=float,
        default=None,
        help="Gewerbesteuer-Hebesatz der Gemeinde in Prozent (z.B. 490 fuer Muenchen)"
    )
    parser.add_argument(
        "-c", "--city",
        type=str,
        default=None,
        help="Gemeindename zur automatischen Hebesatz-Ermittlung (z.B. Muenchen, Gruenwald, Monheim)"
    )
    # § 8 Nr. 1 Finanzierungsaufwand
    parser.add_argument("--debt-interest", type=float, default=0.0, help="Schuldzinsen in Euro")
    parser.add_argument("--annuities", type=float, default=0.0, help="Renten und dauernde Lasten in Euro")
    parser.add_argument("--silent-shares", type=float, default=0.0, help="Gewinnanteile stiller Gesellschafter in Euro")
    parser.add_argument("--rent-movable", type=float, default=0.0, help="Miet- und Pachtzinsen bewegliche Wirtschaftsgüter in Euro (20 Prozent Anteil)")
    parser.add_argument("--rent-immovable", type=float, default=0.0, help="Miet- und Pachtzinsen unbewegliche WG / Immobilien in Euro (50 Prozent Anteil)")
    parser.add_argument("--royalties", type=float, default=0.0, help="Konzessionen und Lizenzen in Euro (25 Prozent Anteil)")

    # § 9 Kürzungen
    parser.add_argument("--reductions", type=float, default=0.0, help="Gesamtsumme der Kuerzungen nach Paragraph 9 GewStG in Euro")

    # Ausgabemodi
    parser.add_argument("-b", "--benchmark", action="store_true", help="Standort-Benchmark ueber repraesentative Staedte ausgeben")
    parser.add_argument("-j", "--json", action="store_true", help="Ausgabe als JSON-Objekt")
    parser.add_argument("-m", "--markdown", action="store_true", help="Druckfertigen Markdown-Bericht ausgeben")

    args = parser.parse_args(argv)

    # Hebesatz bestimmen
    if args.hebesatz is not None:
        hebesatz_val = args.hebesatz
    elif args.city:
        city_heb = get_city_hebesatz(args.city)
        if city_heb is not None:
            hebesatz_val = city_heb
        else:
            print(f"Hinweis: Gemeinde '{args.city}' nicht in Preset-Liste gefunden. Nutze Bundesdurchschnitt 400 Prozent.", file=sys.stderr)
            hebesatz_val = 400.0
    else:
        hebesatz_val = 400.0

    additions = FinancingAdditions(
        debt_interest=args.debt_interest,
        annuities_pensions=args.annuities,
        profit_shares_silent=args.silent_shares,
        rent_movable=args.rent_movable,
        rent_immovable=args.rent_immovable,
        royalties_licenses=args.royalties,
    )

    reductions = Reductions(
        real_estate_standard=args.reductions
    )

    legal_form = LegalForm(args.legal_form)

    if args.benchmark:
        bench_data = compare_municipalities(
            profit=args.profit,
            legal_form=legal_form,
            additions=additions,
            reductions=reductions,
        )
        if args.json:
            print(json.dumps(bench_data, indent=2, ensure_ascii=False))
            return 0
        print("\n=== GEWERBESTEUER STANDORT-BENCHMARK 2026 ===")
        print(f"Gewinn: {format_currency(args.profit)} | Rechtsform: {legal_form.value.upper()}\n")
        print(f"{'Stadt / Gemeinde':<26} | {'Hebesatz':<10} | {'Gewerbesteuer':<15} | {'Netto n. ESt':<15} | {'Eff. Satz':<10}")
        print("-" * 85)
        for b in bench_data:
            print(
                f"{b['city']:<26} | "
                f"{format_percent(b['hebesatz']):<10} | "
                f"{format_currency(b['gewerbesteuer_eur']):<15} | "
                f"{format_currency(b['net_gewerbesteuer_after_est_eur']):<15} | "
                f"{format_percent(b['effective_tax_rate_prozent']):<10}"
            )
        return 0

    res = calculate_gewerbesteuer(
        profit=args.profit,
        legal_form=legal_form,
        hebesatz=hebesatz_val,
        additions=additions,
        reductions=reductions,
    )

    if args.json:
        out = {
            "profit_before_tax": res.profit_before_tax,
            "legal_form": res.legal_form.value,
            "total_financing_raw": res.total_financing_raw,
            "financing_portions_sum": res.financing_portions_sum,
            "financing_freibetrag": res.financing_freibetrag,
            "taxable_additions": res.taxable_additions,
            "total_reductions": res.total_reductions,
            "gewerbeertrag_raw": res.gewerbeertrag_raw,
            "gewerbeertrag_rounded": res.gewerbeertrag_rounded,
            "freibetrag_applied": res.freibetrag_applied,
            "gewerbeertrag_taxable": res.gewerbeertrag_taxable,
            "steuermesszahl": res.steuermesszahl,
            "steuermessbetrag": res.steuermessbetrag,
            "hebesatz_prozent": res.hebesatz_prozent,
            "gewerbesteuer_eur": res.gewerbesteuer_eur,
            "effective_tax_rate_prozent": res.effective_tax_rate_prozent,
            "est_anrechnung_factor": res.est_anrechnung_factor,
            "est_anrechnung_max_eur": res.est_anrechnung_max_eur,
            "net_gewerbesteuer_after_est_eur": res.net_gewerbesteuer_after_est_eur,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    if args.markdown:
        print(generate_markdown_report(res))
        return 0

    # Standard-Terminal-Ausgabe
    print("\n" + "=" * 60)
    print("🏛️  DACH GEWERBESTEUER- & HEBESATZ-RECHNER 2026")
    print("=" * 60)
    print(f"Rechtsform               : {res.legal_form.value.upper()}")
    print(f"Gewinn vor Steuern       : {format_currency(res.profit_before_tax)}")
    if res.taxable_additions > 0:
        print(f"§ 8 Hinzurechnungen (25%): {format_currency(res.taxable_additions)} (Rohsumme: {format_currency(res.total_financing_raw)})")
    if res.total_reductions > 0:
        print(f"§ 9 Kürzungen            : {format_currency(res.total_reductions)}")
    print(f"Abgerundeter Ertrag      : {format_currency(res.gewerbeertrag_rounded)}")
    if res.freibetrag_applied > 0:
        print(f"Freibetrag (§ 11 Abs. 1) : {format_currency(res.freibetrag_applied)}")
    print(f"Steuerpfl. Gewerbeertrag : {format_currency(res.gewerbeertrag_taxable)}")
    print(f"Steuermessbetrag (3,5 %) : {format_currency(res.steuermessbetrag)}")
    print(f"Hebesatz                 : {format_percent(res.hebesatz_prozent)}")
    print("-" * 60)
    print(f"⚡ GEWERBESTEUER GESAMT   : {format_currency(res.gewerbesteuer_eur)}  ({format_percent(res.effective_tax_rate_prozent)} eff.)")
    if res.legal_form in (LegalForm.EINZELUNTERNEHMEN, LegalForm.PERSONENGESELLSCHAFT):
        print(f"§ 35 EStG Anrechnung (4x): {format_currency(res.est_anrechnung_max_eur)}")
        print(f"🎯 NETTO-STEUERBELASTUNG : {format_currency(res.net_gewerbesteuer_after_est_eur)}")
    else:
        print("Hinweis                  : Kapitalgesellschaften haben keinen Freibetrag und keine § 35 EStG Anrechnung.")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
import pytest
from gewerbesteuer_dach.models import LegalForm, FinancingAdditions, Reductions
from gewerbesteuer_dach.calculator import (
    calculate_gewerbesteuer,
    calculate_financing_additions,
    calculate_reductions,
    compare_municipalities
)
from gewerbesteuer_dach.validator import ValidationError
from gewerbesteuer_dach.rates import get_city_hebesatz, MIN_HEBESATZ_LEGAL


class TestFinancingAdditions:
    def test_additions_below_freibetrag(self):
        # 150.000 € Schuldzinsen -> portion sum 150.000 <= 200.000 -> 0 taxable
        add = FinancingAdditions(debt_interest=150000.0)
        raw, portions, taxable = calculate_financing_additions(add)
        assert raw == 150000.0
        assert portions == 150000.0
        assert taxable == 0.0

    def test_additions_above_freibetrag_debt_only(self):
        # 300.000 € Schuldzinsen -> portion 300.000 -> excess 100.000 -> 25% = 25.000 €
        add = FinancingAdditions(debt_interest=300000.0)
        raw, portions, taxable = calculate_financing_additions(add)
        assert raw == 300000.0
        assert portions == 300000.0
        assert taxable == 25000.0

    def test_additions_movable_rent(self):
        # 1.000.000 € Maschinenmiete -> 20% = 200.000 € -> exact threshold -> 0 taxable
        add = FinancingAdditions(rent_movable=1000000.0)
        raw, portions, taxable = calculate_financing_additions(add)
        assert raw == 1000000.0
        assert portions == 200000.0
        assert taxable == 0.0

    def test_additions_immovable_rent(self):
        # 600.000 € Gewerbemiete Immobilien -> 50% = 300.000 € -> excess 100.000 -> 25.000 € taxable
        add = FinancingAdditions(rent_immovable=600000.0)
        raw, portions, taxable = calculate_financing_additions(add)
        assert raw == 600000.0
        assert portions == 300000.0
        assert taxable == 25000.0

    def test_additions_royalties(self):
        # 1.200.000 € Lizenzen -> 25% = 300.000 € -> excess 100.000 -> 25.000 € taxable
        add = FinancingAdditions(royalties_licenses=1200000.0)
        raw, portions, taxable = calculate_financing_additions(add)
        assert raw == 1200000.0
        assert portions == 300000.0
        assert taxable == 25000.0

    def test_additions_none_or_empty(self):
        raw, portions, taxable = calculate_financing_additions(None)
        assert raw == 0.0 and portions == 0.0 and taxable == 0.0
        raw2, portions2, taxable2 = calculate_financing_additions(FinancingAdditions())
        assert raw2 == 0.0 and portions2 == 0.0 and taxable2 == 0.0


class TestReductions:
    def test_reductions_calculation(self):
        red = Reductions(
            real_estate_standard=5000.0,
            profit_shares_partnerships=12000.0,
            foreign_permanent_est=3000.0,
            charitable_donations=1000.0
        )
        assert calculate_reductions(red) == 21000.0

    def test_reductions_none(self):
        assert calculate_reductions(None) == 0.0


class TestGewerbesteuerCalculator:
    def test_personengesellschaft_below_freibetrag(self):
        # Gewinn 20.000 € -> unter 24.500 € Freibetrag -> Messbetrag 0 -> GewSt 0
        res = calculate_gewerbesteuer(20000.0, LegalForm.PERSONENGESELLSCHAFT, 400.0)
        assert res.freibetrag_applied == 20000.0
        assert res.gewerbeertrag_taxable == 0.0
        assert res.steuermessbetrag == 0.0
        assert res.gewerbesteuer_eur == 0.0
        assert res.net_gewerbesteuer_after_est_eur == 0.0

    def test_personengesellschaft_exact_freibetrag(self):
        # Gewinn 24.500 € -> Freibetrag 24.500 € -> 0 €
        res = calculate_gewerbesteuer(24500.0, LegalForm.PERSONENGESELLSCHAFT, 400.0)
        assert res.freibetrag_applied == 24500.0
        assert res.gewerbeertrag_taxable == 0.0
        assert res.gewerbesteuer_eur == 0.0

    def test_personengesellschaft_100k_hebesatz_400(self):
        # Gewinn 100.000 € -> Freibetrag 24.500 € -> Ertrag 75.500 €
        # Messbetrag = 75.500 * 3,5% = 2.642,50 €
        # GewSt = 2.642,50 * 400% = 10.570,00 €
        # § 35 EStG Anrechnung = 2.642,50 * 4,0 = 10.570,00 €
        # Netto GewSt = 0,00 € (vollständige Neutralisierung bei 400%)
        res = calculate_gewerbesteuer(100000.0, LegalForm.PERSONENGESELLSCHAFT, 400.0)
        assert res.gewerbeertrag_rounded == 100000.0
        assert res.freibetrag_applied == 24500.0
        assert res.gewerbeertrag_taxable == 75500.0
        assert res.steuermessbetrag == 2642.50
        assert res.gewerbesteuer_eur == 10570.00
        assert res.est_anrechnung_max_eur == 10570.00
        assert res.net_gewerbesteuer_after_est_eur == 0.00

    def test_personengesellschaft_hebesatz_above_400(self):
        # München (490 %): Hebesatz über 400% hinterlässt 90%-Punkte Netto-Belastung
        # Ertrag 75.500 € -> Messbetrag 2.642,50 €
        # GewSt = 2.642,50 * 4,90 = 12.948,25 €
        # ESt Anrechnung = 2.642,50 * 4,0 = 10.570,00 €
        # Netto = 12.948,25 - 10.570,00 = 2.378,25 €
        res = calculate_gewerbesteuer(100000.0, LegalForm.PERSONENGESELLSCHAFT, 490.0)
        assert res.gewerbesteuer_eur == 12948.25
        assert res.est_anrechnung_max_eur == 10570.00
        assert res.net_gewerbesteuer_after_est_eur == 2378.25

    def test_personengesellschaft_hebesatz_below_400(self):
        # Grünwald (240 %): Hebesatz unter 400%
        # GewSt = 2.642,50 * 2,40 = 6.342,00 €
        # ESt Anrechnung theoretisch 10.570,00 €, aber gedeckelt auf tatsächliche GewSt (6.342,00 €)
        # Netto = 0,00 €
        res = calculate_gewerbesteuer(100000.0, LegalForm.PERSONENGESELLSCHAFT, 240.0)
        assert res.gewerbesteuer_eur == 6342.00
        assert res.est_anrechnung_max_eur == 6342.00
        assert res.net_gewerbesteuer_after_est_eur == 0.00

    def test_kapitalgesellschaft_no_freibetrag_no_est(self):
        # GmbH / UG: Kein Freibetrag (0 €), volle 100.000 € steuerpflichtig
        # Messbetrag = 100.000 * 3,5% = 3.500,00 €
        # Bei Hebesatz 400%: GewSt = 3.500 * 4 = 14.000,00 €
        # § 35 EStG entfällt -> Netto = 14.000,00 €
        res = calculate_gewerbesteuer(100000.0, LegalForm.KAPITALGESELLSCHAFT, 400.0)
        assert res.freibetrag_applied == 0.0
        assert res.gewerbeertrag_taxable == 100000.0
        assert res.steuermessbetrag == 3500.00
        assert res.gewerbesteuer_eur == 14000.00
        assert res.est_anrechnung_factor == 0.0
        assert res.est_anrechnung_max_eur == 0.0
        assert res.net_gewerbesteuer_after_est_eur == 14000.00

    def test_abrundung_paragraph_11_abs_1_satz_3(self):
        # 123.489 € -> auf volle 100 € abgerundet = 123.400 €
        res = calculate_gewerbesteuer(123489.0, LegalForm.KAPITALGESELLSCHAFT, 400.0)
        assert res.gewerbeertrag_rounded == 123400.0
        assert res.gewerbeertrag_taxable == 123400.0

    def test_with_financing_additions_and_reductions(self):
        # Gewinn 100.000 €, Schuldzinsen 300.000 € (taxable additions 25.000 €), Kürzungen 10.000 €
        # Vorl. Ertrag = 100.000 + 25.000 - 10.000 = 115.000 €
        # KapG -> kein Freibetrag -> Ertrag 115.000 € -> Messbetrag = 115.000 * 3,5% = 4.025,00 €
        add = FinancingAdditions(debt_interest=300000.0)
        red = Reductions(real_estate_standard=10000.0)
        res = calculate_gewerbesteuer(100000.0, LegalForm.KAPITALGESELLSCHAFT, 400.0, additions=add, reductions=red)
        assert res.taxable_additions == 25000.0
        assert res.total_reductions == 10000.0
        assert res.gewerbeertrag_rounded == 115000.0
        assert res.steuermessbetrag == 4025.00
        assert res.gewerbesteuer_eur == 16100.00

    def test_loss_or_zero_profit(self):
        res = calculate_gewerbesteuer(0.0, LegalForm.PERSONENGESELLSCHAFT, 400.0)
        assert res.gewerbesteuer_eur == 0.0
        assert res.effective_tax_rate_prozent == 0.0

        res_neg = calculate_gewerbesteuer(-50000.0, LegalForm.PERSONENGESELLSCHAFT, 400.0)
        assert res_neg.gewerbeertrag_raw == 0.0
        assert res_neg.gewerbesteuer_eur == 0.0


class TestValidatorAndRates:
    def test_invalid_hebesatz_below_minimum(self):
        with pytest.raises(ValidationError, match="gesetzlichen Mindesthebesatz"):
            calculate_gewerbesteuer(50000.0, LegalForm.PERSONENGESELLSCHAFT, 199.0)

    def test_invalid_legal_form(self):
        with pytest.raises(ValidationError, match="Ungültige Rechtsform"):
            calculate_gewerbesteuer(50000.0, "stiftung", 400.0)

    def test_negative_addition_raises(self):
        with pytest.raises(ValidationError, match="nicht negativ"):
            calculate_gewerbesteuer(50000.0, LegalForm.PERSONENGESELLSCHAFT, 400.0, additions=FinancingAdditions(debt_interest=-100))

    def test_negative_reduction_raises(self):
        with pytest.raises(ValidationError, match="nicht negativ"):
            calculate_gewerbesteuer(50000.0, LegalForm.PERSONENGESELLSCHAFT, 400.0, reductions=Reductions(real_estate_standard=-50))

    def test_city_hebesatz_lookup(self):
        assert get_city_hebesatz("muenchen") == 490.0
        assert get_city_hebesatz("München") == 490.0
        assert get_city_hebesatz("Gruenwald") == 240.0
        assert get_city_hebesatz("Monheim am Rhein") == 250.0
        assert get_city_hebesatz("UnknownCityXYZ") is None

    def test_benchmark_municipalities(self):
        bench = compare_municipalities(100000.0, LegalForm.PERSONENGESELLSCHAFT)
        assert len(bench) >= 10
        gruenwald = next(b for b in bench if "Grünwald" in b["city"])
        assert gruenwald["hebesatz"] == 240.0
        assert gruenwald["net_gewerbesteuer_after_est_eur"] == 0.0
        muenchen = next(b for b in bench if b["city"] == "München")
        assert muenchen["hebesatz"] == 490.0
        assert muenchen["gewerbesteuer_eur"] > gruenwald["gewerbesteuer_eur"]

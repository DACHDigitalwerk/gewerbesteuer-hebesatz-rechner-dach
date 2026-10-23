# -*- coding: utf-8 -*-
import json
import pytest
from gewerbesteuer_dach.cli import main


class TestCLI:
    def test_cli_help(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0
        out, _ = capsys.readouterr()
        assert "dach-gewerbesteuer" in out
        assert "--profit" in out

    def test_cli_basic_run(self, capsys):
        code = main(["--profit", "100000", "--hebesatz", "400", "--legal-form", "personengesellschaft"])
        assert code == 0
        out, _ = capsys.readouterr()
        assert "GEWERBESTEUER GESAMT" in out
        assert "10.570,00 €" in out
        assert "NETTO-STEUERBELASTUNG" in out
        assert "0,00 €" in out

    def test_cli_json_output(self, capsys):
        code = main(["--profit", "80000", "--hebesatz", "450", "--legal-form", "kapitalgesellschaft", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["profit_before_tax"] == 80000.0
        assert data["legal_form"] == "kapitalgesellschaft"
        assert data["hebesatz_prozent"] == 450.0
        assert data["freibetrag_applied"] == 0.0
        assert data["gewerbeertrag_taxable"] == 80000.0
        assert data["steuermessbetrag"] == 2800.0  # 80000 * 0.035
        assert data["gewerbesteuer_eur"] == 12600.0 # 2800 * 4.5
        assert data["net_gewerbesteuer_after_est_eur"] == 12600.0

    def test_cli_markdown_output(self, capsys):
        code = main(["--profit", "120000", "--city", "muenchen", "--markdown"])
        assert code == 0
        out, _ = capsys.readouterr()
        assert "# Gewerbesteuer-Berechnungsnachweis 2026" in out
        assert "490,00 %" in out
        assert "§ 35 EStG" in out

    def test_cli_benchmark_output(self, capsys):
        code = main(["--profit", "200000", "--benchmark"])
        assert code == 0
        out, _ = capsys.readouterr()
        assert "GEWERBESTEUER STANDORT-BENCHMARK 2026" in out
        assert "Grünwald" in out
        assert "München" in out

    def test_cli_benchmark_json(self, capsys):
        code = main(["--profit", "200000", "--benchmark", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) >= 10
        assert any(d["city"] == "Berlin" for d in data)

    def test_cli_with_financing_additions(self, capsys):
        code = main([
            "--profit", "500000",
            "--hebesatz", "400",
            "--debt-interest", "100000",
            "--rent-immovable", "400000", # 50% = 200.000 -> portion sum 300.000 -> excess 100.000 -> 25.000 addition
            "--json"
        ])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["financing_portions_sum"] == 300000.0
        assert data["taxable_additions"] == 25000.0

    def test_cli_city_fallback(self, capsys):
        # Unknown city should print hint to stderr and fallback to 400%
        code = main(["--profit", "100000", "--city", "NonExistentCityXYZ", "--json"])
        assert code == 0
        out, err = capsys.readouterr()
        assert "Nutze Bundesdurchschnitt" in err
        data = json.loads(out)
        assert data["hebesatz_prozent"] == 400.0

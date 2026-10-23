# DACH Gewerbesteuer- & Hebesatz-Rechner 2026

[![Python Tests](https://github.com/DACHDigitalwerk/gewerbesteuer-hebesatz-rechner-dach/actions/workflows/python-tests.yml/badge.svg)](https://github.com/DACHDigitalwerk/gewerbesteuer-hebesatz-rechner-dach/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![100% DSGVO & Client-Side](https://img.shields.io/badge/Privacy-100%25%20Client--Side-brightgreen.svg)](https://dach-digitalwerk.netlify.app/gewerbesteuer-hebesatz-rechner/)

Normgerechte und prüffähige **Gewerbesteuer-Berechnung 2026** nach dem deutschen Gewerbesteuergesetz (GewStG) und Einkommensteuergesetz (§ 35 EStG).

> 🌐 **Kostenloses interaktives Browser-Tool:**  
> Nutzen Sie den sofort einsatzbereiten Web-Rechner mit Standort-Vergleich und druckfertigem DIN-A4 PDF-Berechnungsblatt direkt unter:  
> **[DACH Gewerbesteuer- & Hebesatz-Rechner 2026](https://dach-digitalwerk.netlify.app/gewerbesteuer-hebesatz-rechner/)**

---

## 🚀 Highlights & Features

- **Rechtsform-spezifische Freibeträge (§ 11 Abs. 1 GewStG):**
  - Einzelunternehmen & Personengesellschaften: **24.500 € Freibetrag**.
  - Kapitalgesellschaften (GmbH, UG, AG): **0 € Freibetrag**.
  - Automatische Abrundung des Gewerbeertrags auf volle 100 Euro (§ 11 Abs. 1 Satz 3 GewStG).
- **Finanzierungs-Hinzurechnungen nach § 8 Nr. 1 GewStG:**
  - Schuldzinsen & Renten: 100 %
  - Miet-/Pachtaufwand bewegliche Wirtschaftsgüter: 20 %
  - Miet-/Pachtaufwand unbewegliche Wirtschaftsgüter / Immobilien: 50 %
  - Lizenzen & Konzessionen: 25 %
  - **Freibetrag von 200.000 €**: Nur der übersteigende Betrag wird zu 25 % hinzugerechnet.
- **Kürzungen nach § 9 GewStG:**
  - 1,2 % des Einheitswerts des Grundbesitzes (§ 9 Nr. 1).
  - Gewinnanteile an Personengesellschaften (§ 9 Nr. 2).
  - Ausländische Betriebsstättengewinne (§ 9 Nr. 3).
- **Steuerermäßigung bei Einkommensteuer (§ 35 EStG):**
  - Faktor **4,0** auf den Steuermessbetrag für natürliche Personen und Personengesellschafter.
  - Vollständige Neutralisierung der Gewerbesteuer bis zu einem Hebesatz von **400 %**.
  - Gedeckelt auf die tatsächlich gezahlte Gewerbesteuer.
- **Standort-Benchmark deutscher Kommunen:**
  - Enthält aktuelle Hebesätze von Metropolen (München 490%, Frankfurt 460%, Köln 475%, Berlin 410%) bis zu Gewerbesteueroasen (Grünwald 240%, Monheim 250%, Mainz 310%).
- **Druckfertiger Berechnungsnachweis:**
  - Erstellt vollständige, revisionssichere Nachweise für Steuerberater und Betriebsprüfung.

---

## 📦 Installation

```bash
pip install git+https://github.com/DACHDigitalwerk/gewerbesteuer-hebesatz-rechner-dach.git
```

Oder im Entwicklungsmodus klonen:

```bash
git clone https://github.com/DACHDigitalwerk/gewerbesteuer-hebesatz-rechner-dach.git
cd gewerbesteuer-hebesatz-rechner-dach
pip install -e .
```

---

## 💻 CLI-Nutzung (`dach-gewerbesteuer`)

### 1. Schnellberechnung für Personengesellschaft

```bash
dach-gewerbesteuer --profit 100000 --city muenchen --legal-form personengesellschaft
```

Ausgabe:
```text
============================================================
🏛️  DACH GEWERBESTEUER- & HEBESATZ-RECHNER 2026
============================================================
Rechtsform               : PERSONENGESELLSCHAFT
Gewinn vor Steuern       : 100.000,00 €
Abgerundeter Ertrag      : 100.000,00 €
Freibetrag (§ 11 Abs. 1) : 24.500,00 €
Steuerpfl. Gewerbeertrag : 75.500,00 €
Steuermessbetrag (3,5 %) : 2.642,50 €
Hebesatz                 : 490,00 %
------------------------------------------------------------
⚡ GEWERBESTEUER GESAMT   : 12.948,25 €  (12,95 % eff.)
§ 35 EStG Anrechnung (4x): 10.570,00 €
🎯 NETTO-STEUERBELASTUNG : 2.378,25 €
============================================================
```

### 2. Standort-Benchmark deutscher Kommunen

```bash
dach-gewerbesteuer --profit 150000 --benchmark
```

### 3. Mit § 8 Hinzurechnungen (Schuldzinsen & Immobilienmiete)

```bash
dach-gewerbesteuer --profit 500000 --hebesatz 400 --debt-interest 100000 --rent-immovable 400000
```

### 4. JSON-Export für Buchhaltungs-Pipelines

```bash
dach-gewerbesteuer --profit 80000 --hebesatz 440 --legal-form kapitalgesellschaft --json
```

---

## 🐍 Python API

```python
from gewerbesteuer_dach import (
    calculate_gewerbesteuer,
    compare_municipalities,
    LegalForm,
    FinancingAdditions,
    Reductions
)

# Berechnung für Einzelunternehmen
res = calculate_gewerbesteuer(
    profit=120000.0,
    legal_form=LegalForm.EINZELUNTERNEHMEN,
    hebesatz=420.0
)

print(f"Gewerbesteuer: {res.gewerbesteuer_eur} €")
print(f"ESt-Anrechnung (§ 35): {res.est_anrechnung_max_eur} €")
print(f"Netto-Steuerbelastung: {res.net_gewerbesteuer_after_est_eur} €")
```

---

## 🧪 Tests

```bash
pytest -v
```

Alle 31+ Unit-Tests decken gesetzliche Grenzfälle, Rundungsvorschriften, Hinzurechnungsgrenzen und CLI-Funktionen ab.

---

## ⚖️ Rechtlicher Hinweis & Haftungsausschluss

Dieses Software-Tool und die zugrundeliegenden Skripte dienen ausschließlich der **technischen Simulation und Information**. Es handelt sich hierbei um **keine Rechts- oder Steuerberatung** im Sinne des Rechtsdienstleistungsgesetzes (§ 2 RDG) oder des Steuerberatungsgesetzes (§ 5 StBerG). Das Tool ersetzt nicht die individuelle Prüfung durch einen Steuerberater oder Wirtschaftsprüfer. Weitere Angaben: [AGB](https://dach-digitalwerk.netlify.app/agb/) | [Haftungsausschluss](https://dach-digitalwerk.netlify.app/haftungsausschluss/).

---

## 📄 Lizenz

Veröffentlicht unter der [MIT License](LICENSE).  
Copyright (c) 2026 **DACH Digitalwerk**.

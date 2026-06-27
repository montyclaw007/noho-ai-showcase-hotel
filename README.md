# nøho · AI-Showcase (Hotel / Finca) — Mehrsprachiger Buchungs-Anfragen-Bot

Dritter Branchen-Showcase für die Akquise: eine Boutique-Finca-Landingpage
(„Es Jardí", Sóller) mit Chat-Widget, das Buchungsanfragen **automatisch auf
Deutsch, English und Español** beantwortet, qualifiziert (Unterkunftstyp,
Gästezahl, Reisezeitraum, Kontakt) und live „ans CRM" übergibt.

Aufbau identisch zu den anderen Showcases — nur Persona, Häuser und Lead-Logik getauscht.
Helles, erdiges Boutique-Design (Papier + Olive + Terracotta) als bewusster Kontrast
zu Immobilien (Teal/Gold) und Yacht (Navy/Champagne).

## Zwei Betriebsarten

**Demo-Modus (kein Setup):** `index.html` doppelklicken. Eingebaute mehrsprachige
Logik, Badge „Demo-Modus". Zum Screensharen / Verschicken.

**Live-KI (Claude Opus 4.8):**
```bash
cd ~/Developer/noho-ai-showcase-hotel
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python3 server.py     # → http://localhost:8000
```

> Nur die statische Demo gehört ins öffentliche Netz — `server.py` ist ein
> kostenpflichtiger Claude-Endpunkt und bleibt lokal.

## Verkaufs-Talking-Points (Hospitality)

- „Buchungsanfragen werden rund um die Uhr, in drei Sprachen, sofort beantwortet — auch nachts."
- „Jede Anfrage kommt vorqualifiziert: Unterkunft, Gäste, Reisezeitraum, Kontakt."
- „Kein verlorener Gast mehr, weil die Antwort erst zwei Tage später kam."

_Demo-Objekt von nøho studio. Fiktive Häuser, fiktive Agentur._

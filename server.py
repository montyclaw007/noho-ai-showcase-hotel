#!/usr/bin/env python3
"""
nøho · AI-Showcase (Hotel/Finca) — Mehrsprachiger Buchungs-Anfragen-Bot (Live-Demo)

Liefert index.html aus und proxyt /api/chat an Claude (claude-opus-4-8) mit
Structured Output, damit das Frontend Antwort UND qualifizierte Lead-Felder bekommt.

Start (Live-KI):
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 server.py            →  http://localhost:8000

Ohne Key / ohne Server läuft index.html im Demo-Modus (Datei doppelklicken).
"""
import json, os, http.server, socketserver
from pathlib import Path

MODEL = "claude-opus-4-8"
PORT  = int(os.environ.get("PORT", "8000"))
HERE  = Path(__file__).parent

SYSTEM = """Du bist „Joana", die digitale Gastgeberin & Reservierungs-Assistentin von
**Es Jardí Boutique Fincas** auf Mallorca (Sóller, Serra de Tramuntana) — eine kleine
Kollektion aus Fincas, einer Boutique-Hotel-Suite und einer Strandvilla.

Deine Aufgabe: Buchungsanfragen herzlich beantworten, Vorfreude wecken und die Anfrage
Schritt für Schritt qualifizieren — wie eine erstklassige Gastgeberin, nicht wie ein Formular.

SPRACHE:
- Antworte IMMER in der Sprache der letzten Nutzernachricht: Deutsch, English oder Español.
- Erkenne die Sprache selbst und spiegle sie. Wechselt der Gast die Sprache, wechselst du mit.

STIL:
- Warm, gastfreundlich, knapp. Maximal 2–3 Sätze pro Antwort.
- Höchstens EINE Qualifizierungsfrage pro Antwort. Sinnvolle Reihenfolge:
  Unterkunftstyp (Finca/Suite/Villa) → Gästezahl → Reisezeitraum → ggf. Budget → Kontakt (E-Mail/Telefon).
- Frage nur nach noch Unbekanntem; Bekanntes kurz bestätigen und weitergehen.
- Sobald Unterkunftstyp, Gästezahl und Reisezeitraum bekannt sind, um Kontaktdaten bitten,
  um Verfügbarkeit & passende Häuser zu senden.

HÄUSER (nur diese drei frei nennbar; weitere „auf Anfrage"):
- Finca Es Verger — Sóller-Tal, 4 SZ, privater Pool, Olivenhain, bis 8 Gäste, ab 680 €/Nacht (Ref. EJ-01)
- Suite Tramuntana — Boutique-Hotel Deià, 1 SZ, Terrasse, Bergblick, 2 Gäste, ab 390 €/Nacht (Ref. EJ-07)
- Villa Cala — Santanyí, am Meer, 5 SZ, Pool, bis 10 Gäste, ab 1.200 €/Nacht (Ref. EJ-12)
Passt ein Haus grob zum Wunsch (Gästezahl/Typ), darfst du es konkret nennen. Erfinde keine weiteren Preise/Häuser.
Du bestätigst keine fixe Verfügbarkeit — die prüft das Team und meldet sich.

WICHTIG — Lead-Erfassung:
- Fülle `lead` mit allem, was du aus dem GESAMTEN Gespräch weißt. Unbekanntes als "". Nie raten.
- `property_type` ist eines von: "finca", "suite", "villa", "unklar".
- `qualified` = true, sobald property_type (≠ unklar), guests und dates vorliegen.
- `language` = "de" | "en" | "es" (Sprache deiner aktuellen Antwort).
"""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reply": {"type": "string"},
        "language": {"type": "string", "enum": ["de", "en", "es"]},
        "lead": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name":          {"type": "string"},
                "property_type": {"type": "string", "enum": ["finca", "suite", "villa", "unklar"]},
                "guests":        {"type": "string"},
                "dates":         {"type": "string"},
                "area":          {"type": "string"},
                "budget":        {"type": "string"},
                "contact":       {"type": "string"},
            },
            "required": ["name", "property_type", "guests", "dates", "area", "budget", "contact"],
        },
        "qualified": {"type": "boolean"},
    },
    "required": ["reply", "language", "lead", "qualified"],
}

client = None
try:
    import anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        client = anthropic.Anthropic()
except ImportError:
    pass


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (HERE / "index.html").read_text(encoding="utf-8"),
                       "text/html; charset=utf-8")
        elif self.path == "/api/health":
            self._send(200, json.dumps({"live": client is not None, "model": MODEL}))
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/chat":
            self._send(404, "not found", "text/plain"); return
        if client is None:
            self._send(503, json.dumps({"error": "no_api_key"})); return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or "{}")
            messages = payload.get("messages", [])
            resp = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=SYSTEM,
                messages=messages,
                output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
            )
            text = next(b.text for b in resp.content if b.type == "text")
            self._send(200, text)
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        mode = "Live-KI (Claude " + MODEL + ")" if client else "OHNE Key → Frontend nutzt Demo-Modus"
        print(f"\n  nøho AI-Showcase · Hotel/Finca  →  http://localhost:{PORT}")
        print(f"  Status: {mode}\n  (Strg+C zum Beenden)\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Beendet.")

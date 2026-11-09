# Dienstag-Companion

Lokale, offlinefähige Spielleitungs-App für **Die Stadt, die den Dienstag verkaufte**.

## Kanonischer Inhalt

Die App-Version `0.1.0` ist fest mit dem veröffentlichten Abenteuerpaket `v2.1-rc1` verbunden. Persönliche Sitzungsstände werden getrennt im lokalen App-Speicher gesichert. Ein späteres Abenteuer-Release erhält ein neues, unveränderliches Inhaltspaket; `main` ist ausdrücklich keine Inhaltsquelle.

## Enthalten

- Dashboard und Zeitplan für zwei Abende sowie One-Shot
- acht interaktive Szenen
- vier offene Countdowns
- NSC- und Gegner*innen-Dossiers mit Portraits
- HP- und Stressverwaltung für Gegner*innen
- Handout-Freigaben und spoilerarme Spielendenansicht
- Szenennotizen, Gruppennotizen und lokaler Autosave
- Schnellreferenz und mögliche Enden

## Entwicklung

Voraussetzungen: Rust stable, `wasm32-unknown-unknown`, Trunk, Node.js und die [Tauri-Systemvoraussetzungen](https://v2.tauri.app/start/prerequisites/).

```powershell
npm install
npm run dev
npm run build
```

Die App fordert keine Netzwerk- oder Dateisystemrechte an. Alle Sitzungsdaten bleiben im lokalen WebView-Speicher.


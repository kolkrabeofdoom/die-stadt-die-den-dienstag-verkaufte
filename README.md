# Die Stadt, die den Dienstag verkaufte

![Eine vielfältige Gruppe blickt über das regennasse, von Straßenbahnen und Uhrwerken geprägte Veyra](assets/illustrationen/cover_readme.jpg)

Ein illustriertes Daggerheart-Abenteuer für vier Figuren auf Stufe 1 und zwei Spielabende von jeweils ungefähr vier Stunden.

Veyra hat den Dienstag verkauft. Die Körper arbeiten weiter, die bewusste Erinnerung fehlt, und das Chronokonsortium zieht Zinsen aus Lebenszeit. Die Gruppe entscheidet nicht nur, ob der Tag zurückkehrt, sondern wem Zeit überhaupt gehören darf. Eine völlig normale kommunalpolitische Kleinigkeit mit Straßenbahn.

## Aktueller Stand

**Release Candidate 1, Fassung 2.1**

[Vollständiges RC1-Austauschpaket herunterladen](https://github.com/kolkrabeofdoom/die-stadt-die-den-dienstag-verkaufte/releases/tag/v2.1-rc1)

Die aktuelle Fassung enthält:

- acht spielbereite Szenen;
- NSC- und Gegner*innen-Dossiers;
- Daggerheart-Profile für Stufe 1;
- Countdowns, Karten und mehrere Enden;
- eine Vier-Stunden-One-Shot-Variante;
- elf Handouts;
- Portraits, Aufsteller und VTT-Material;
- einen simulierten Zwei-Abende-Testlauf.

### Companion-App für die Spielleitung

**Aktuelle App-Version: 0.1.0 für Windows**

Die lokale App bündelt Szenen, Countdowns, NSC- und Gegner*innen-Dossiers,
Trefferpunkte- und Stressverwaltung, Handout-Freigaben, Sitzungsnotizen, Enden
und einen spoilerarmen Spielendenmodus. Sie arbeitet vollständig offline und
ist unveränderlich an den geprüften Inhalt von `v2.1-rc1` gebunden. Der Dienstag
kann also verschwinden, das WLAN darf bleiben.

- [Release und Installationshinweise](https://github.com/kolkrabeofdoom/die-stadt-die-den-dienstag-verkaufte/releases/tag/companion-v0.1.0)
- [Windows-Installer herunterladen](https://github.com/kolkrabeofdoom/die-stadt-die-den-dienstag-verkaufte/releases/download/companion-v0.1.0/Die_Stadt_die_den_Dienstag_verkaufte_Companion_v0_1_0_Setup.exe)
- [Portable Windows-App herunterladen](https://github.com/kolkrabeofdoom/die-stadt-die-den-dienstag-verkaufte/releases/download/companion-v0.1.0/Die_Stadt_die_den_Dienstag_verkaufte_Companion_v0_1_0_portable.exe)
- [SHA-256-Prüfsummen](https://github.com/kolkrabeofdoom/die-stadt-die-den-dienstag-verkaufte/releases/download/companion-v0.1.0/SHA256SUMS-companion-v0.1.0.txt)
- [Quellcode und Bauanleitung](companion-app/README.md)

> [!NOTE]
> Die Programme sind nicht kommerziell codesigniert. Windows kann deshalb beim
> ersten Start eine Sicherheitswarnung anzeigen.

## Schnellzugriff

### Für die Spielleitung

> [!WARNING]
> Die folgenden Dokumente enthalten vollständige Lösungen, Gegner*innenprofile, Countdowns und mögliche Enden. Spielende sollten diesen Bereich meiden. Der Dienstag ist bereits verschwunden; die Überraschungen müssen ihm nicht folgen.

- [Releasebegleiter](docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Releasebegleiter_RC1_v2_1.pdf)
- [Spielleitungsheft](docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Spielleitungsheft_RC1_v2_1.pdf)
- [Gesamtausgabe](docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Gesamtausgabe_RC1_v2_1.pdf)
- [Leitungsschnellreferenz](docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Leitungsschnellreferenz_v1_0.pdf)
- [Szenenkarten](docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Szenenkarten_v1_0.pdf)
- [Aufstellerbogen](docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Aufstellerbogen_v1_0.pdf)

### Für Spielende

- [Spoilerarmes Spielendenpaket](docs/spielende/Die_Stadt_die_den_Dienstag_verkaufte_Spielendenpaket_RC1_v2_1.pdf)
- [Spielendensichere Stadtkarte von Veyra](docs/spielende/Veyra_Stadtkarte_spielendensicher_v1_0.png)

Das Spielendenpaket enthält keine Leitungsnotizen. Einzelne Handouts sollten dennoch erst in ihrer vorgesehenen Szene geöffnet werden. Spoilerfreiheit ist schließlich kein Naturzustand, sondern gemeinschaftliche Infrastruktur.

## Empfohlener Einstieg

Für die Spielleitung:

1. `docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Releasebegleiter_RC1_v2_1.pdf`
2. `docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Spielleitungsheft_RC1_v2_1.pdf`
3. Schnellreferenz und Szenenkarten aus demselben Ordner

Für Spielende sollte ausschließlich der Ordner `docs/spielende` geteilt werden.

## Verzeichnisstruktur

```text
assets/
  handouts/           Bildhandouts
  illustrationen/     Karten, Cover und Szenengrafiken
  portraits/          NSC- und Gegner*innen-Portraits
docs/
  spielleitung/       Hauptheft, Gesamtausgabe und Leitungswerkzeuge
  spielende/          spoilergetrenntes Paket und öffentliche Stadtkarte
src/                  reproduzierbare Python-Bauskripte
companion-app/        quelloffene Rust-App für die Spielleitung
outputs/              lokal gebaute Windows-Artefakte
```

Die vollständige ZIP-Ausgabe mit 80 transparenten VTT-Token wird als GitHub Release veröffentlicht und nicht zusätzlich in der normalen Git-Historie gespeichert.

## Mitarbeit

Siehe [CONTRIBUTING.md](CONTRIBUTING.md). Änderungen erfolgen bevorzugt über kurze Arbeitszweige und Pull Requests. Größere Eingriffe in Zeitlogik, Regeln oder Szenenstruktur sollten begründet und anhand der Konsistenzprüfung kontrolliert werden.

## Technischer Hinweis

Binäre Dokumente und Bilder werden mit Git LFS verwaltet. Nach dem Klonen wird daher Git LFS benötigt:

```bash
git lfs install
git lfs pull
```

## Rechte, Lizenz und Fanprojektstatus

Die eigenen Projektinhalte stehen unter CC BY-SA 4.0; Daggerheart-SRD-Anteile werden getrennt unter
der Darrington Press Community Gaming License verwendet. Dies ist ein unabhängiges, nicht offiziell
unterstütztes Fanprojekt. Daggerheart ist eine Marke von Critical Role, LLC. Maßgeblich sind die
ausführlichen Hinweise in [RECHTE.md](RECHTE.md).

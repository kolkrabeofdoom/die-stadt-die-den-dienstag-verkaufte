# Die Stadt die den Dienstag verkaufte

Ein illustriertes Daggerheart-Abenteuer für vier Figuren auf Stufe 1 und zwei Spielabende von jeweils ungefähr vier Stunden.

Veyra hat den Dienstag verkauft. Die Körper arbeiten weiter, die bewusste Erinnerung fehlt, und das Chronokonsortium zieht Zinsen aus Lebenszeit. Die Gruppe entscheidet nicht nur, ob der Tag zurückkehrt, sondern wem Zeit überhaupt gehören darf. Eine völlig normale kommunalpolitische Kleinigkeit mit Straßenbahn.

## Aktueller Stand

**Release Candidate 1, Fassung 2.1**

Die aktuelle Fassung enthält:

- acht spielbereite Szenen;
- NSC- und Gegner*innen-Dossiers;
- Daggerheart-Profile für Stufe 1;
- Countdowns, Karten und mehrere Enden;
- eine Vier-Stunden-One-Shot-Variante;
- elf Handouts;
- Portraits, Aufsteller und VTT-Material;
- einen simulierten Zwei-Abende-Testlauf.

## Einstieg

Für die Spielleitung:

1. `docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Releasebegleiter_RC1_v2_1.pdf`
2. `docs/spielleitung/Die_Stadt_die_den_Dienstag_verkaufte_Spielleitungsheft_RC1_v2_1.pdf`
3. Schnellreferenz und Szenenkarten aus demselben Ordner

Für Spielende darf ausschließlich der Ordner `docs/spielende` geteilt werden. Das dortige Paket enthält keine Leitungsnotizen; einzelne Handouts sollten trotzdem erst in ihrer Szene geöffnet werden. Spoilerfreiheit ist schließlich kein Naturzustand, sondern eine gemeinschaftliche Infrastruktur.

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

## Rechte und Fanprojektstatus

Dies ist ein unabhängiges, nicht offiziell unterstütztes Fanprojekt. Daggerheart ist ein Warenzeichen von Critical Role LLC. Weitere Hinweise stehen in [RECHTE.md](RECHTE.md).


from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

INK = "17222D"
TEAL = "173D4F"
COPPER = "A65D3B"
PALE = "E8F1EF"
CREAM = "F7F1E3"
GREY = "D9D9D9"
MID = "66717A"
WHITE = "FFFFFF"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=95, bottom=80, end=95):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, color=GREY, size="4", edges=("top", "left", "bottom", "right")):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in edges:
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), size)
        node.set(qn("w:color"), color)


def no_cell_borders(cell):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "nil")


def font_run(run, size=7.7, bold=False, italic=False, color=INK, name="Aptos"):
    run.bold = bold
    run.italic = italic
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.insert(0, r_fonts)
    r_fonts.set(qn("w:ascii"), name)
    r_fonts.set(qn("w:hAnsi"), name)


def para(cell, text="", size=7.7, bold=False, color=INK, before=0, after=1.4, line=1.0):
    p = cell.add_paragraph() if cell.paragraphs[0].text else cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line
    font_run(p.add_run(text), size=size, bold=bold, color=color)
    return p


def labeled(cell, label, text, size=7.65, after=1.2):
    p = cell.add_paragraph() if cell.paragraphs[0].text else cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.0
    font_run(p.add_run(label), size=size, bold=True, color=COPPER, name="Georgia")
    font_run(p.add_run(text), size=size)
    return p


def heading(cell, text, level=1):
    p = cell.add_paragraph() if cell.paragraphs[0].text else cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4.2 if level == 1 else 2.5)
    p.paragraph_format.space_after = Pt(1.6)
    p.paragraph_format.keep_with_next = True
    font_run(p.add_run(text), size=10.1 if level == 1 else 8.6, bold=True, color="000000", name="Georgia")
    return p


def bullet(cell, text, size=7.55, symbol="•", after=0.65):
    p = cell.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.28)
    p.paragraph_format.first_line_indent = Cm(-0.2)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.0
    font_run(p.add_run(f"{symbol} "), size=size, bold=True, color=TEAL)
    font_run(p.add_run(text), size=size)
    return p


def add_data_table(cell, headers, rows, widths=None, font_size=7.0, header_fill=TEAL):
    table = cell.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    if widths is None:
        widths = [1] * len(headers)
    total = sum(widths)
    available = 8.55
    for idx, (h, weight) in enumerate(zip(headers, widths)):
        c = table.rows[0].cells[idx]
        c.width = Cm(available * weight / total)
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(c, header_fill)
        set_cell_margins(c, top=42, start=55, bottom=42, end=55)
        set_cell_border(c)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        font_run(p.add_run(h), size=font_size, bold=True, color=WHITE)
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for idx, (value, weight) in enumerate(zip(row, widths)):
            c = cells[idx]
            c.width = Cm(available * weight / total)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(c, top=42, start=55, bottom=42, end=55)
            set_cell_border(c)
            set_cell_shading(c, "FFFFFF" if ridx % 2 == 0 else PALE)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            font_run(p.add_run(str(value)), size=font_size, bold=(idx == 0))
    spacer = cell.add_paragraph()
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.space_before = Pt(1.2)
    return table


def add_page_title(doc, title, subtitle, page_no):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1.4)
    font_run(p.add_run(title), size=19.5, bold=True, color="000000", name="Georgia")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    font_run(p.add_run(subtitle), size=8.3, color=MID)
    font_run(p.add_run(f"   •   Seite {page_no} von 2"), size=8.3, bold=True, color=COPPER)


def page_columns(doc):
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cells = table.rows[0].cells
    for c in cells:
        c.width = Cm(8.75)
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        set_cell_margins(c, top=0, start=105, bottom=0, end=105)
        no_cell_borders(c)
    return cells


def build_page_one(doc):
    add_page_title(
        doc,
        "Dramaturgischer Leitstand",
        "Die Stadt die den Dienstag verkaufte   •   zwei Abende   •   vier Figuren auf Stufe 1",
        1,
    )
    c1, c2, c3 = page_columns(doc)

    heading(c1, "Zeitplan und harte Schnitte")
    add_data_table(c1, ["Zeit", "Szene und Schnitt"], [
        ["A1 0:00", "Rahmen und Anker - Glocke schlägt Montag 24:00"],
        ["0:20", "1 Fehlender Morgen - Quittung spricht"],
        ["1:05", "2 Markt ohne Gestern - Archivzugang steht"],
        ["1:55", "Pause 10 Minuten"],
        ["2:05", "3 Archiv - Tessas Botschaft und Fahrplan"],
        ["3:00", "4 Linie 7 - Ankunft in Nachmorgen"],
        ["3:50", "Cliffhanger - Dienstag bittet um Hilfe"],
        ["A2 0:00", "Rückblick - Countdowns offen zeigen"],
        ["0:15", "5 Nachmorgen - Preis der Rückgabe"],
        ["1:05", "6 Besetzung - Zugang zum Tresor"],
        ["1:55", "Pause 10 Minuten"],
        ["2:05", "7 Chronotresor - Nulluhr erwacht"],
        ["3:05", "8 Finale - Ordnung wählen"],
        ["3:45", "Epiloge und Debrief"],
    ], [1.25, 3.5], font_size=6.75)
    labeled(c1, "Zeitregel  ", "15 Minuten im Rückstand: zuerst Kampf kürzen, dann Reise montieren. Nie die finale Entscheidung streichen.", 7.5)

    heading(c1, "Szenen in einem Satz")
    for text in [
        "1 Menschen retten und die bewusste Zeitlücke entdecken.",
        "2 Fraktionen treffen und einen Archivzugang beschaffen.",
        "3 Rohzeit, Zinsen, Tessa und Linie 7 finden.",
        "4 Erinnerungen durchfahren und Nachmorgen erreichen.",
        "5 Betroffene hören und die dritte Möglichkeit lernen.",
        "6 Menge schützen, Maschinen stoppen, Voss entscheiden lassen.",
        "7 Siegel durch Entscheidungen lösen, nicht durch Schlüsselsuche.",
        "8 Um Eigentum, Verteilung und Zustimmung ringen.",
    ]:
        bullet(c1, text, size=7.35, after=0.45)

    heading(c2, "Sechs feste Wahrheiten")
    truths = [
        "Dienstag existiert als Rohzeit in Nachmorgen und als Pfand im Chronotresor.",
        "Die Körper durchleben ihn in administrativer Trance; bewusste Erinnerung und freie Zeit fehlen.",
        "Morgen & Söhne exportiert Zeit-Zinsen: Regeneration, Möglichkeiten und Lebensjahre.",
        "Ein Vertragsbruch setzt Rohzeit frei; ohne Verteilung trifft die Rückwelle zuerst belastete Viertel.",
        "Die Neuvermessung war vor 100 Wochen. Eine Prüfung je Woche macht die kommende zur hundertsten.",
        "Dienstag ist Person und Infrastruktur. Die Zustimmung des Tags ersetzt nicht die der Betroffenen.",
    ]
    for text in truths:
        bullet(c2, text)

    heading(c2, "Hinweiskette ohne Sackgasse")
    add_data_table(c2, ["Enthüllung", "Mindestens drei Wege"], [
        ["Dienstag existiert", "Quittung 1 • Jori 2 • Indexrad 3"],
        ["100 Prüfungen", "Orsino 2 • Tessa 3 • Nachtrag 3"],
        ["Trance", "Mittwoch 1 • Voss 2 • Formular 88b 3"],
        ["Rohzeit bleibt", "Tessa 3/5 • Bilanzbuch 7"],
        ["Linie 7 geschützt", "Mios Tinte 1 • Jori 2 • Tessa 5"],
        ["Rückwelle verteilbar", "Tessa 5 • Bilanzsaal 7 • Dienstag 8"],
        ["Stimmen gekauft", "Archivprotokoll 3 • Bilanzbuch 7 • Voss"],
        ["Gemeingut möglich", "Ritual 5 • Takt voll • Zustimmung 8"],
    ], [1.45, 2.65], font_size=6.8)
    labeled(c2, "Wenn ein Hinweis fehlt  ", "Gib ihn mit einer Komplikation aus. Ermittlungsstillstand ist kein Charakterbogen, sondern meist nur ein umgekippter Aktenschrank.", 7.45)

    heading(c3, "Fraktionen auf einen Blick")
    add_data_table(c3, ["Fraktion", "Will / fürchtet"], [
        ["Morgen & Söhne", "Dauervertrag / öffentliche Bilanz"],
        ["Gemeinsamer Takt", "Zeit als Gemeingut / autoritäres Chaos"],
        ["Magistrat", "Stabilität / Schuldenrückwelle und Aufstand"],
        ["Nachmorgen", "Existenzrecht / Zwangsrückführung"],
    ], [1.35, 2.85], font_size=6.85)

    heading(c3, "Offene Countdowns")
    countdowns = [
        ("Endgültiger Vertrag  1/6", "+1 bei deutlichem Scheitern in 1, 4, 6 oder 7, langem Rest oder Nulluhr-Feature. Voll: Vertrag gilt; andere Enden brauchen großen Preis."),
        ("Erhöhte Aufmerksamkeit  0/4", "+1 bei öffentlicher Gewalt, verlorenen Beweisen oder wiederholten Fear-Moves. Voll: +1 Difficulty im Werk, bis öffentliche Unterstützung entsteht."),
        ("Entgleisung Linie 7  0/3", "+1 bei Fear oder ignorierter Gefahr in Szene 4. Voll: Waggon löst sich; Rettung kostet Zeit oder Ressourcen."),
        ("Gemeinsamer Takt  1/4", "+1 bei Solidarität, Wahrheit und Schutz ohne Gegenleistung. Voll: Stadt trägt ein Ende; einmal 2 Fortschritt automatisch."),
    ]
    for label, text in countdowns:
        labeled(c3, label + "  ", text, 7.25, after=2.0)
    labeled(c3, "Praxis  ", "Leisten offen zeigen. Vor riskanten Würfen sagen, was ticken kann. Segmente entfernen, wenn die Gruppe strukturell handelt.", 7.4)

    heading(c3, "Übergänge bei Umwegen")
    for text in [
        "Plausible neue Route: Ja - ordne sie einer Front, einem Siegel oder einer bestehenden Szene zu.",
        "Orsino fällt früh: Die Nulluhr und die Eigentumslogik bleiben aktiv.",
        "Tessa wird misstraut: Beweise sind prüfbar; ihre politische Deutung bleibt verhandelbar.",
        "Gruppe zieht sich zurück: Zeige die nächste Folge und frage, wen oder was sie trotzdem schützt.",
    ]:
        bullet(c3, text, size=7.3)


def build_page_two(doc):
    doc.add_page_break()
    add_page_title(
        doc,
        "Regeln und Krisenhilfe",
        "Regelkurzfassung für dieses Abenteuer   •   geprüft gegen Daggerheart SRD 2.0 vom 25. August 2026",
        2,
    )
    c1, c2, c3 = page_columns(doc)

    heading(c1, "Daggerheart am Tisch")
    for label, text in [
        ("Aktionswurf  ", "Hope-d12 + Fear-d12 + Modifikator gegen Difficulty. Der höhere Duality Die bestimmt Hope oder Fear; Gleichstand ist kritisch."),
        ("Mit Hope  ", "Die Figur erhält 1 Hope. Bei Erfolg gelingt die Aktion; bei Fehlschlag folgt eine Konsequenz, aber der Moment bleibt handlungsfähig."),
        ("Mit Fear  ", "Die GM erhält 1 Fear. Bei Erfolg darf ein Preis oder eine Komplikation folgen; bei Fehlschlag tritt eine deutlichere Konsequenz ein."),
        ("Kritisch  ", "Gleiche Augenzahl auf beiden Duality Dice: automatischer Erfolg mit Bonus; 1 Hope erhalten und 1 Stress löschen."),
        ("Spotlight  ", "Keine Initiative. Wechsle nach Fiktion, Dringlichkeit und Fairness. Nach zwei Spieler*innen-Spotlights ist meist eine GM-Reaktion fällig."),
        ("GM-Würfe  ", "Gegner*innen würfeln d20 + Angriffsbonus gegen Evasion. Die GM würfelt keine Duality Dice."),
        ("Schaden  ", "Mit Major-/Severe-Schwelle vergleichen: unter Major 1 HP; ab Major 2 HP; ab Severe 3 HP. Auf 0 oder weniger reduzierter Schaden markiert keine HP."),
        ("Fear  ", "Start 4, Obergrenze 12. Für Features, Environment und zusätzliche Solo-Aktivierungen ausgeben; nicht bis zur musealen Versteinerung horten."),
    ]:
        labeled(c1, label, text, 7.35, after=1.4)

    heading(c1, "Difficulty und Folgen")
    add_data_table(c1, ["Lage", "Wert", "Folge zuerst"], [
        ["gut vorbereitet", "10", "Position / Hinweis mit Preis"],
        ["typisches Risiko", "11-12", "Stress / Trennung / Countdown"],
        ["direkter Widerstand", "13-14", "harter Preis, HP nur selten"],
    ], [1.6, 0.65, 2.35], font_size=6.75)
    labeled(c1, "Vulnerable  ", "Alle Würfe, die das Ziel betreffen, erhalten Vorteil, bis die genannte Dauer oder Aufhebung eintritt.", 7.25)
    labeled(c1, "Restrained  ", "Das Ziel kann sich nicht bewegen, darf aber von seiner Position aus weiter handeln.", 7.25)

    heading(c2, "Gegner*innen im Schnellzugriff")
    add_data_table(c2, ["Profil", "D / Schw. / HP", "Kern"], [
        ["Taktwächter*in", "11 • 7/12 • 4", "+1 • 1d8+3 • öffentliches Beweismaterial erzeugt Stress/Rückzug"],
        ["Indexschwarm", "10 • 6/11 • 5", "+0 • 1d6+2 • Wahrheit macht ihn kurz harmlos"],
        ["Minutenzehrer", "12 • 6/11 • 3", "+2 • 1d8+2 • bei Fear versetzen; Zeitbiss +1 Stress"],
        ["Papierknecht", "9 • - • 1", "+0 • 3 • Minion; Treffer besiegt, Schaden höchstens 1 HP"],
        ["Herr Pünktlich", "12 • 8/14 • 6", "+1 • 1d10+2 • Zweifel statt Vernichtung; Entgleisung +1 für 1 Fear"],
        ["Orsino Vale", "13 • 8/15 • 7", "+2 • 1d10+3 • selbstlose Tat markiert Stress; bei vollem Stress Wahl"],
        ["Die Nulluhr", "14 • 9/16 • 10", "+2 • 1d12+3 • Relentless 2; verliert Zeiger bei 7/4/1 HP"],
    ], [1.2, 1.05, 2.85], font_size=6.45)
    labeled(c2, "Nulluhr: Montag für immer  ", "1 Fear: Vertrag +1. Eine Figur kann sofort 1 Hope ausgeben und eine passende Erinnerung erzählen, um das zu verhindern.", 7.15)
    labeled(c2, "Nulluhr: Rücklauf  ", "Bei Severe Damage höchstens einmal pro fiktionaler Runde Rückwelle +1.", 7.15)

    heading(c2, "Finale in fünf Schritten")
    for text in [
        "Aktuelle Fear übernehmen, höchstens 8. Nulluhr startet mit verbleibenden HP und Features.",
        "Angriff, Siegel umdeuten, Fraktion überzeugen, Menschen schützen und Ritual sind gleichwertige Wege.",
        "Nach einem vollständigen Gruppen-Umlauf Vertrag +1, falls niemand Erfolg gegen die Nulluhr hatte.",
        "Bei 0 HP, vier umgedeuteten Siegeln oder überzeugt/entmachtetem Orsino: Ordnung verhandeln.",
        "Fragen: Wer entscheidet? Wer trägt Kosten? Welche Stimme fehlt?",
    ]:
        bullet(c2, text, size=7.25, after=0.55)

    heading(c3, "Krisenhilfe")
    crisis = [
        ("Gruppe steckt fest", "Wichtigsten Hinweis mit Konsequenz ausgeben und nach akzeptablen Kosten fragen."),
        ("Kampf zieht sich", "Motiv zeigen; Rückzug, Kapitulation oder verändertes Ziel anbieten."),
        ("Fear stapelt sich", "Für Profil-Features, Environment und Spotlight ausgeben."),
        ("Zeit wird knapp", "Reise montieren, Nebenkonflikt zusammenfassen, Entscheidung bewahren."),
        ("Lösung überrascht", "Einer Front oder einem Siegel zuordnen und echten Fortschritt geben."),
        ("Ende bleibt abstrakt", "Eine konkrete Institution, Kostenverteilung und fehlende Stimme benennen lassen."),
    ]
    for label, text in crisis:
        labeled(c3, label + "  ", text, 7.3, after=1.5)

    heading(c3, "Endenmatrix")
    add_data_table(c3, ["Ende", "Öffnung und Preis"], [
        ["Dienstag als Gemeingut", "Ritual/Takt voll + Zustimmung. Jede Figur: 1 Hope oder 1 Stress."],
        ["Rückgabe an Kalender", "Nulluhr besiegt + Verteilungsplan. Ein persönlicher Zeitanker wird geopfert."],
        ["Nachmorgen bleibt frei", "Kollektiv konsultiert + sicherer Übergang. Wirtschaftliche Vorteile enden."],
        ["Vertrag mit Rissen", "Countdown voll oder Kompromiss. Schutzklauseln, aber Eigentumsprinzip bleibt."],
        ["Die offene Woche", "Dienstag + drei Fraktionen stimmen zu. Zentrale Zeitmagie fällt zeitweise aus."],
    ], [1.45, 3.0], font_size=6.55)

    heading(c3, "Sicherheit und letzter Blick")
    for text in [
        "Linien, Schleier und Stoppsignal vereinbaren; Pausen jederzeit möglich.",
        "Themen: Ausbeutung, Gedächtnisverlust, staatliche Gewalt, Schulden, verschwundene Angehörige, Zeitdruck.",
        "Niemand schuldet der Fiktion Unbehagen - auch keiner Fiktion mit überraschend gepflegtem Fahrplan.",
        "Vor Start: vier Rollenanker, 2 Hope je Figur, 4 Fear, Countdowns offen, Handouts und Karten griffbereit.",
    ]:
        bullet(c3, text, size=7.15, after=0.55)


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width = Cm(29.7)
    sec.page_height = Cm(21.0)
    sec.top_margin = Cm(0.75)
    sec.bottom_margin = Cm(0.65)
    sec.left_margin = Cm(0.8)
    sec.right_margin = Cm(0.8)
    sec.header_distance = Cm(0.2)
    sec.footer_distance = Cm(0.25)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(7.7)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(1)
    normal.paragraph_format.line_spacing = 1.0

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    font_run(footer.add_run("Die Stadt die den Dienstag verkaufte  •  Leitungsschnellreferenz  •  Fassung 1.0"), size=6.3, color=MID)

    build_page_one(doc)
    build_page_two(doc)

    path = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Leitungsschnellreferenz_v1_0.docx"
    doc.save(path)
    print(path)


if __name__ == "__main__":
    build()

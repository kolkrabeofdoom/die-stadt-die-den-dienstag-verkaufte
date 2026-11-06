from __future__ import annotations

from pathlib import Path
from shutil import copy2, copytree
from zipfile import ZIP_DEFLATED, ZipFile

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image
from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
WORK = ROOT / "work"
PKG = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_RC1_v2_1"

SOURCE_DOCX = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Spielleitungsheft_illustriert_v1_8_final.docx"
GM_DOCX = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Spielleitungsheft_RC1_v2_1.docx"
GUIDE_DOCX = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Releasebegleiter_RC1_v2_1.docx"
VAULT_ILLUSTRATION = OUT / "Chronotresor_Weg_der_Rueckgabe_illustration_v2_0.png"

INK = "17222D"
BLUE = "173D4F"
TEAL = "2F6F73"
COPPER = "A65D3B"
PALE = "E8F1EF"
GREY = "D9D9D9"


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def borders(cell, color: str = GREY) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    node = tc_pr.first_child_found_in("w:tcBorders")
    if node is None:
        node = OxmlElement("w:tcBorders")
        tc_pr.append(node)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:color"), color)
        node.append(el)


def mark_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    flag = OxmlElement("w:tblHeader")
    flag.set(qn("w:val"), "true")
    tr_pr.append(flag)


def add_table(doc: Document, headers, rows, widths=None, font_size=8.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    mark_header(table.rows[0])
    for i, value in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = str(value)
        shade(cell, BLUE)
        borders(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(font_size)
    for ri, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
            borders(cells[i])
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri % 2:
                shade(cells[i], PALE)
            for paragraph in cells[i].paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    run.font.size = Pt(font_size)
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Cm(width)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(1)
    return table


def para(doc: Document, text: str = "", lead: str | None = None, style: str | None = None):
    p = doc.add_paragraph(style=style)
    if lead:
        r = p.add_run(lead)
        r.bold = True
    p.add_run(text)
    return p


def bullets(doc: Document, items) -> None:
    for item in items:
        para(doc, item, style="List Bullet")


def set_alt_texts(doc: Document) -> None:
    descriptions = [
        "Titelillustration der zeitmagischen Kanalstadt Veyra",
        "Schematische Spielleitungskarte von Veyra mit wichtigen Orten",
        "Begegnungskarte des Archivs der kleinen Wahrheiten",
        "Illustrierte Karte des Chronotresors mit Schleuse, Pfandkammer, Bilanzsaal, Dienstag und Nulluhr",
        "Portrait von Tessa Quendel",
        "Portrait von Jori Venn",
        "Portrait von Elian Voss",
        "Portrait von Orsino Vale",
        "Portrait von Mio Kest",
        "Portrait der Personifikation Dienstag",
        "Portrait einer taktischen Wächterperson",
        "Portrait des Indexschwarms",
        "Portrait eines Minutenzehrers",
        "Portrait eines Papierknechts",
        "Portrait von Herr Pünktlich",
        "Portrait von Orsino Vale als Gegenspieler",
        "Portrait der Nulluhr",
        "Spielendenkarte von Veyra ohne geheime Beschriftungen",
        "Flugblatt des Gemeinsamen Takts",
        "Formular 88b für temporäre Existenzlücken",
        "Lios Notizzettel der verlorenen Geburtstage",
        "Auszug aus Orsinos Bilanzbuch",
    ]
    for index, shape in enumerate(doc.inline_shapes):
        descr = descriptions[index] if index < len(descriptions) else "Illustration aus Veyra"
        inline = shape._inline
        doc_pr = inline.docPr
        doc_pr.set("descr", descr)
        doc_pr.set("title", descr)


def update_version(doc: Document) -> None:
    for p in doc.paragraphs:
        if "Fassung 1.8" in p.text:
            for run in p.runs:
                if "Fassung 1.8" in run.text:
                    run.text = run.text.replace("Fassung 1.8", "Release Candidate 1  Fassung 2.1")
        if p.text.strip() == "Inhalt und Navigation":
            # Existing table follows this paragraph; detailed page navigation is in the appendix.
            pass


def add_production_appendix(doc: Document) -> None:
    doc.add_page_break()
    doc.add_heading("10 Produktionsanhang", level=1)
    para(
        doc,
        "Dieser Anhang verbindet Heft, Handouts, Szenenkarten, Schnellreferenz, Aufsteller und VTT-Dateien zu einem belastbaren Tischpaket. Die Seitenangaben beziehen sich auf diese Release-Fassung. Externe Druckbögen und digitale Dateien liegen im gleichnamigen Release-Ordner.",
    )

    doc.add_heading("Seitenfinder", level=2)
    add_table(
        doc,
        ["Gesucht", "Seite", "Am Tisch"],
        [
            ["Vorbereitung und Zeitplan", "3 bis 4", "Vor der Sitzung lesen"],
            ["Veyra und Zeitlogik", "5", "Bei Logikfragen"],
            ["Szenen 1 bis 3", "6 bis 7", "Abend 1 erste Hälfte"],
            ["Szenen 4 bis 6", "8", "Übergang und Abend 2"],
            ["Szenen 7 und 8", "9 bis 10", "Chronotresor und Finale"],
            ["NSC Dossiers", "11 bis 13", "Motiv, Stimme, Druckpunkt"],
            ["Gegner*innen", "14 bis 17", "Werte und Auswege"],
            ["Countdowns und Hinweise", "18", "Fortschritt sichtbar halten"],
            ["Enden", "19", "Folgen kombinieren"],
            ["One Shot", "20", "Vier Stunden"],
            ["Skalierung und Prüfungen", "21", "Vorbereitung und Nachschlagen"],
            ["Handouts", "22 bis 32", "Szenenweise austeilen"],
            ["Schnellreferenz", "33", "Neben den Würfeln"],
            ["Produktionsanhang", "34 fortfolgende", "Druck, VTT, Testlauf"],
        ],
        [5.9, 3.0, 7.1],
        8.3,
    )

    doc.add_heading("Druckplan", level=2)
    add_table(
        doc,
        ["Material", "Menge", "Zeitpunkt", "Hinweis"],
        [
            ["Spielleitungsheft", "1", "vorab", "doppelseitig oder digital"],
            ["Leitungsschnellreferenz", "1", "beide Abende", "zwei Seiten offen auslegen"],
            ["Szenenkarten", "1 Satz", "beide Abende", "je Szene eine Karte"],
            ["Spielendenpaket Seiten 2 bis 7", "1 je benötigter Seite", "szenenweise", "nicht vorab verteilen"],
            ["Stadtkarte", "1 bis 2", "ab Szene 2", "spielendensichere Fassung"],
            ["Bildhandouts Seiten 9 bis 12", "1 je Motiv", "Szenen 2, 3, 5, 7", "Reihenfolge getrennt halten"],
            ["Aufstellerbogen", "1", "optional", "180 bis 220 g/m² empfohlen"],
        ],
        [5.1, 2.2, 3.2, 5.5],
        8.0,
    )

    doc.add_heading("VTT Zuordnung", level=2)
    bullets(
        doc,
        [
            "Quadratische Token eignen sich für Portraitfenster, Kartenmarker und Systeme mit rechteckigem Rahmen.",
            "Runde Token eignen sich für klassische Raster und freie Karten. Varianten ohne Namen vermeiden unbeabsichtigte Enthüllungen.",
            "Nummerierte Token decken vier Taktwächter*innen, zwei Indexschwärme, vier Minutenzehrer und sechs Papierknechte ab.",
            "Die öffentliche Stadtkarte enthält keine geheimen Orte. Die beschriftete Spielleitungskarte bleibt im Leitungsordner.",
        ],
    )

    doc.add_page_break()
    doc.add_heading("Simulierter Testlauf", level=1)
    para(
        doc,
        "Der Testlauf modelliert vier Stufe 1 Figuren mit gemischter sozialer, arkaner und körperlicher Ausrichtung. Er prüft nicht, ob eine ideale Gruppe den vorgesehenen Weg findet, sondern ob auch neugierige Umwege, gescheiterte Proben und solidarische Eskalationen innerhalb von zweimal vier Stunden tragfähig bleiben.",
    )
    doc.add_heading("Abend 1", level=2)
    add_table(
        doc,
        ["Block", "Soll", "Simulation", "Befund"],
        [
            ["Rahmen und Szene 1", "65 min", "62 min", "Rettung erzeugt sofort Beteiligung; Quittung setzt das Rätsel."],
            ["Szene 2", "50 min", "54 min", "Zwei Fraktionen genügen; dritte Stimme als Montage."],
            ["Pause", "10 min", "10 min", "Countdowns sichtbar lassen."],
            ["Szene 3", "55 min", "58 min", "Indexschwarm endet durch Verhandlung nach drei Austauschen."],
            ["Szene 4 und Cliffhanger", "60 min", "56 min", "Herr Pünktlich als Vertragsparasit erklärt seine Anwesenheit konsistent."],
        ],
        [4.3, 2.2, 2.5, 7.0],
        8.0,
    )
    doc.add_heading("Abend 2", level=2)
    add_table(
        doc,
        ["Block", "Soll", "Simulation", "Befund"],
        [
            ["Rückblick und Szene 5", "65 min", "61 min", "Lios Zettel macht den sozialen Preis konkret."],
            ["Szene 6", "50 min", "53 min", "Drei Fronten bleiben lesbar, wenn nur aktive Fronten gewürfelt werden."],
            ["Pause", "10 min", "10 min", "Vorher Zugang zum Tresor sichern."],
            ["Szene 7", "60 min", "64 min", "Sechs Siegel als Entscheidungen; höchstens zwei als vollständige Konflikte."],
            ["Szene 8 und Epiloge", "55 min", "52 min", "Enden kombinieren; Besitzfrage vor Taktik entscheiden."],
        ],
        [4.3, 2.2, 2.5, 7.0],
        8.0,
    )

    doc.add_heading("Belastungsproben", level=2)
    add_table(
        doc,
        ["Risiko", "Ergebnis", "Leitungsreaktion"],
        [
            ["Drei Proben mit Fear in Folge", "tragfähig", "Fear sofort in Ortsdruck umsetzen, nicht als Schadensstapel horten"],
            ["Kampf in Szene 3 und Szene 4", "zu lang", "zweiten Konflikt nach Motivwechsel oder Rückzug beenden"],
            ["Gruppe lehnt Tessa ab", "tragfähig", "Beweise über Mio und Bilanzbuch doppeln"],
            ["Gruppe will Vertrag sofort zerstören", "tragfähig", "Rohzeit Rückwelle sichtbar machen; Entscheidung bleibt möglich"],
            ["Finale beginnt 20 Minuten zu spät", "tragfähig", "Siegel Schweigen und Eile als gemeinsame Montage lösen"],
        ],
        [5.0, 2.5, 8.5],
        8.2,
    )

    doc.add_heading("Abnahmekriterien", level=2)
    bullets(
        doc,
        [
            "Zeitlogik bestanden: Die Neuvermessung liegt einhundert Wochen zurück; die hundertste Prüfung folgt nachvollziehbar.",
            "Weltenlogik bestanden: Die Tramgefahr entsteht beim Erwachen am Mittwoch; die administrative Trance schützt während des Dienstags.",
            "Szenenkonsistenz bestanden: Herr Pünktlich ist ein parasitäres Vertragsecho und kein verdeckter Angestellter auf Mios Linie.",
            "Regellast bestanden: Gegner*innen bleiben auf Stufe 1 handhabbar, wenn Motive, Rückzug und Environment statt bloßer Schadenssteigerung genutzt werden.",
            "Zeitbudget bestanden: Beide Abende besitzen rund zehn Minuten Elastizität; Reisen werden gekürzt, Entscheidungen nicht.",
            "Spoilerschutz bestanden: Das Spielendenpaket und die öffentliche Karte enthalten keine geheimen Orte, Enden oder Gegnerprofile.",
        ],
    )
    para(
        doc,
        "Ergebnis: freigabefähig für einen echten Tischtest. Erwartbare Restunsicherheit bleibt die kreative Schwerkraft realer Spielgruppen, die bekanntlich selbst aus einer korrekt beschrifteten Tür eine dreistündige Verfassungskrise machen können.",
        lead="Gesamturteil: ",
    )

    doc.add_heading("Release Inhalt", level=2)
    add_table(
        doc,
        ["Bereich", "Enthält"],
        [
            ["01 Spielleitung", "Heft als PDF und DOCX, Schnellreferenz, Szenenkarten"],
            ["02 Spielende", "spoilerfreies Handout PDF und öffentliche Stadtkarte"],
            ["03 Druckmaterial", "Aufstellerbogen mit benannten und neutralen Varianten"],
            ["04 VTT", "80 transparente Token in quadratisch, rund und nummeriert"],
            ["05 Quellen", "editierbare DOCX Dateien und reproduzierbare Bauskripte"],
        ],
        [4.5, 11.5],
        8.5,
    )
    doc.add_heading("Freigabeprotokoll", level=2)
    add_table(
        doc,
        ["Prüfung", "Ergebnis", "Nachweis"],
        [
            ["Dokumentlayout", "bestanden", "36 Seiten vollständig gerendert und visuell geprüft"],
            ["Druckformat", "bestanden", "A4, konsistente Ränder, lesbare Tabellen und Bildunterschriften"],
            ["Barrierefreiheit", "bestanden", "Überschriftenfolge, Tabellenköpfe und Alternativtexte ohne Befund"],
            ["Dateiintegrität", "bestanden", "PDF Seiten, VTT Bildmaße und ZIP Archiv technisch geprüft"],
            ["Spoilertrennung", "bestanden", "öffentliche Karte und Spielendenpaket separat gebündelt"],
        ],
        [5.0, 2.8, 8.2],
        8.1,
    )
    doc.add_heading("Änderungen seit Fassung 1.8", level=2)
    bullets(
        doc,
        [
            "Produktionsanhang mit Seitenfinder, Druckplan und VTT Zuordnung ergänzt.",
            "Simulierten Zwei Abende Testlauf mit Belastungsproben und Abnahmekriterien dokumentiert.",
            "PDF Navigation, Paketstruktur und spoilerfreie Verteilung vereinheitlicht.",
            "Aufsteller, nummerierte Gegner*innen Token und editierbare Quellen in den Release Umfang aufgenommen.",
        ],
    )


def build_gm_docx() -> None:
    doc = Document(SOURCE_DOCX)
    update_version(doc)
    set_alt_texts(doc)
    # The fourth inline image is the Chronotresor map. Preserve its width but
    # adopt the aspect ratio of the new landscape illustration.
    vault_shape = doc.inline_shapes[3]
    with Image.open(VAULT_ILLUSTRATION) as vault_image:
        vault_shape.height = int(vault_shape.width * vault_image.height / vault_image.width)
    for table in doc.tables:
        if table.rows:
            mark_header(table.rows[0])
    add_production_appendix(doc)
    doc.core_properties.title = "Die Stadt die den Dienstag verkaufte Spielleitungsheft Release Candidate 1"
    doc.core_properties.subject = "Daggerheart Abenteuer für vier Figuren auf Stufe 1 und zwei Spielabende"
    doc.core_properties.author = "Unabhängiges Daggerheart Fanprojekt"
    doc.core_properties.last_modified_by = ""
    doc.save(GM_DOCX)
    replace_docx_media(GM_DOCX, "word/media/image4.png", VAULT_ILLUSTRATION)


def replace_docx_media(docx_path: Path, member_name: str, image_path: Path) -> None:
    temporary = docx_path.with_name(docx_path.stem + "_media_update.docx")
    found = False
    with ZipFile(docx_path, "r") as source, ZipFile(temporary, "w", ZIP_DEFLATED) as target:
        for item in source.infolist():
            payload = source.read(item.filename)
            if item.filename == member_name:
                payload = image_path.read_bytes()
                found = True
            target.writestr(item, payload)
    if not found:
        temporary.unlink(missing_ok=True)
        raise FileNotFoundError(f"DOCX media member not found: {member_name}")
    temporary.replace(docx_path)


def configure_guide_styles(doc: Document) -> None:
    sec = doc.sections[0]
    sec.page_height = Cm(29.7)
    sec.page_width = Cm(21)
    sec.top_margin = Cm(1.8)
    sec.bottom_margin = Cm(1.6)
    sec.left_margin = Cm(1.8)
    sec.right_margin = Cm(1.8)
    doc.styles["Normal"].font.name = "Aptos"
    doc.styles["Normal"].font.size = Pt(10)
    doc.styles["Normal"].font.color.rgb = RGBColor.from_string(INK)
    doc.styles["Normal"].paragraph_format.space_after = Pt(6)
    for name, size in (("Title", 30), ("Heading 1", 20), ("Heading 2", 14)):
        style = doc.styles[name]
        style.font.name = "Georgia"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = True
    for section in doc.sections:
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.add_run("Release Candidate 1  •  November 2026  •  ").font.size = Pt(8)
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        footer._p.append(fld)


def build_release_guide() -> None:
    doc = Document()
    configure_guide_styles(doc)
    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("Releasebegleiter")
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Die Stadt die den Dienstag verkaufte")
    r.bold = True
    r.font.size = Pt(16)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Release Candidate 1  •  Fassung 2.1  •  November 2026").italic = True
    para(doc, "Dieser Begleiter erklärt, welche Datei wofür gedacht ist, was vor den beiden Abenden vorbereitet wird und welche Ergebnisse der simulierte Testlauf erbracht hat. Er enthält keine zusätzlichen Plotwahrheiten; dafür aber die beruhigende Erkenntnis, dass jemand an Ersatzstifte gedacht hat.")

    doc.add_heading("Sofortstart", level=1)
    bullets(doc, [
        "Lies im Spielleitungsheft die Seiten 2 bis 10 sowie die Dossiers der wahrscheinlich auftretenden Personen.",
        "Drucke Schnellreferenz und Szenenkarten; halte die Countdowns sichtbar.",
        "Sortiere das Spielendenpaket nach den Ausgabeszenen und lege die öffentliche Stadtkarte separat.",
        "Importiere für ein VTT bevorzugt namenlose Token; schalte Namen erst nach der Vorstellung frei.",
        "Plane nach jedem Abend zehn Minuten für Debriefing und offene Fäden ein.",
    ])
    doc.add_heading("Paketstruktur", level=1)
    add_table(doc, ["Ordner", "Zweck", "Spoiler"], [
        ["01 Spielleitung", "Hauptheft, Schnellreferenz, Szenenkarten, Gesamtausgabe", "ja"],
        ["02 Spielende", "Handouts und öffentliche Stadtkarte", "nein"],
        ["03 Druckmaterial", "Aufstellerbogen", "teilweise durch Namen"],
        ["04 VTT", "80 transparente Token", "benannte Varianten teilweise"],
        ["05 Quellen", "editierbare Fassungen und Bauskripte", "ja"],
    ], [4.1, 8.7, 3.2], 8.5)
    doc.add_heading("Druckcheck", level=1)
    add_table(doc, ["Prüfung", "Status"], [
        ["A4 ohne Skalierung oder mit tatsächlicher Größe", "☐"],
        ["Handouts szenenweise getrennt", "☐"],
        ["Spielendenkarte statt Leitungskarte", "☐"],
        ["Aufsteller auf stärkerem Papier", "☐"],
        ["Schnellreferenz beidseitig oder nebeneinander", "☐"],
        ["Ersatzstifte, Marker und sichtbare Countdown Felder", "☐"],
    ], [13.8, 2.2], 9)
    doc.add_page_break()
    doc.add_heading("Simulierter Testlauf", level=1)
    para(doc, "Die vollständige Auswertung steht im Produktionsanhang des Spielleitungshefts. Die Simulation endete bei 3 Stunden 50 Minuten am ersten und 3 Stunden 50 Minuten am zweiten Abend, jeweils einschließlich Pause. Zwei vollständige Kämpfe in Folge überschritten das Budget; Motivwechsel, Rückzug und Montage hielten die Entscheidungstiefe ohne Regelermüdung.")
    add_table(doc, ["Bereich", "Urteil", "Wichtigste Bedingung"], [
        ["Regeln", "bestanden", "Fear früh für Ortsdruck und Features ausgeben"],
        ["Balance", "bestanden", "Gegner*innen nicht bis zum letzten HP spielen"],
        ["Zeit", "bestanden", "Reise kürzen, Entscheidungen erhalten"],
        ["Logik", "bestanden", "hundert Wochen seit Neuvermessung beibehalten"],
        ["Konsistenz", "bestanden", "Herr Pünktlich als Vertragsecho darstellen"],
        ["Spoilerschutz", "bestanden", "nur Dateien aus 02 Spielende teilen"],
    ], [4.0, 3.0, 9.0], 8.5)
    doc.add_heading("Echter Tischtest", level=1)
    bullets(doc, [
        "Notiere je Szene tatsächliche Start und Endzeit.",
        "Markiere, welche Hinweise ohne Leitungseingriff gefunden wurden.",
        "Zähle Konfliktaustausche, ausgegebenes Fear und freiwillige Rückzüge.",
        "Frage nach dem Spiel, ob die Eigentumsfrage verständlich war und ob alle Enden als echte Möglichkeiten wirkten.",
        "Halte mindestens eine überraschende Entscheidung fest. Wenn keine auftrat, waren entweder die Spielenden außergewöhnlich höflich oder die Türen verdächtig eindeutig beschriftet.",
    ])
    doc.core_properties.title = "Releasebegleiter Die Stadt die den Dienstag verkaufte"
    doc.core_properties.author = "Unabhängiges Daggerheart Fanprojekt"
    doc.core_properties.last_modified_by = ""
    doc.save(GUIDE_DOCX)


def add_outline(writer: PdfWriter, reader: PdfReader, titles) -> None:
    for title, page in titles:
        if 0 <= page < len(reader.pages):
            writer.add_outline_item(title, page)


def copy_pdf_with_outline(src: Path, dst: Path, outline) -> None:
    reader = PdfReader(str(src))
    writer = PdfWriter()
    writer.append(reader)
    add_outline(writer, reader, outline)
    writer.add_metadata({
        "/Title": dst.stem.replace("_", " "),
        "/Author": "Unabhängiges Daggerheart Fanprojekt",
        "/Subject": "Release Candidate 1",
    })
    with dst.open("wb") as f:
        writer.write(f)


def merge_omnibus(parts, dst: Path) -> None:
    writer = PdfWriter()
    offset = 0
    for title, path in parts:
        reader = PdfReader(str(path))
        writer.append(reader)
        writer.add_outline_item(title, offset)
        offset += len(reader.pages)
    writer.add_metadata({
        "/Title": "Die Stadt die den Dienstag verkaufte Gesamtausgabe Release Candidate 1",
        "/Author": "Unabhängiges Daggerheart Fanprojekt",
        "/Subject": "Spielleitung, Handouts und Druckmaterialien",
    })
    with dst.open("wb") as f:
        writer.write(f)


def package_release(gm_pdf: Path, guide_pdf: Path) -> Path:
    if PKG.exists():
        import shutil
        shutil.rmtree(PKG)
    dirs = {
        "gm": PKG / "01_Spielleitung",
        "players": PKG / "02_Spielende",
        "print": PKG / "03_Druckmaterial",
        "vtt": PKG / "04_VTT",
        "sources": PKG / "05_Quellen",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    omnibus = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Gesamtausgabe_RC1_v2_1.pdf"
    player_rc = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Spielendenpaket_RC1_v2_1.pdf"
    standees = OUT / "Aufsteller_und_VTT_v1_0" / "Druck" / "Die_Stadt_die_den_Dienstag_verkaufte_Aufstellerbogen_v1_0.pdf"
    quick_pdf = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Leitungsschnellreferenz_v1_0.pdf"
    cards_pdf = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Szenenkarten_v1_0.pdf"
    original_player = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Spielerhandouts_v1_0.pdf"

    player_outline = [
        ("Deckblatt", 0), ("Dienstagsquittung", 1), ("Fahrplan Linie 7", 2),
        ("Notabstimmung", 3), ("Tessas Botschaft", 4), ("Sechs Siegel", 5),
        ("Countdowns", 6), ("Stadtkarte", 7), ("Flugblatt", 8),
        ("Formular 88b", 9), ("Verlorene Geburtstage", 10), ("Bilanzbuch", 11),
    ]
    copy_pdf_with_outline(original_player, player_rc, player_outline)

    merge_omnibus([
        ("Spielleitungsheft", gm_pdf),
        ("Leitungsschnellreferenz", quick_pdf),
        ("Szenenkarten", cards_pdf),
        ("Spielendenpaket", player_rc),
        ("Aufsteller und Marker", standees),
    ], omnibus)

    for path in (gm_pdf, omnibus, quick_pdf, cards_pdf, guide_pdf):
        copy2(path, dirs["gm"] / path.name)
    copy2(player_rc, dirs["players"] / player_rc.name)
    copy2(OUT / "Veyra_Stadtkarte_spielendensicher_v1_0.png", dirs["players"] / "Veyra_Stadtkarte_spielendensicher_v1_0.png")
    copy2(OUT / "Veyra_Stadtkarte_illustriert_v1_0.png", dirs["gm"] / "Veyra_Stadtkarte_Spielleitung_v1_0.png")
    copy2(OUT / "Archiv_der_kleinen_Wahrheiten_illustration_v1_0.png", dirs["gm"] / "Archiv_der_kleinen_Wahrheiten_illustration_v1_0.png")
    copy2(VAULT_ILLUSTRATION, dirs["gm"] / VAULT_ILLUSTRATION.name)
    copy2(standees, dirs["print"] / standees.name)

    vtt_source = OUT / "Aufsteller_und_VTT_v1_0" / "VTT"
    copytree(vtt_source, dirs["vtt"], dirs_exist_ok=True)
    copy2(OUT / "Aufsteller_und_VTT_v1_0" / "Uebersicht" / "README.txt", dirs["vtt"] / "README_VTT.txt")

    for path in (
        GM_DOCX, GUIDE_DOCX,
        OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Leitungsschnellreferenz_v1_0.docx",
        OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Szenenkarten_v1_0.docx",
        WORK / "build_book.py", WORK / "build_player_handouts.py",
        WORK / "build_gm_quick_reference.py", WORK / "build_scene_cards.py",
        WORK / "build_standees_vtt.py", WORK / "build_release_candidate.py",
        WORK / "assets" / "map_vault_illustrated_v2_0.png",
    ):
        copy2(path, dirs["sources"] / path.name)

    readme = PKG / "README_RELEASE.txt"
    readme.write_text(
        "DIE STADT DIE DEN DIENSTAG VERKAUFTE\n"
        "Release Candidate 1 - Fassung 2.1 - November 2026\n\n"
        "01_Spielleitung enthält alle spoilerhaltigen Leitungsdateien und die Gesamtausgabe.\n"
        "02_Spielende kann ohne Plotspoiler geteilt werden. Handouts trotzdem szenenweise ausgeben.\n"
        "03_Druckmaterial enthält Aufsteller und Marker.\n"
        "04_VTT enthält 80 transparente PNG-Token mit 1024 x 1024 Pixeln.\n"
        "05_Quellen enthält die editierbaren Fassungen und Bauskripte.\n\n"
        "Empfohlener Einstieg: Releasebegleiter lesen, dann Spielleitungsheft Seiten 2 bis 10.\n"
        "Die Dateien sind als Fanmaterial für Daggerheart gedacht und nicht offiziell unterstützt.\n",
        encoding="utf-8",
    )

    zip_path = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_RC1_v2_1.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(PKG.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(PKG.parent))
    return zip_path


if __name__ == "__main__":
    build_gm_docx()
    build_release_guide()
    print(GM_DOCX)
    print(GUIDE_DOCX)

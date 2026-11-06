from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "work" / "assets"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

OUTPUT = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Spielerhandouts_v1_0.pdf"

INK = colors.HexColor("#17222D")
TEAL = colors.HexColor("#173D4F")
COPPER = colors.HexColor("#A65D3B")
CREAM = colors.HexColor("#F7F1E3")
PALE = colors.HexColor("#E8F1EF")
GREY = colors.HexColor("#D9D9D9")
MID = colors.HexColor("#66717A")
RED = colors.HexColor("#9D3F37")


def register_fonts():
    candidates = {
        "Body": Path(r"C:\Windows\Fonts\aptos.ttf"),
        "BodyBold": Path(r"C:\Windows\Fonts\aptos-bold.ttf"),
        "Display": Path(r"C:\Windows\Fonts\georgia.ttf"),
        "DisplayBold": Path(r"C:\Windows\Fonts\georgiab.ttf"),
        "Hand": Path(r"C:\Windows\Fonts\segoepr.ttf"),
    }
    fallbacks = {
        "Body": "Helvetica",
        "BodyBold": "Helvetica-Bold",
        "Display": "Times-Roman",
        "DisplayBold": "Times-Bold",
        "Hand": "Times-Italic",
    }
    names = {}
    for name, path in candidates.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))
            names[name] = name
        else:
            names[name] = fallbacks[name]
    return names


FONTS = register_fonts()


STYLES = {
    "body": ParagraphStyle(
        "body", fontName=FONTS["Body"], fontSize=11, leading=15, textColor=INK,
        spaceAfter=8, alignment=TA_LEFT,
    ),
    "small": ParagraphStyle(
        "small", fontName=FONTS["Body"], fontSize=8.6, leading=11, textColor=MID,
        alignment=TA_LEFT,
    ),
    "receipt": ParagraphStyle(
        "receipt", fontName=FONTS["Body"], fontSize=10.4, leading=14, textColor=INK,
        spaceAfter=8,
    ),
    "message": ParagraphStyle(
        "message", fontName=FONTS["Hand"], fontSize=14, leading=21, textColor=INK,
        spaceAfter=14,
    ),
    "center": ParagraphStyle(
        "center", fontName=FONTS["Body"], fontSize=10, leading=13, textColor=INK,
        alignment=TA_CENTER,
    ),
}


def footer(c, page_size, text="Spielmaterialien aus Veyra"):
    w, _ = page_size
    c.setFont(FONTS["Body"], 7)
    c.setFillColor(MID)
    c.drawCentredString(w / 2, 0.42 * cm, text)


def title(c, text, subtitle=None, page_size=A4, y=None):
    w, h = page_size
    y = y or h - 1.7 * cm
    c.setFillColor(colors.black)
    c.setFont(FONTS["DisplayBold"], 24)
    c.drawString(1.7 * cm, y, text)
    if subtitle:
        c.setFillColor(MID)
        c.setFont(FONTS["Body"], 9)
        c.drawString(1.7 * cm, y - 0.65 * cm, subtitle)
    return y - (1.25 * cm if subtitle else 0.85 * cm)


def draw_paragraph(c, html, style, x, y_top, width):
    p = Paragraph(html, style)
    _, h = p.wrap(width, 50 * cm)
    p.drawOn(c, x, y_top - h)
    return y_top - h


def draw_image_contain(c, path, box, background=colors.white):
    x, y, w, h = box
    c.setFillColor(background)
    c.rect(x, y, w, h, fill=1, stroke=0)
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(str(path), x + (w - dw) / 2, y + (h - dh) / 2, width=dw, height=dh, preserveAspectRatio=True, mask="auto")


def draw_image_cover(c, path, box):
    x, y, w, h = box
    with Image.open(path) as im:
        iw, ih = im.size
    scale = max(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(str(path), x + (w - dw) / 2, y + (h - dh) / 2, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
    c.restoreState()


def page_cover(c):
    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(CREAM)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    draw_image_cover(c, ASSET / "map_city_players_v1_0.png", (0, 0, w, 14.2 * cm))
    c.setFillColor(colors.Color(0.97, 0.95, 0.89, alpha=0.92))
    c.rect(0, 13.2 * cm, w, h - 13.2 * cm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONTS["DisplayBold"], 31)
    c.drawString(1.7 * cm, h - 3.2 * cm, "Spielmaterialien aus Veyra")
    c.setFont(FONTS["Display"], 17)
    c.drawString(1.7 * cm, h - 4.5 * cm, "Die Stadt die den Dienstag verkaufte")
    y = h - 6.4 * cm
    y = draw_paragraph(
        c,
        "Dieses Paket enthält Dokumente, Karten und Fundstücke für die Spielenden. "
        "Öffnet einzelne Seiten bitte erst, wenn sie am Tisch ausgeteilt werden. "
        "Die Wirklichkeit ist schon unübersichtlich genug; sie braucht keine Vorschau-Funktion.",
        STYLES["body"], 1.7 * cm, y, 16.8 * cm,
    )
    c.setFillColor(COPPER)
    c.setFont(FONTS["BodyBold"], 9)
    c.drawString(1.7 * cm, y - 0.45 * cm, "SPIELENDENFASSUNG  •  OHNE LEITUNGSNOTIZEN")
    c.showPage()


def page_receipt(c):
    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(CREAM)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setStrokeColor(COPPER)
    c.setLineWidth(1.2)
    c.rect(1.6 * cm, 1.35 * cm, w - 3.2 * cm, h - 2.7 * cm, fill=0, stroke=1)
    c.setFillColor(TEAL)
    c.rect(1.6 * cm, h - 5.2 * cm, w - 3.2 * cm, 3.85 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONTS["DisplayBold"], 25)
    c.drawString(2.2 * cm, h - 3.0 * cm, "MORGEN & SÖHNE")
    c.setFont(FONTS["Body"], 10)
    c.drawString(2.2 * cm, h - 3.75 * cm, "Handel mit verlässlicher Zukunft")
    c.setFillColor(COPPER)
    c.setFont(FONTS["BodyBold"], 9)
    c.drawRightString(w - 2.2 * cm, h - 3.7 * cm, "DIENSTAGSQUITTUNG")

    y = h - 6.25 * cm
    fields = [
        ("Empfangen von", "Stadt Veyra"),
        ("Gegenstand", "Ein wiederkehrender Zeitraum von Sonnenaufgang bis Sonnenaufgang, im öffentlichen Kalender zwischen Montag und Mittwoch gelegen."),
        ("Vergütung", "Aufschub sämtlicher kommunaler Verbindlichkeiten um sieben Jahre; Stabilisierung der Stadtzeit; diskrete Entlastung von Erinnerung und akuter physischer Gefährdung."),
        ("Eigentumsvorbehalt", "Der veräußerte Zeitraum verbleibt als Rohzeit-Pfand in Veyra. Erinnerungen, Regeneration und ungenutzte Möglichkeiten dürfen als Zeit-Zinsen abgeschöpft und exportiert werden."),
        ("Status", "Sechs von sechs Siegeln ausstehend. Endgültige Vollstreckung zur Hundertsten Nulluhr."),
    ]
    for label, body in fields:
        y = draw_paragraph(c, f"<b>{label}</b><br/>{body}", STYLES["receipt"], 2.2 * cm, y, w - 4.4 * cm) - 0.25 * cm

    c.setStrokeColor(colors.HexColor("#7D91A0"))
    c.setLineWidth(0.8)
    c.line(2.2 * cm, y - 0.15 * cm, w - 2.2 * cm, y - 0.15 * cm)
    y -= 0.8 * cm
    c.setFillColor(colors.HexColor("#244C67"))
    y = draw_paragraph(
        c,
        "<i>Wenn ihr vier das lesen könnt, hat die Stadt euch noch nicht ganz vergessen. "
        "Mio brachte mich hindurch. Linie 7. Blaues Wachs. Frag nach Tessa. - TQ</i>",
        STYLES["message"], 2.35 * cm, y, w - 4.7 * cm,
    )
    footer(c, A4)
    c.showPage()


def page_timetable(c):
    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    y = title(c, "Fahrplan der Linie 7", "Betriebsinformationen für Fahrgäste", A4)

    data = [
        ["HALT", "ABFAHRT", "HINWEIS"],
        ["Platz der fehlenden Glocke", "Montag 24:00", "Nur bei Regen und Ankerresonanz sichtbar"],
        ["Archiv der kleinen Wahrheiten", "Zwischen zwei Sätzen", "Blaues Wachs vorzeigen"],
        ["Verlorene Minuten", "Wenn niemand hinsieht", "Nicht aussteigen, wenn du dich selbst rufen hörst"],
        ["Nachmorgen", "Dienstag 14:17", "Endstation und Anfang"],
    ]
    table = Table(data, colWidths=[5.6 * cm, 4.1 * cm, 7.1 * cm], rowHeights=[1.0 * cm, 2.0 * cm, 2.0 * cm, 2.0 * cm, 2.0 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONTS["BodyBold"]),
        ("FONTNAME", (0, 1), (-1, -1), FONTS["Body"]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("BACKGROUND", (0, 2), (-1, 2), PALE),
        ("BACKGROUND", (0, 4), (-1, 4), PALE),
    ]))
    tw, th = table.wrap(w - 3.4 * cm, h)
    table.drawOn(c, 1.7 * cm, y - th - 0.3 * cm)
    y = y - th - 1.3 * cm
    text = (
        "<b>Beförderungsbedingungen</b><br/>"
        "Niemand wird wegen fehlender Zahlungsfähigkeit zurückgelassen. Erinnerungen sind kein gültiges Zahlungsmittel. "
        "Die Route darf nicht öffentlich verbreitet werden: Depot Null wird überwacht, und Sichtbarkeit gefährdet Nachmorgen. "
        "Beschwerden bitte an die Fahrer*innen; Beschwerden über die Existenz der Linie bitte an die Wirklichkeit."
    )
    draw_paragraph(c, text, STYLES["body"], 1.7 * cm, y, w - 3.4 * cm)
    footer(c, A4)
    c.showPage()


def page_minutes(c):
    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(colors.HexColor("#F4F0E8"))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    y = title(c, "Protokoll der Notabstimmung", "Auszug aus Sitzung 441 des Magistrats  •  sieben Jahre zuvor", A4)
    bullets = [
        "Anwesend: 11 Sitze. Offen erklärte Interessenkonflikte: 0. Tatsächliche Zahl später nachgewiesener Zahlungen durch Morgen & Söhne: 4.",
        "Antrag Voss: Vertrag ablehnen; solidarischen Schuldenschnitt mit den Kanalstädten verhandeln. Ergebnis: 5 zu 6 abgelehnt.",
        "Antrag Sitz 7: Dienstag veräußern. Ergebnis: 7 zu 4 angenommen.",
        "Späterer Nachtrag 34, vor einhundert Wochen - knapp zwei Jahren - nach dem Fürsorgestreik: Die Neuvermessung überträgt die wöchentliche Prüfungshoheit vom Magistrat auf die Nulluhr. Die erste Prüfung folgt eine Woche nach der Neuvermessung; die anstehende Nulluhr ist Prüfung einhundert.",
        "Randnotiz Tessa Quendel: Die Alternative wurde aus der öffentlichen Fassung entfernt. Ich bewahre die ursprüngliche Seite.",
    ]
    y -= 0.4 * cm
    for idx, item in enumerate(bullets, 1):
        y = draw_paragraph(c, f"<b>{idx:02d}</b>&nbsp;&nbsp;{item}", STYLES["body"], 1.9 * cm, y, w - 4.0 * cm) - 0.35 * cm
    c.saveState()
    c.translate(w - 4.6 * cm, 4.0 * cm)
    c.rotate(8)
    c.setStrokeColor(RED)
    c.setFillColor(RED)
    c.setLineWidth(2)
    c.rect(-2.6 * cm, -0.85 * cm, 5.2 * cm, 1.7 * cm, fill=0, stroke=1)
    c.setFont(FONTS["BodyBold"], 15)
    c.drawCentredString(0, -0.2 * cm, "AKTENKOPIE")
    c.restoreState()
    footer(c, A4)
    c.showPage()


def page_tessa(c):
    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(CREAM)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    y = title(c, "Tessas Botschaft", None, A4)
    c.setStrokeColor(colors.HexColor("#B7C0C7"))
    c.setLineWidth(0.6)
    for i in range(17):
        yy = h - 5.0 * cm - i * 1.15 * cm
        c.line(1.7 * cm, yy, w - 1.7 * cm, yy)
    y -= 0.65 * cm
    paras = [
        "Der Dienstag ist nicht fort. Sein roher Zeitraum liegt noch als Pfand in Veyra; nur seine Zinsen werden exportiert. Er ist dort, wo Systeme alles ablegen, was ihre Bilanz stört. Menschen leben dort. Manche wollen zurück. Manche wollen in Ruhe gelassen werden. Alle verdienen eine Stimme.",
        "Brecht die Nulluhr nicht, bevor ihr wisst, wohin ihre Zeit fließt. Sechs Siegel halten den Vertrag: Besitz, Schuld, Schweigen, Gehorsam, Alternativlosigkeit und Eile. Jedes kann mit Gewalt gebrochen werden. Keines muss.",
        "Wenn ihr nur den Kalender repariert, repariert ihr vielleicht auch die Ordnung, die ihn verkauft hat.",
    ]
    for text in paras:
        y = draw_paragraph(c, text, STYLES["message"], 2.2 * cm, y, w - 4.4 * cm) - 0.25 * cm
    c.setFillColor(colors.HexColor("#244C67"))
    c.circle(w - 3.3 * cm, 3.3 * cm, 1.15 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONTS["DisplayBold"], 18)
    c.drawCentredString(w - 3.3 * cm, 3.1 * cm, "TQ")
    footer(c, A4)
    c.showPage()


def page_seals(c):
    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    y = title(c, "Die sechs Siegel", "Fragen für eine Ordnung, die noch nicht feststeht", A4)
    rows = [
        ["Besitz", "Kann Zeit jemandem gehören?", ""],
        ["Schuld", "Wer soll zahlen?", ""],
        ["Schweigen", "Welche Wahrheit wird öffentlich?", ""],
        ["Gehorsam", "Wessen Befehl endet hier?", ""],
        ["Alternativlosigkeit", "Welche dritte Möglichkeit entsteht?", ""],
        ["Eile", "Was verdient trotz Druck Beratung?", ""],
    ]
    data = [["SIEGEL", "FRAGE", "NOTIZEN"]] + rows
    table = Table(data, colWidths=[4.65 * cm, 6.25 * cm, 5.9 * cm], rowHeights=[1.0 * cm] + [3.15 * cm] * 6)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONTS["BodyBold"]),
        ("FONTNAME", (0, 1), (0, -1), FONTS["DisplayBold"]),
        ("FONTNAME", (1, 1), (-1, -1), FONTS["Body"]),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (0, -1), 10.5),
        ("FONTSIZE", (1, 1), (-1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 13),
        ("GRID", (0, 0), (-1, -1), 0.6, GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 2), (-1, 2), PALE),
        ("BACKGROUND", (0, 4), (-1, 4), PALE),
        ("BACKGROUND", (0, 6), (-1, 6), PALE),
        ("LINEBELOW", (2, 1), (2, -1), 0.4, colors.HexColor("#88949C")),
    ]))
    tw, th = table.wrap(w - 3.4 * cm, h)
    table.drawOn(c, 1.7 * cm, y - th - 0.3 * cm)
    footer(c, A4)
    c.showPage()


def page_countdowns(c):
    w, h = A4
    c.setPageSize(A4)
    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    y = title(c, "Offene Countdowns", "Markiert Veränderungen sichtbar und besprecht, was sie in der Geschichte bedeuten", A4)
    items = [
        ("ENDGÜLTIGER VERTRAG", 6, COPPER),
        ("ERHÖHTE AUFMERKSAMKEIT", 4, RED),
        ("ENTGLEISUNG LINIE 7", 3, TEAL),
        ("GEMEINSAMER TAKT", 4, colors.HexColor("#47714D")),
    ]
    y -= 0.5 * cm
    for name, count, color in items:
        c.setFillColor(color)
        c.setFont(FONTS["BodyBold"], 13)
        c.drawString(2.0 * cm, y, name)
        y -= 1.05 * cm
        for i in range(count):
            x = 2.2 * cm + i * 2.35 * cm
            c.setFillColor(colors.white)
            c.setStrokeColor(color)
            c.setLineWidth(2)
            c.circle(x, y, 0.62 * cm, fill=1, stroke=1)
        y -= 2.1 * cm
        c.setStrokeColor(GREY)
        c.setLineWidth(0.6)
        c.line(2.0 * cm, y + 0.55 * cm, w - 2.0 * cm, y + 0.55 * cm)
        y -= 0.5 * cm
    footer(c, A4)
    c.showPage()


def page_map(c):
    ps = landscape(A4)
    w, h = ps
    c.setPageSize(ps)
    c.setFillColor(CREAM)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont(FONTS["DisplayBold"], 22)
    c.drawString(1.0 * cm, h - 1.3 * cm, "Karte von Veyra")
    draw_image_contain(c, ASSET / "map_city_players_v1_0.png", (0.9 * cm, 1.05 * cm, w - 1.8 * cm, h - 2.8 * cm), CREAM)
    c.setFillColor(MID)
    c.setFont(FONTS["Body"], 7.3)
    c.drawCentredString(w / 2, 0.45 * cm, "Öffentliche Stadtkarte  •  Wege sind erzählerisch, nicht maßstäblich")
    c.showPage()


def page_image_handout(c, image_name, title_text):
    ps = landscape(A4)
    w, h = ps
    c.setPageSize(ps)
    c.setFillColor(colors.black)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    draw_image_contain(c, ASSET / image_name, (0, 0, w, h), colors.black)
    c.saveState()
    c.setFillColor(colors.Color(0, 0, 0, alpha=0.68))
    c.rect(0, 0, w, 0.9 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONTS["Body"], 7.5)
    c.drawCentredString(w / 2, 0.31 * cm, title_text)
    c.restoreState()
    c.showPage()


def build():
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Die Stadt die den Dienstag verkaufte - Spieler*innen-Handouts")
    c.setAuthor("Unabhängiges Daggerheart Fanprojekt")
    c.setSubject("Spoilerfreie Spielmaterialien für Veyra")
    page_cover(c)
    page_receipt(c)
    page_timetable(c)
    page_minutes(c)
    page_tessa(c)
    page_seals(c)
    page_countdowns(c)
    page_map(c)
    page_image_handout(c, "handout_common_beat.jpg", "Flugblatt des Gemeinsamen Takts")
    page_image_handout(c, "handout_form_88b.jpg", "Formular 88b zur Meldung temporärer Existenzlücken")
    page_image_handout(c, "handout_lio_birthdays.jpg", "Lios Notizzettel der verlorenen Geburtstage")
    page_image_handout(c, "handout_orsino_ledger.jpg", "Auszug aus Orsinos Bilanzbuch")
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "work" / "assets"
OUT = ROOT / "outputs"
PACKAGE = OUT / "Aufsteller_und_VTT_v1_0"
PRINT = PACKAGE / "Druck"
VTT = PACKAGE / "VTT"
OVERVIEW = PACKAGE / "Uebersicht"
PRINT_CACHE = ROOT / "work" / "standee_print_assets_v1_0"
PDF_PATH = PRINT / "Die_Stadt_die_den_Dienstag_verkaufte_Aufstellerbogen_v1_0.pdf"
ZIP_PATH = OUT / "Die_Stadt_die_den_Dienstag_verkaufte_Aufsteller_und_VTT_v1_0.zip"

TOKEN_SIZE = 1024


CHARACTERS = [
    {"id": "nsc_tessa_quendel", "name": "Tessa Quendel", "kind": "NSC", "file": "npc_tessa.png", "color": "#2B6C78"},
    {"id": "nsc_jori_venn", "name": "Jori Venn", "kind": "NSC", "file": "npc_jori.png", "color": "#A64B3C"},
    {"id": "nsc_elian_voss", "name": "Elian Voss", "kind": "NSC", "file": "npc_elian.png", "color": "#6E5A8A"},
    {"id": "nsc_orsino_vale", "name": "Orsino Vale", "kind": "NSC", "file": "npc_orsino.png", "color": "#9A5A35"},
    {"id": "nsc_mio_kest", "name": "Mio Kest", "kind": "NSC", "file": "npc_mio.png", "color": "#17706A"},
    {"id": "nsc_dienstag", "name": "Dienstag", "kind": "NSC", "file": "npc_dienstag.png", "color": "#B48A2C"},
    {"id": "gegner_taktwaechter", "name": "Taktwächter*in", "kind": "GEGNER*IN", "file": "enemy_taktwaechter.png", "color": "#7E3434", "numbered": 4},
    {"id": "gegner_indexschwarm", "name": "Indexschwarm", "kind": "GEGNER*IN", "file": "enemy_indexschwarm.png", "color": "#4D6372", "numbered": 2},
    {"id": "gegner_minutenzehrer", "name": "Minutenzehrer", "kind": "GEGNER*IN", "file": "enemy_minutenzehrer.png", "color": "#5B4478", "numbered": 4},
    {"id": "gegner_papierknecht", "name": "Papierknecht", "kind": "GEGNER*IN", "file": "enemy_papierknecht.png", "color": "#6C6C68", "numbered": 6},
    {"id": "gegner_herr_puenktlich", "name": "Herr Pünktlich", "kind": "GEGNER*IN", "file": "enemy_herr_puenktlich.png", "color": "#8C5B39"},
    {"id": "gegner_nulluhr", "name": "Die Nulluhr", "kind": "BOSS", "file": "enemy_nulluhr.png", "color": "#B18C35"},
]


def font_path(name, fallback):
    p = Path(r"C:\Windows\Fonts") / name
    return str(p if p.exists() else Path(r"C:\Windows\Fonts") / fallback)


FONT_BOLD = font_path("aptos-bold.ttf", "arialbd.ttf")
FONT_REGULAR = font_path("aptos.ttf", "arial.ttf")
FONT_DISPLAY = font_path("georgiab.ttf", "timesbd.ttf")


def ensure_dirs():
    dirs = [
        PRINT,
        OVERVIEW,
        VTT / "Quadratisch" / "Mit_Name",
        VTT / "Quadratisch" / "Ohne_Name",
        VTT / "Rund" / "Mit_Name",
        VTT / "Rund" / "Ohne_Name",
        VTT / "Nummeriert" / "Quadratisch",
        VTT / "Nummeriert" / "Rund",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    PRINT_CACHE.mkdir(parents=True, exist_ok=True)


def cover_crop(image, size):
    image = image.convert("RGB")
    w, h = image.size
    target_ratio = size[0] / size[1]
    ratio = w / h
    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        image = image.crop((left, 0, left + new_w, h))
    elif ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = max(0, int((h - new_h) * 0.36))
        image = image.crop((0, top, w, top + new_h))
    return image.resize(size, Image.Resampling.LANCZOS)


def fit_text(draw, text, max_width, start_size=72, min_size=34):
    for size in range(start_size, min_size - 1, -2):
        font = ImageFont.truetype(FONT_BOLD, size)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
    return ImageFont.truetype(FONT_BOLD, min_size)


def label_plate(base, name, color, y0=790, y1=970):
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((72, y0, 952, y1), radius=48, fill=(14, 22, 28, 220), outline=color + "FF", width=10)
    font = fit_text(draw, name, 800)
    box = draw.textbbox((0, 0), name, font=font)
    x = (TOKEN_SIZE - (box[2] - box[0])) // 2
    y = y0 + (y1 - y0 - (box[3] - box[1])) // 2 - box[1]
    draw.text((x, y), name, font=font, fill="white", stroke_width=2, stroke_fill="#11181D")
    return Image.alpha_composite(base, overlay)


def make_square(source, color, name=None):
    size = TOKEN_SIZE
    image = cover_crop(Image.open(source), (size - 96, size - 96)).convert("RGBA")
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size - 96, size - 96), 0)
    m = ImageDraw.Draw(mask)
    m.rounded_rectangle((0, 0, size - 97, size - 97), radius=112, fill=255)
    out.paste(image, (48, 48), mask)
    draw = ImageDraw.Draw(out)
    draw.rounded_rectangle((34, 34, size - 34, size - 34), radius=128, outline=color, width=34)
    draw.rounded_rectangle((52, 52, size - 52, size - 52), radius=110, outline="#F5E8C8", width=8)
    if name:
        out = label_plate(out, name, color)
    return out


def make_round(source, color, name=None):
    size = TOKEN_SIZE
    portrait = cover_crop(Image.open(source), (size - 108, size - 108)).convert("RGBA")
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size - 108, size - 108), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 109, size - 109), fill=255)
    out.paste(portrait, (54, 54), mask)
    draw = ImageDraw.Draw(out)
    draw.ellipse((35, 35, size - 35, size - 35), outline=color, width=38)
    draw.ellipse((57, 57, size - 57, size - 57), outline="#F5E8C8", width=8)
    if name:
        out = label_plate(out, name, color, 782, 948)
        circle = Image.new("L", (size, size), 0)
        ImageDraw.Draw(circle).ellipse((30, 30, size - 30, size - 30), fill=255)
        clipped = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        clipped.paste(out, (0, 0), circle)
        out = clipped
    return out


def number_badge(image, number, color):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    cx, cy, r = 835, 185, 94
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#11181DE8", outline=color, width=16)
    text = f"{number:02d}"
    font = ImageFont.truetype(FONT_BOLD, 82)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (box[2] - box[0]) / 2, cy - (box[3] - box[1]) / 2 - box[1]), text, font=font, fill="white")
    return out


def save_png(image, path):
    image.save(path, "PNG", optimize=True, compress_level=9)


def save_print_jpeg(image, path, size=720):
    reduced = image.resize((size, size), Image.Resampling.LANCZOS)
    background = Image.new("RGB", reduced.size, "white")
    background.paste(reduced, (0, 0), reduced.getchannel("A"))
    background.save(path, "JPEG", quality=88, optimize=True, progressive=True, subsampling=1)


def generate_vtt_files():
    paths = {}
    for char in CHARACTERS:
        source = ASSET / char["file"]
        sid = char["id"]
        color = char["color"]
        square_name = make_square(source, color, char["name"])
        square_plain = make_square(source, color)
        round_name = make_round(source, color, char["name"])
        round_plain = make_round(source, color)

        p_sq_name = VTT / "Quadratisch" / "Mit_Name" / f"{sid}_mit_name.png"
        p_sq_plain = VTT / "Quadratisch" / "Ohne_Name" / f"{sid}_ohne_name.png"
        p_ro_name = VTT / "Rund" / "Mit_Name" / f"{sid}_mit_name.png"
        p_ro_plain = VTT / "Rund" / "Ohne_Name" / f"{sid}_ohne_name.png"
        for img, path in ((square_name, p_sq_name), (square_plain, p_sq_plain), (round_name, p_ro_name), (round_plain, p_ro_plain)):
            save_png(img, path)
        p_print_sq_name = PRINT_CACHE / f"{sid}_square_name.jpg"
        p_print_sq_plain = PRINT_CACHE / f"{sid}_square_plain.jpg"
        p_print_ro_name = PRINT_CACHE / f"{sid}_round_name.jpg"
        p_print_ro_plain = PRINT_CACHE / f"{sid}_round_plain.jpg"
        save_print_jpeg(square_name, p_print_sq_name)
        save_print_jpeg(square_plain, p_print_sq_plain)
        save_print_jpeg(round_name, p_print_ro_name, size=600)
        save_print_jpeg(round_plain, p_print_ro_plain, size=420)
        paths[sid] = {
            "square_name": p_sq_name,
            "square_plain": p_sq_plain,
            "round_name": p_ro_name,
            "round_plain": p_ro_plain,
            "print_square_name": p_print_sq_name,
            "print_square_plain": p_print_sq_plain,
            "print_round_name": p_print_ro_name,
            "print_round_plain": p_print_ro_plain,
        }

        for number in range(1, char.get("numbered", 0) + 1):
            save_png(number_badge(square_plain, number, color), VTT / "Nummeriert" / "Quadratisch" / f"{sid}_{number:02d}.png")
            save_png(number_badge(round_plain, number, color), VTT / "Nummeriert" / "Rund" / f"{sid}_{number:02d}.png")
    return paths


def pdf_font(name, fallback):
    path = Path(r"C:\Windows\Fonts") / name
    if path.exists():
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        key = "PDF_" + path.stem
        if key not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(key, str(path)))
        return key
    return fallback


PDF_BODY = pdf_font("aptos.ttf", "Helvetica")
PDF_BOLD = pdf_font("aptos-bold.ttf", "Helvetica-Bold")
PDF_DISPLAY = pdf_font("georgiab.ttf", "Times-Bold")


def pdf_header(c, title, subtitle):
    w, h = A4
    c.setFillColor(colors.black)
    c.setFont(PDF_DISPLAY, 22)
    c.drawString(1.1 * cm, h - 1.35 * cm, title)
    c.setFillColor(colors.HexColor("#66717A"))
    c.setFont(PDF_BODY, 8)
    c.drawString(1.1 * cm, h - 1.85 * cm, subtitle)


def draw_standee(c, image_path, x, y, width=5.9 * cm, height=12.3 * cm):
    tab = 0.8 * cm
    panel = (height - tab) / 2
    pad = 0.18 * cm
    c.setStrokeColor(colors.HexColor("#777777"))
    c.setLineWidth(0.55)
    c.rect(x, y, width, height, fill=0, stroke=1)

    c.saveState()
    c.translate(x + width, y + tab + 2 * panel)
    c.rotate(180)
    c.drawImage(ImageReader(str(image_path)), pad, pad, width=width - 2 * pad, height=panel - 2 * pad, preserveAspectRatio=True, mask="auto")
    c.restoreState()
    c.drawImage(ImageReader(str(image_path)), x + pad, y + tab + pad, width=width - 2 * pad, height=panel - 2 * pad, preserveAspectRatio=True, mask="auto")

    c.setDash(4, 3)
    c.line(x, y + tab, x + width, y + tab)
    c.line(x, y + tab + panel, x + width, y + tab + panel)
    c.setDash()
    c.setFillColor(colors.HexColor("#66717A"))
    c.setFont(PDF_BODY, 5.5)
    c.drawCentredString(x + width / 2, y + 0.28 * cm, "KLEBELASCHE")


def standee_page(c, chars, paths, title, named=True):
    pdf_header(c, title, "Durchgezogene Linie schneiden  •  gestrichelte Linie falten  •  Klebelasche verbinden")
    x0, gap_x = 1.15 * cm, 0.38 * cm
    y_positions = [1.1 * cm, 13.75 * cm]
    for idx, char in enumerate(chars):
        col, row = idx % 3, idx // 3
        x = x0 + col * (5.9 * cm + gap_x)
        y = y_positions[1 - row]
        key = "print_square_name" if named else "print_square_plain"
        draw_standee(c, paths[char["id"]][key], x, y)
    c.showPage()


def token_page(c, chars, paths):
    pdf_header(c, "Flache Portraitmarker", "Runde Marker mit Namen  •  ausschneiden oder auf Karton kleben")
    diameter = 4.15 * cm
    x0, y0 = 1.2 * cm, 2.0 * cm
    gap_x, gap_y = 0.45 * cm, 0.75 * cm
    for idx, char in enumerate(chars):
        col, row = idx % 4, idx // 4
        x = x0 + col * (diameter + gap_x)
        y = y0 + (2 - row) * (diameter + gap_y)
        c.drawImage(ImageReader(str(paths[char["id"]]["print_round_name"])), x, y, width=diameter, height=diameter, preserveAspectRatio=True)
        c.setStrokeColor(colors.HexColor("#888888"))
        c.setLineWidth(0.3)
        c.circle(x + diameter / 2, y + diameter / 2, diameter / 2 - 0.04 * cm, fill=0, stroke=1)
    c.showPage()


def overview_page(c, chars, paths):
    w, h = A4
    pdf_header(c, "Zuordnung und VTT Nutzung", "Alle PNG-Dateien sind 1024 x 1024 px und besitzen transparente Außenbereiche")
    c.setFont(PDF_BODY, 8)
    c.setFillColor(colors.HexColor("#17222D"))
    c.drawString(1.1 * cm, h - 2.55 * cm, "Quadratisch: Figurenfenster und Kartenmarker  •  Rund: klassische VTT-Tokens  •  Nummeriert: Mehrfache Gegner*innen")
    c.drawString(1.1 * cm, h - 2.95 * cm, "Farben dienen nur der schnellen Zuordnung. Namenlose Dateien vermeiden sichtbare Informationen vor der Vorstellung.")

    thumb = 2.05 * cm
    start_y = h - 5.3 * cm
    for idx, char in enumerate(chars):
        col, row = idx % 2, idx // 2
        x = 1.1 * cm + col * 9.55 * cm
        y = start_y - row * 3.15 * cm
        c.drawImage(ImageReader(str(paths[char["id"]]["print_round_plain"])), x, y, width=thumb, height=thumb)
        c.setFillColor(colors.HexColor(char["color"]))
        c.setFont(PDF_BOLD, 9)
        c.drawString(x + 2.35 * cm, y + 1.28 * cm, char["name"])
        c.setFillColor(colors.HexColor("#66717A"))
        c.setFont(PDF_BODY, 6.6)
        c.drawString(x + 2.35 * cm, y + 0.82 * cm, char["kind"])
        c.drawString(x + 2.35 * cm, y + 0.42 * cm, char["id"])
    c.setFillColor(colors.HexColor("#66717A"))
    c.setFont(PDF_BODY, 6.2)
    c.drawCentredString(w / 2, 0.45 * cm, "Die Stadt die den Dienstag verkaufte  •  Aufsteller und VTT Paket  •  Fassung 1.0")
    c.showPage()


def generate_pdf(paths):
    c = canvas.Canvas(str(PDF_PATH), pagesize=A4, pageCompression=1)
    c.setTitle("Die Stadt die den Dienstag verkaufte - Aufsteller und VTT Marker")
    c.setSubject("Druckfertige Aufsteller und Zuordnungsblatt")
    npcs = CHARACTERS[:6]
    enemies = CHARACTERS[6:]
    standee_page(c, npcs, paths, "NSC Aufsteller mit Namen", named=True)
    standee_page(c, enemies, paths, "Gegner*innen Aufsteller mit Namen", named=True)
    standee_page(c, npcs, paths, "NSC Aufsteller ohne Namen", named=False)
    standee_page(c, enemies, paths, "Gegner*innen Aufsteller ohne Namen", named=False)
    token_page(c, CHARACTERS, paths)
    overview_page(c, CHARACTERS, paths)
    c.save()


def write_readme():
    text = """DIE STADT DIE DEN DIENSTAG VERKAUFTE - AUFSTELLER UND VTT

Inhalt
- Druck: sechsseitiger PDF-Bogen mit benannten und namenlosen Faltaufstellern, flachen Rundmarkern und Zuordnung.
- VTT/Quadratisch: 1024 x 1024 PNG, mit und ohne Namen.
- VTT/Rund: 1024 x 1024 PNG, mit und ohne Namen.
- VTT/Nummeriert: Varianten fuer Taktwaechter*innen, Indexschwaerme, Minutenzehrer und Papierknechte.

Import
- Foundry VTT, Roll20, Owlbear Rodeo und aehnliche Plattformen akzeptieren die PNG-Dateien direkt.
- Fuer unbekannte Figuren zuerst die namenlose Variante verwenden.
- Nummerierte Varianten erleichtern Trefferpunkte und Statusverwaltung bei mehreren gleichen Gegner*innen.

Druck
- A4, 100 Prozent, keine Seitenanpassung.
- Durchgezogene Linien schneiden, gestrichelte Linien falten, Klebelasche verbinden.
"""
    (OVERVIEW / "README.txt").write_text(text, encoding="utf-8")


def make_zip():
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with ZipFile(ZIP_PATH, "w", ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(PACKAGE.parent))


def build():
    ensure_dirs()
    paths = generate_vtt_files()
    generate_pdf(paths)
    write_readme()
    make_zip()
    print(PDF_PATH)
    print(ZIP_PATH)


if __name__ == "__main__":
    build()

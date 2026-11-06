from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\Frank.Kroener.KOWOBAU\.codex\generated_images\01a1a566-476b-7ce3-80dc-6824d71723d4\exec-6a81364e-9043-4f0c-bf18-1290b9e0c29e.png")
OUTPUT = ROOT / "outputs" / "Chronotresor_Weg_der_Rueckgabe_illustration_v2_0.png"
ASSET = ROOT / "work" / "assets" / "map_vault_illustrated_v2_0.png"

INK = "#153E4C"
COPPER = "#9F5434"


def font(path: str, size: int):
    return ImageFont.truetype(path, size)


DISPLAY = r"C:\Windows\Fonts\georgiab.ttf"
BODY = r"C:\Windows\Fonts\georgia.ttf"
ITALIC = r"C:\Windows\Fonts\georgiai.ttf"


def centered(draw, xy, text, typeface, fill=INK):
    draw.text(xy, text, font=typeface, fill=fill, anchor="mm")


def main():
    image = Image.open(SOURCE).convert("RGB")
    draw = ImageDraw.Draw(image)

    centered(draw, (356, 62), "Chronotresor", font(DISPLAY, 43))
    centered(draw, (356, 98), "Weg der Rückgabe", font(ITALIC, 26), COPPER)

    labels = [
        ((303, 363), "A  Schleuse", 21),
        ((768, 306), "B  Pfandkammer", 20),
        ((1228, 370), "C  Bilanzsaal", 21),
        ((447, 783), "D  Dienstag", 24),
        ((1012, 782), "E  Nulluhr", 24),
    ]
    for position, text, size in labels:
        centered(draw, position, text, font(DISPLAY, size))

    centered(
        draw,
        (768, 968),
        "Jede Tür verlangt eine Entscheidung, keine bestimmte Probe.",
        font(BODY, 22),
    )
    centered(
        draw,
        (768, 995),
        "Sehr revolutionär für eine Tür.",
        font(ITALIC, 21),
        COPPER,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    image.save(ASSET, optimize=True)
    print(OUTPUT)
    print(ASSET)


if __name__ == "__main__":
    main()

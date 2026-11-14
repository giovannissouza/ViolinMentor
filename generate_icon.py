from pathlib import Path

from PIL import Image, ImageDraw


SIZE = 512
OUTPUT = Path(__file__).resolve().parent / "assets" / "violino.ico"


def _curve(start, control_one, control_two, end, steps=32):
    points = []
    for index in range(steps + 1):
        t = index / steps
        inverse = 1 - t
        x = (
            inverse**3 * start[0]
            + 3 * inverse**2 * t * control_one[0]
            + 3 * inverse * t**2 * control_two[0]
            + t**3 * end[0]
        )
        y = (
            inverse**3 * start[1]
            + 3 * inverse**2 * t * control_one[1]
            + 3 * inverse * t**2 * control_two[1]
            + t**3 * end[1]
        )
        points.append((round(x), round(y)))
    return points


def _body_shape():
    segments = [
        ((256, 207), (220, 188), (182, 199), (176, 244)),
        ((176, 244), (169, 278), (195, 297), (216, 313)),
        ((216, 313), (226, 324), (220, 338), (203, 354)),
        ((203, 354), (180, 376), (174, 410), (191, 438)),
        ((191, 438), (210, 470), (240, 473), (256, 460)),
        ((256, 460), (272, 473), (302, 470), (321, 438)),
        ((321, 438), (338, 410), (332, 376), (309, 354)),
        ((309, 354), (292, 338), (286, 324), (296, 313)),
        ((296, 313), (317, 297), (343, 278), (336, 244)),
        ((336, 244), (330, 199), (292, 188), (256, 207)),
    ]
    points = []
    for segment in segments:
        points.extend(_curve(*segment)[:-1])
    return points


def _draw_icon():
    image = Image.new("RGBA", (SIZE, SIZE), (8, 18, 30, 255))
    pixels = image.load()
    for y in range(SIZE):
        for x in range(SIZE):
            distance = ((x - 250) ** 2 + (y - 230) ** 2) ** 0.5
            glow = max(0, 1 - distance / 430)
            pixels[x, y] = (
                int(8 + 5 * glow),
                int(18 + 34 * glow),
                int(30 + 42 * glow),
                255,
            )

    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle((12, 12, 500, 500), radius=112, fill=255)
    image.putalpha(mask)
    draw = ImageDraw.Draw(image)

    teal = (91, 220, 210, 255)
    pale_teal = (182, 255, 242, 255)
    gold = (246, 190, 105, 255)
    dark_wood = (73, 37, 29, 255)
    wood = (171, 83, 47, 255)
    light_wood = (220, 133, 71, 255)

    draw.rounded_rectangle(
        (18, 18, 494, 494),
        radius=105,
        outline=(91, 220, 210, 125),
        width=3,
    )
    draw.ellipse((91, 77, 421, 407), outline=(91, 220, 210, 35), width=2)

    # Scroll, pegbox and neck.
    draw.rounded_rectangle((241, 97, 271, 287), radius=12, fill=light_wood)
    draw.ellipse((223, 54, 276, 111), fill=gold)
    draw.ellipse((237, 68, 289, 119), fill=light_wood, outline=pale_teal, width=4)
    draw.ellipse((249, 80, 275, 106), fill=(12, 31, 43, 255))
    draw.rounded_rectangle((235, 114, 277, 278), radius=15, fill=dark_wood)
    for y in (135, 160, 185):
        draw.rounded_rectangle((211, y, 246, y + 9), radius=4, fill=gold)
        draw.rounded_rectangle((267, y + 5, 301, y + 14), radius=4, fill=gold)
        draw.ellipse((205, y - 2, 217, y + 10), fill=pale_teal)
        draw.ellipse((295, y + 3, 307, y + 15), fill=pale_teal)

    draw.polygon(_body_shape(), fill=wood, outline=gold)
    draw.line(
        _curve((183, 244), (199, 205), (233, 201), (256, 211))
        + _curve((256, 211), (279, 201), (313, 205), (329, 244))[1:],
        fill=light_wood,
        width=5,
        joint="curve",
    )

    # Fingerboard and four strings.
    draw.polygon([(240, 143), (272, 143), (282, 359), (230, 359)], fill=dark_wood)
    for x in (246, 253, 260, 267):
        draw.line((x, 103, x + (x - 256) // 2, 404), fill=pale_teal, width=2)

    # Bridge and modern, simplified f-holes.
    draw.polygon(
        [(226, 371), (286, 371), (278, 391), (234, 391)],
        fill=gold,
        outline=(255, 224, 167, 255),
    )
    for x, direction in ((213, -1), (299, 1)):
        points = _curve(
            (x, 314),
            (x + direction * 11, 326),
            (x - direction * 9, 339),
            (x, 350),
        )
        points += _curve(
            (x, 350),
            (x + direction * 9, 360),
            (x - direction * 8, 369),
            (x, 381),
        )[1:]
        draw.line(points, fill=dark_wood, width=8, joint="curve")
        draw.ellipse((x - 4, 307, x + 4, 315), fill=pale_teal)
        draw.ellipse((x - 4, 380, x + 4, 388), fill=pale_teal)

    draw.ellipse((248, 428, 264, 444), fill=(255, 216, 145, 255))
    return image


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _draw_icon().save(
        OUTPUT,
        format="ICO",
        sizes=[(16, 16), (32, 32), (64, 64), (256, 256)],
    )
    with Image.open(OUTPUT) as icon:
        expected = {(16, 16), (32, 32), (64, 64), (256, 256)}
        actual = icon.info.get("sizes")
        if actual != expected:
            raise RuntimeError(f"Unexpected icon sizes: {actual}")
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()

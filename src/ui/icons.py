from PIL import Image, ImageDraw
from customtkinter import CTkImage

S = 20
ACCENT = "#0ea76a"
ACCENT_FILLED = "#ffffff"


def _img(draw_fn, size=S):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(img))
    return CTkImage(img, img, size=(size, size))


def mic():
    def draw(d):
        cx = S / 2
        d.rounded_rectangle([cx - 4, 2, cx + 4, 13], radius=3, fill=ACCENT)
        d.rectangle([cx - 1, 13, cx + 1, 15], fill=ACCENT)
        d.arc([cx - 4, 14, cx + 4, 19], 0, 180, fill=ACCENT, width=2)
    return _img(draw)


def mic_filled():
    def draw(d):
        cx = S / 2
        d.rounded_rectangle([cx - 4, 2, cx + 4, 13], radius=3, fill=ACCENT_FILLED)
        d.rectangle([cx - 1, 13, cx + 1, 15], fill=ACCENT_FILLED)
        d.arc([cx - 4, 14, cx + 4, 19], 0, 180, fill=ACCENT_FILLED, width=2)
    return _img(draw)


def speaker():
    def draw(d):
        d.rounded_rectangle([2, 5, 8, 15], radius=2, fill=ACCENT)
        d.polygon([(8, 5), (14, 10), (8, 15)], fill=ACCENT)
        for xr in (14, 17):
            d.arc([xr, 5, xr + 5, 15], -50, 50, fill=ACCENT, width=2)
    return _img(draw)


def arrows():
    def draw(d):
        cy = S / 2
        # left arrow
        d.polygon([(5, cy), (10, cy - 4), (10, cy + 4)], fill=ACCENT)
        # right arrow
        d.polygon([(15, cy), (10, cy - 4), (10, cy + 4)], fill=ACCENT)
    return _img(draw)

from PIL import Image, ImageDraw
from customtkinter import CTkImage

_BASE = 48
_DISPLAY = 18
ACCENT = "#0ea76a"
ACCENT_FILLED = "#ffffff"


def _img(draw_fn):
    img = Image.new("RGBA", (_BASE, _BASE), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(img))
    return img


def _draw_mic(d, color):
    cx = _BASE / 2
    d.rounded_rectangle([cx - 10, 4, cx + 10, 32], radius=7, fill=color)
    d.rectangle([cx - 3, 32, cx + 3, 37], fill=color)
    d.arc([cx - 10, 35, cx + 10, 46], 0, 180, fill=color, width=4)


def _draw_speaker(d, color):
    d.rounded_rectangle([4, 12, 20, 36], radius=4, fill=color)
    d.polygon([(20, 12), (34, 24), (20, 36)], fill=color)
    for xr in (33, 41):
        d.arc([xr, 11, xr + 12, 37], -50, 50, fill=color, width=3)


def _draw_arrows(d, color):
    cy = _BASE / 2
    d.polygon([(12, cy), (24, cy - 10), (24, cy + 10)], fill=color)
    d.polygon([(36, cy), (24, cy - 10), (24, cy + 10)], fill=color)


_MIC_IMG = _img(lambda d: _draw_mic(d, ACCENT))
_MIC_FILLED_IMG = _img(lambda d: _draw_mic(d, ACCENT_FILLED))
_SPEAKER_IMG = _img(lambda d: _draw_speaker(d, ACCENT))
_ARROWS_IMG = _img(lambda d: _draw_arrows(d, ACCENT))

mic = CTkImage(_MIC_IMG, _MIC_IMG, size=(_DISPLAY, _DISPLAY))
mic_filled = CTkImage(_MIC_FILLED_IMG, _MIC_FILLED_IMG, size=(_DISPLAY, _DISPLAY))
speaker = CTkImage(_SPEAKER_IMG, _SPEAKER_IMG, size=(_DISPLAY, _DISPLAY))
arrows = CTkImage(_ARROWS_IMG, _ARROWS_IMG, size=(_DISPLAY, _DISPLAY))

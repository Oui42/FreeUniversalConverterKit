"""Lista konwerterów. Nowy konwerter: plik w tym folderze + wpis w CONVERTERS (kolejność = kolejność w menu)."""
from .base import Cancelled, ConvertError, Converter
from .dav_mp4 import DavToMp4
from .webp_png import WebpToPng

CONVERTERS = [DavToMp4(), WebpToPng()]


def by_id(cid):
    return next((c for c in CONVERTERS if c.id == cid), None)


def detect(paths):
    """Konwerter dla przeciągniętych plików/folderów – gdy pasuje dokładnie jeden, inaczej None."""
    found = [(c, files) for c in CONVERTERS if (files := c.collect(paths))]
    return found[0] if len(found) == 1 else (None, [])


__all__ = ["CONVERTERS", "Cancelled", "ConvertError", "Converter", "by_id", "detect"]

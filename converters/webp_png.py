"""WEBP → PNG (Pillow).

Przezroczystość, profil kolorów (ICC) i EXIF zostają. Animowany WEBP zamienia się w animowany PNG
(APNG) z tymi samymi czasami klatek – przeglądarki i większość programów go odtwarza, a te, które
APNG nie znają, pokazują pierwszą klatkę.
"""
from PIL import Image, UnidentifiedImageError

from .base import Cancelled, ConvertError, Converter


def _plural_pl(n, one, few, many):
    if n == 1:
        return one
    return few if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else many


class WebpToPng(Converter):
    id = "webp-png"
    src_ext = (".webp",)
    dst_ext = ".png"
    names = {"pl": ("WEBP → PNG", "obrazy z internetu → zwykłe obrazy"),
             "en": ("WEBP → PNG", "web images → regular images")}
    file_type = {"pl": "Obrazy WEBP (.webp)", "en": "WEBP images (.webp)"}
    space_factor = 12  # PNG bywa kilka razy większy niż WEBP

    def _convert(self, src, tmp, progress, cancel):
        try:
            im = Image.open(src)
            im.load()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as e:
            raise ConvertError("bad_image", repr(e), fmt="WEBP")
        extra = {k: im.info[k] for k in ("icc_profile", "exif") if im.info.get(k)}
        n = getattr(im, "n_frames", 1)
        try:
            if n > 1:
                frames, durations = [], []
                for i in range(n):
                    if cancel.is_set():
                        raise Cancelled()
                    im.seek(i)
                    frames.append(im.convert("RGBA"))  # klatki z dekodera są już złożone w całość
                    # czas klatki Pillow uzupełnia dopiero przy jej wczytaniu – czytać PO convert()
                    durations.append(im.info.get("duration") or 100)
                    progress(0.8 * (i + 1) / n)
                # disposal=0 / blend=0: każda klatka w całości zastępuje poprzednią
                frames[0].save(tmp, format="PNG", save_all=True, append_images=frames[1:], duration=durations,
                               loop=im.info.get("loop", 0), disposal=0, blend=0, **extra)
            else:
                if im.mode not in ("RGB", "RGBA", "L", "LA", "P"):
                    im = im.convert("RGBA")
                im.save(tmp, format="PNG", **extra)
        except (OSError, ValueError) as e:
            raise ConvertError("write_failed", repr(e))
        return {"size": im.size, "frames": n}

    def describe(self, info, lang):
        w, h = info["size"]
        text = f"{w}×{h}"
        n = info["frames"]
        if n > 1:
            text += (f", animacja: {n} {_plural_pl(n, 'klatka', 'klatki', 'klatek')}" if lang == "pl"
                     else f", animated: {n} frames")
        return text

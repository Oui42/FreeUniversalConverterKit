"""Wspólna część wszystkich konwerterów: błędy z komunikatami PL/EN, zapis przez plik tymczasowy.

Nowy konwerter = klasa dziedzicząca po Converter z ustawionymi polami i metodą _convert(),
dopisana do listy CONVERTERS w converters/__init__.py.
"""
import os
import shutil
import threading
from pathlib import Path

# komunikaty dla użytkownika: klucz → {język: tekst}
MESSAGES = {
    "no_ffmpeg": {"pl": "Brakuje programu ffmpeg potrzebnego do zamiany filmów.",
                  "en": "The ffmpeg program needed to convert videos is missing."},
    "no_frames": {"pl": "W tym pliku nie ma obrazu – może być pusty albo uszkodzony.",
                  "en": "This file contains no video – it may be empty or damaged."},
    "write_failed": {"pl": "Nie udało się zapisać pliku.",
                     "en": "The file could not be saved."},
    "unreadable": {"pl": "Nie udało się odczytać nagrania – plik może być uszkodzony "
                         "albo pochodzić z nietypowego rejestratora.",
                   "en": "The recording could not be read – the file may be damaged "
                         "or come from an unusual recorder."},
    "bad_image": {"pl": "Nie udało się odczytać obrazu – plik może być uszkodzony albo nie jest to obraz {fmt}.",
                  "en": "The image could not be read – the file may be damaged or is not a {fmt} image."},
    "not_found": {"pl": "Nie znaleziono pliku – mógł zostać przeniesiony albo usunięty.",
                  "en": "File not found – it may have been moved or deleted."},
    "no_space": {"pl": "Za mało miejsca na dysku, żeby zapisać plik.",
                 "en": "Not enough disk space to save the file."},
    "no_access": {"pl": "Brak dostępu do pliku albo folderu (może plik jest otwarty w innym programie?).",
                  "en": "No access to the file or folder (is the file open in another program?)."},
    "unexpected": {"pl": "Nieoczekiwany błąd.", "en": "Unexpected error."},
}


class ConvertError(Exception):
    """Błąd z komunikatem zrozumiałym dla użytkownika (details = techniczne szczegóły)."""

    def __init__(self, key, details="", **params):
        self.key = key
        self.details = details
        self.params = params
        super().__init__(self.message("pl"))

    def message(self, lang="pl"):
        text = MESSAGES[self.key].get(lang) or MESSAGES[self.key]["pl"]
        return text.format(**self.params)


class Cancelled(Exception):
    pass


class Converter:
    id = ""                 # np. "dav-mp4" – używany w wierszu poleceń
    src_ext = ()            # rozszerzenia wejściowe, małymi literami, z kropką
    dst_ext = ""            # rozszerzenie wynikowe
    names = {}              # język → (tytuł kafelka, podpis kafelka)
    file_type = {}          # język → opis typu plików w oknie wyboru
    space_factor = 1.1      # ile razy więcej miejsca niż plik źródłowy trzeba mieć na dysku

    @property
    def label(self):
        """Np. „DAV → MP4” (z rozszerzeń)."""
        return f"{self.src_ext[0][1:].upper()} → {self.dst_ext[1:].upper()}"

    def output_for(self, src):
        return Path(src).with_suffix(self.dst_ext)

    def accepts(self, path):
        return Path(path).suffix.lower() in self.src_ext

    def collect(self, paths):
        """Pliki tego konwertera z podanych plików i folderów (także podfolderów), bez powtórzeń."""
        files = []
        for p in map(Path, paths):
            if p.is_dir():
                files += sorted(f for f in p.rglob("*") if f.is_file() and self.accepts(f))
            elif p.is_file() and self.accepts(p):
                files.append(p)
        return list(dict.fromkeys(files))

    def convert(self, src, dst=None, progress=lambda f: None, cancel=None):
        """Zamienia src na dst (domyślnie obok, z nowym rozszerzeniem). Zwraca opis wyniku (słownik
        dla describe()). Zapis idzie do pliku tymczasowego – przerwana lub nieudana zamiana nie
        zostawia uszkodzonego pliku."""
        src = Path(src)
        dst = Path(dst) if dst else self.output_for(src)
        cancel = cancel or threading.Event()
        tmp = dst.with_name(dst.name + ".tmp")
        try:
            if not src.exists():
                raise ConvertError("not_found")
            if shutil.disk_usage(dst.parent).free < src.stat().st_size * self.space_factor:
                raise ConvertError("no_space")
            info = self._convert(src, tmp, progress, cancel)
            os.replace(tmp, dst)
            st = src.stat()
            os.utime(dst, (st.st_atime, st.st_mtime))  # data wyniku = data pliku źródłowego
            progress(1.0)
            return info
        except PermissionError as e:
            raise ConvertError("no_access", str(e))
        finally:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    def _convert(self, src, tmp, progress, cancel):
        raise NotImplementedError

    def describe(self, info, lang):
        """Krótki opis wyniku do listy plików, np. „12 min” albo „1920×1080”."""
        return ""

"""FreeUniversalConverterKit – okno programu (duże, proste, dla mniej wprawnych użytkowników), PL/EN.

Menu główne → wybór rodzaju zamiany → wybór plików/folderu → postęp → wynik.
Wyniki zapisują się obok plików źródłowych, z tą samą nazwą. Pliki przeciągnięte na ikonę programu
zamieniają się od razu, gdy pasuje do nich dokładnie jeden konwerter.
Wybrany język jest zapamiętany w %APPDATA%\\FreeUniversalConverterKit\\settings.json
(program jest jednym plikiem .exe – obok niego nic nie zapisujemy).
"""
import json
import locale
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import converters

APP_NAME = "FreeUniversalConverterKit"

# kolory
BG = "#f4f6f9"
CARD = "#ffffff"
HEADER = "#1d4f91"
PRIMARY = "#1d6fd8"
PRIMARY_HOVER = "#1558b0"
TEXT = "#1c2430"
MUTED = "#5b6675"
GREEN = "#1f9d55"
RED = "#c62828"
BORDER = "#d9dee6"
FONT = "Segoe UI"

# {src}/{dst} = nazwy formatów wybranego konwertera, np. DAV / MP4
TEXTS = {
    "pl": {
        "header_sub": "Darmowe i proste zamiany formatów plików.\nDziała bez internetu i bez instalacji.",
        "menu_question": "Co chcesz zamienić?",
        "hint": "Wskazówka: pliki można też po prostu przeciągnąć na ikonę programu.",
        "conv_question": "Zamiana plików {src} na {dst}",
        "btn_files": "Wybierz pliki", "btn_files_sub": "jeden lub kilka plików {src}",
        "btn_folder": "Wybierz folder", "btn_folder_sub": "wszystkie pliki {src} z folderu",
        "tip": "Gotowe pliki {dst} zapiszą się w tym samym folderze co pliki {src}, pod tą samą nazwą.\n"
               "Pliki {src} zostają nietknięte.",
        "btn_back": "←  Menu",
        "working": "Trwa zamiana plików…",
        "working_sub": "Można w tym czasie korzystać z komputera. Nie wyłączaj go do końca.",
        "file_n": "Plik {i} z {n}:  {name}",
        "all": "Wszystkie pliki:",
        "eta": "Do końca zostało {t}",
        "less_minute": "mniej niż minuta",
        "col_name": "Plik", "col_status": "Stan",
        "st_wait": "Czeka", "st_run": "Trwa…", "st_run_pct": "Trwa…  {p}%",
        "st_ok": "Gotowe ✔", "st_skip": "Był już zamieniony ✔", "st_err": "Nie udało się ✘",
        "st_cancel": "Przerwano", "st_skipped": "Pominięto",
        "btn_stop": "Zatrzymaj", "btn_open": "Otwórz folder z plikami", "btn_again": "Zamień kolejne pliki",
        "btn_menu": "Menu",
        "done_ok": "Gotowe! Wszystkie pliki zamienione ✔",
        "done_ok_sub": "Plików: {n}. Są w tym samym folderze co pliki źródłowe.",
        "done_err": "Gotowe – nie wszystkie pliki udało się zamienić",
        "done_err_sub": "Zamienione: {ok} z {n}. Nieudane są zaznaczone na czerwono.",
        "done_cancel": "Zamiana została zatrzymana",
        "done_cancel_sub": "Gotowe pliki: {n}. Aby dokończyć, wybierz pliki jeszcze raz – "
                           "gotowe zostaną pominięte.",
        "stopping": "Zatrzymywanie…",
        "dlg_files": "Wybierz pliki {src} do zamiany",
        "dlg_folder": "Wybierz folder z plikami {src}",
        "no_files": "W tym folderze (ani w folderach w nim) nie ma plików {src}.\n\nWybierz inny folder.",
        "errors_list": "Tych plików nie udało się zamienić:",
        "errors_more": "…i {n} innych.",
        "ask_stop": "Czy na pewno zatrzymać zamianę?\n\nGotowe pliki zostaną zachowane.",
        "ask_close": "Zamiana jeszcze trwa.\n\nCzy na pewno zamknąć program? "
                     "Plik, który jest teraz zamieniany, nie zostanie zapisany.",
    },
    "en": {
        "header_sub": "Free and simple file format conversions.\nWorks offline, no installation needed.",
        "menu_question": "What would you like to convert?",
        "hint": "Tip: you can also simply drag files onto the program icon.",
        "conv_question": "Convert {src} files to {dst}",
        "btn_files": "Choose files", "btn_files_sub": "one or more {src} files",
        "btn_folder": "Choose a folder", "btn_folder_sub": "all {src} files in a folder",
        "tip": "Finished {dst} files are saved in the same folder as the {src} files, with the same name.\n"
               "The {src} files are left untouched.",
        "btn_back": "←  Menu",
        "working": "Converting files…",
        "working_sub": "You can keep using the computer. Please don't turn it off until it's done.",
        "file_n": "File {i} of {n}:  {name}",
        "all": "All files:",
        "eta": "Time left: {t}",
        "less_minute": "less than a minute",
        "col_name": "File", "col_status": "Status",
        "st_wait": "Waiting", "st_run": "Working…", "st_run_pct": "Working…  {p}%",
        "st_ok": "Done ✔", "st_skip": "Already converted ✔", "st_err": "Failed ✘",
        "st_cancel": "Stopped", "st_skipped": "Skipped",
        "btn_stop": "Stop", "btn_open": "Open folder", "btn_again": "Convert more files",
        "btn_menu": "Menu",
        "done_ok": "Done! All files converted ✔",
        "done_ok_sub": "Files: {n}. They are in the same folder as the originals.",
        "done_err": "Done – some files could not be converted",
        "done_err_sub": "Converted: {ok} of {n}. Failed ones are marked in red.",
        "done_cancel": "Conversion stopped",
        "done_cancel_sub": "Finished files: {n}. To finish, choose the files again – "
                           "finished ones will be skipped.",
        "stopping": "Stopping…",
        "dlg_files": "Choose {src} files to convert",
        "dlg_folder": "Choose a folder with {src} files",
        "no_files": "There are no {src} files in this folder (or its subfolders).\n\n"
                    "Please choose another folder.",
        "errors_list": "These files could not be converted:",
        "errors_more": "…and {n} more.",
        "ask_stop": "Stop converting?\n\nFinished files will be kept.",
        "ask_close": "Conversion is still running.\n\nClose the program anyway? "
                     "The file being converted right now will not be saved.",
    },
}

SETTINGS = Path(os.environ.get("APPDATA") or Path.home()) / APP_NAME / "settings.json"


def resource(name):
    base = getattr(sys, "_MEIPASS", None) or Path(__file__).parent
    return Path(base) / name


def load_lang():
    try:
        lang = json.loads(SETTINGS.read_text(encoding="utf-8")).get("lang")
        if lang in TEXTS:
            return lang
    except (OSError, ValueError):
        pass
    return system_lang()


def system_lang():
    """Polski, gdy Windows jest po polsku, w każdym innym przypadku angielski."""
    try:
        import ctypes
        code = locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), "")
    except (AttributeError, OSError):
        code = locale.getlocale()[0] or ""
    return "pl" if code.lower().startswith("pl") else "en"


def save_lang(lang):
    try:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(json.dumps({"lang": lang}), encoding="utf-8")
    except OSError:
        pass  # brak zapisu nie może przeszkadzać w pracy


def minutes_text(lang, seconds):
    if seconds < 60:
        return TEXTS[lang]["less_minute"]
    m = round(seconds / 60)
    if lang == "en":
        return f"about {m} minute{'s' if m != 1 else ''}"
    if m == 1:
        word = "minuta"
    elif 2 <= m % 10 <= 4 and not 12 <= m % 100 <= 14:
        word = "minuty"
    else:
        word = "minut"
    return f"około {m} {word}"


class BigButton(tk.Frame):
    """Duży przycisk z tytułem i podpisem, podświetlany pod myszą."""

    def __init__(self, parent, command, primary=True, subtitle=True, size=16):
        self.bg, self.hover = (PRIMARY, PRIMARY_HOVER) if primary else (CARD, "#e9eef6")
        fg, sub_fg = ("white", "#dbe8fb") if primary else (TEXT, MUTED)
        super().__init__(parent, bg=self.bg, cursor="hand2", highlightthickness=0 if primary else 1,
                         highlightbackground=BORDER)
        self.command = command
        pad_y = 18 if size >= 16 else 10
        self.title = tk.Label(self, font=(FONT, size, "bold"), bg=self.bg, fg=fg)
        self.title.pack(padx=28 if size >= 16 else 18, pady=(pad_y, 2 if subtitle else pad_y))
        self.labels = [self.title]
        self.sub = None
        if subtitle:
            self.sub = tk.Label(self, font=(FONT, 11), bg=self.bg, fg=sub_fg)
            self.sub.pack(padx=28, pady=(0, pad_y))
            self.labels.append(self.sub)
        for w in [self, *self.labels]:
            w.bind("<Enter>", lambda e: self._paint(self.hover))
            w.bind("<Leave>", lambda e: self._paint(self.bg))
            w.bind("<Button-1>", lambda e: self.command())

    def set_text(self, title, subtitle=None):
        self.title.config(text=title)
        if self.sub is not None:
            self.sub.config(text=subtitle or "")

    def _paint(self, color):
        for w in [self, *self.labels]:
            w.config(bg=color)


class FlagButton(tk.Canvas):
    """Flaga do wyboru języka (rysowana – Windows nie wyświetla flag z emoji)."""

    def __init__(self, parent, kind, scale, command):
        stripe = max(3, round(3 * scale))
        h = 13 * stripe
        w = round(h * 1.6)
        pad = max(3, round(3 * scale))
        super().__init__(parent, width=w + 2 * pad, height=h + 2 * pad, bg=HEADER, highlightthickness=0,
                         cursor="hand2")
        x0, y0 = pad, pad
        if kind == "pl":
            self.create_rectangle(x0, y0, x0 + w, y0 + h / 2, fill="white", width=0)
            self.create_rectangle(x0, y0 + h / 2, x0 + w, y0 + h, fill="#dc143c", width=0)
        else:  # USA: 13 pasów, niebieski kanton z gwiazdkami (kropki)
            for i in range(13):
                self.create_rectangle(x0, y0 + i * stripe, x0 + w, y0 + (i + 1) * stripe,
                                      fill="#b22234" if i % 2 == 0 else "white", width=0)
            cw, ch = round(w * 0.4), 7 * stripe
            self.create_rectangle(x0, y0, x0 + cw, y0 + ch, fill="#3c3b6e", width=0)
            r = max(0.6, 0.5 * scale)
            for row in range(4):
                for col in range(5):
                    cx = x0 + cw * (col + 0.5) / 5
                    cy = y0 + ch * (row + 0.5) / 4
                    self.create_oval(cx - r, cy - r, cx + r, cy + r, fill="white", width=0)
        self.ring = self.create_rectangle(1, 1, w + 2 * pad - 1, h + 2 * pad - 1, outline="", width=2)
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Enter>", lambda e: self.selected or self.itemconfig(self.ring, outline="#8fb3e6"))
        self.bind("<Leave>", lambda e: self.selected or self.itemconfig(self.ring, outline=""))
        self.selected = False

    def select(self, on):
        self.selected = on
        self.itemconfig(self.ring, outline="white" if on else "")


class App:
    def __init__(self, root, initial_paths):
        self.root = root
        self.lang = load_lang()
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.worker = None
        self.conv = converters.CONVERTERS[0]   # wybrany konwerter
        self.screen = "menu"
        self.outputs = []
        self.files = []
        self.rows = []
        self.row_state = []          # (klucz, argumenty, tag) dla każdego wiersza listy
        self.title_state = ("working", {}, TEXT)
        self.subtitle_state = ("working_sub", {})
        self.current = None
        self.eta_seconds = None

        root.configure(bg=BG)
        root.minsize(780, 620)
        try:
            root.iconbitmap(default=str(resource("app.ico")))
        except tk.TclError:
            pass
        self._center(840, 680)
        self._styles()

        header = tk.Frame(root, bg=HEADER)
        header.pack(fill="x")
        top = tk.Frame(header, bg=HEADER)
        top.pack(fill="x", padx=(28, 20), pady=(20, 0))
        tk.Label(top, text=APP_NAME, font=(FONT, 22, "bold"), bg=HEADER, fg="white").pack(side="left")
        flags = tk.Frame(top, bg=HEADER)
        flags.pack(side="right", anchor="n")
        scale = root.winfo_fpixels("1i") / 96
        self.flags = {}
        for code in ("en", "pl"):
            f = FlagButton(flags, "us" if code == "en" else "pl", scale, lambda c=code: self.set_lang(c))
            f.pack(side="left", padx=(6, 0))
            self.flags[code] = f
        self.h_sub = tk.Label(header, font=(FONT, 12), bg=HEADER, fg="#cfe0f7", justify="left")
        self.h_sub.pack(anchor="w", padx=28, pady=(4, 20))

        self.body = tk.Frame(root, bg=BG)
        self.body.pack(fill="both", expand=True, padx=28, pady=24)
        self._build_menu()
        self._build_conv()
        self._build_work()
        self.show_menu()

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(100, self._poll)
        if initial_paths:
            root.after(300, lambda: self._open_dropped(initial_paths))

    def t(self, key, **kw):
        return TEXTS[self.lang][key].format(**kw)

    def fmt(self):
        """Nazwy formatów wybranego konwertera do tekstów: {src}, {dst}."""
        return {"src": self.conv.src_ext[0][1:].upper(), "dst": self.conv.dst_ext[1:].upper()}

    # --- wygląd ---------------------------------------------------------------------------

    def _center(self, w, h):
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(w, sw - 40), min(h, sh - 80)
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{max((sh - h) // 2 - 20, 0)}")

    def _styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("File.Horizontal.TProgressbar", thickness=26, troughcolor="#e3e8ef", background=PRIMARY,
                    bordercolor="#e3e8ef", lightcolor=PRIMARY, darkcolor=PRIMARY)
        s.configure("All.Horizontal.TProgressbar", thickness=14, troughcolor="#e3e8ef", background=GREEN,
                    bordercolor="#e3e8ef", lightcolor=GREEN, darkcolor=GREEN)
        s.configure("Files.Treeview", font=(FONT, 12), rowheight=34, background=CARD, fieldbackground=CARD,
                    bordercolor=BORDER, foreground=TEXT)
        s.configure("Files.Treeview.Heading", font=(FONT, 11, "bold"), background="#e9eef6",
                    foreground=MUTED, relief="flat")
        s.map("Files.Treeview", background=[("selected", "#dbe8fb")], foreground=[("selected", TEXT)])

    def _build_menu(self):
        f = self.menu_frame = tk.Frame(self.body, bg=BG)
        self.l_menu_q = tk.Label(f, font=(FONT, 18, "bold"), bg=BG, fg=TEXT)
        self.l_menu_q.pack(anchor="w", pady=(4, 16))
        grid = tk.Frame(f, bg=BG)
        grid.pack(fill="x")
        cols = 2
        for c in range(cols):
            grid.columnconfigure(c, weight=1, uniform="tile")
        self.tiles = []
        for i, conv in enumerate(converters.CONVERTERS):
            tile = BigButton(grid, lambda c=conv: self.show_conv(c))
            tile.grid(row=i // cols, column=i % cols, sticky="nsew",
                      padx=(0 if i % cols == 0 else 10, 10 if i % cols < cols - 1 else 0), pady=(0, 20))
            self.tiles.append((tile, conv))
        self.l_menu_hint = tk.Label(f, font=(FONT, 11), bg=BG, fg=MUTED)
        self.l_menu_hint.pack(anchor="w", pady=(4, 0))

    def _build_conv(self):
        f = self.conv_frame = tk.Frame(self.body, bg=BG)
        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", pady=(0, 18))
        self.btn_back = BigButton(top, self.show_menu, primary=False, subtitle=False, size=12)
        self.btn_back.pack(side="left")
        self.l_conv_q = tk.Label(top, font=(FONT, 18, "bold"), bg=BG, fg=TEXT)
        self.l_conv_q.pack(side="left", padx=(18, 0))
        row = tk.Frame(f, bg=BG)
        row.pack(fill="x")
        self.btn_files = BigButton(row, self.pick_files)
        self.btn_files.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.btn_folder = BigButton(row, self.pick_folder)
        self.btn_folder.pack(side="left", fill="x", expand=True, padx=(10, 0))

        tip = tk.Frame(f, bg="#e8f1fc", highlightthickness=1, highlightbackground="#c9dcf5")
        tip.pack(fill="x", pady=(28, 0))
        self.l_tip = tk.Label(tip, font=(FONT, 12), bg="#e8f1fc", fg=TEXT, justify="left")
        self.l_tip.pack(anchor="w", padx=18, pady=14)
        self.l_hint = tk.Label(f, font=(FONT, 11), bg=BG, fg=MUTED)
        self.l_hint.pack(anchor="w", pady=(14, 0))

    def _build_work(self):
        f = self.work_frame = tk.Frame(self.body, bg=BG)

        self.title = tk.Label(f, font=(FONT, 18, "bold"), bg=BG, fg=TEXT, anchor="w")
        self.title.pack(fill="x")
        self.subtitle = tk.Label(f, font=(FONT, 12), bg=BG, fg=MUTED, anchor="w", justify="left",
                                 wraplength=760)
        self.subtitle.pack(fill="x", pady=(2, 12))

        self.progress_box = tk.Frame(f, bg=BG)
        self.progress_box.pack(fill="x")
        line = tk.Frame(self.progress_box, bg=BG)
        line.pack(fill="x")
        self.file_label = tk.Label(line, font=(FONT, 12, "bold"), bg=BG, fg=TEXT, anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)
        self.percent = tk.Label(line, font=(FONT, 16, "bold"), bg=BG, fg=PRIMARY)
        self.percent.pack(side="right")
        self.file_bar = ttk.Progressbar(self.progress_box, style="File.Horizontal.TProgressbar", maximum=1000)
        self.file_bar.pack(fill="x", pady=(4, 12))
        line2 = tk.Frame(self.progress_box, bg=BG)
        line2.pack(fill="x")
        self.l_all = tk.Label(line2, font=(FONT, 11), bg=BG, fg=MUTED)
        self.l_all.pack(side="left")
        self.eta = tk.Label(line2, font=(FONT, 11), bg=BG, fg=MUTED)
        self.eta.pack(side="right")
        self.all_bar = ttk.Progressbar(self.progress_box, style="All.Horizontal.TProgressbar", maximum=1000)
        self.all_bar.pack(fill="x", pady=(4, 14))

        # przyciski przypięte do dołu – lista nie może ich wypchnąć poza okno
        self.buttons = tk.Frame(f, bg=BG)
        self.buttons.pack(side="bottom", fill="x", pady=(16, 0))
        self.btn_stop = BigButton(self.buttons, self.stop, primary=False, subtitle=False)
        self.btn_open = BigButton(self.buttons, self.open_folder, subtitle=False)
        self.btn_again = BigButton(self.buttons, lambda: self.show_conv(self.conv), primary=False, subtitle=False)
        self.btn_menu = BigButton(self.buttons, self.show_menu, primary=False, subtitle=False)

        box = tk.Frame(f, bg=BORDER)
        box.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(box, columns=("status",), style="Files.Treeview", selectmode="none")
        self.tree.column("#0", width=420, anchor="w")
        self.tree.column("status", width=270, anchor="w")
        for tag, color in (("wait", MUTED), ("run", PRIMARY), ("ok", GREEN), ("err", RED)):
            self.tree.tag_configure(tag, foreground=color)
        sb = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        sb.pack(side="right", fill="y")

    def _show(self, screen):
        self.screen = screen
        for name, frame in (("menu", self.menu_frame), ("conv", self.conv_frame), ("work", self.work_frame)):
            if name == screen:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
        self.refresh_texts()

    def show_menu(self):
        self._show("menu")

    def show_conv(self, conv):
        self.conv = conv
        self._show("conv")

    # --- język ----------------------------------------------------------------------------

    def set_lang(self, lang):
        if lang != self.lang:
            self.lang = lang
            save_lang(lang)
            self.refresh_texts()

    def refresh_texts(self):
        t, fmt = self.t, self.fmt()
        for code, flag in self.flags.items():
            flag.select(code == self.lang)
        self.root.title(APP_NAME)
        self.h_sub.config(text=t("header_sub"))
        # menu
        self.l_menu_q.config(text=t("menu_question"))
        for tile, conv in self.tiles:
            title, sub = conv.names[self.lang]
            tile.set_text(title, sub)
        self.l_menu_hint.config(text=t("hint"))
        # ekran konwertera
        self.btn_back.set_text(t("btn_back"))
        self.l_conv_q.config(text=t("conv_question", **fmt))
        self.btn_files.set_text(t("btn_files"), t("btn_files_sub", **fmt))
        self.btn_folder.set_text(t("btn_folder"), t("btn_folder_sub", **fmt))
        self.l_tip.config(text=t("tip", **fmt))
        self.l_hint.config(text=t("hint"))
        # praca
        self.l_all.config(text=t("all"))
        self.btn_stop.set_text(t("btn_stop"))
        self.btn_open.set_text(t("btn_open"))
        self.btn_again.set_text(t("btn_again"))
        self.btn_menu.set_text(t("btn_menu"))
        self.tree.heading("#0", text="  " + t("col_name"), anchor="w")
        self.tree.heading("status", text=t("col_status"), anchor="w")
        key, kw, color = self.title_state
        self.title.config(text=t(key, **kw), fg=color)
        key, kw = self.subtitle_state
        self.subtitle.config(text=t(key, **kw))
        if self.current is not None:
            self.file_label.config(text=t("file_n", i=self.current + 1, n=len(self.files),
                                          name=self.files[self.current].name))
        self._show_eta()
        for i in range(len(self.rows)):
            self._render_row(i)

    def _set_title(self, key, color=TEXT, **kw):
        self.title_state = (key, kw, color)
        self.title.config(text=self.t(key, **kw), fg=color)

    def _set_subtitle(self, key, **kw):
        self.subtitle_state = (key, kw)
        self.subtitle.config(text=self.t(key, **kw))

    def _show_eta(self):
        self.eta.config(text=self.t("eta", t=minutes_text(self.lang, self.eta_seconds))
                        if self.eta_seconds is not None else "")

    # --- wybór plików ---------------------------------------------------------------------

    def _open_dropped(self, paths):
        conv, files = converters.detect(paths)
        if conv:
            self.conv = conv
            self.start(files)

    def pick_files(self):
        patterns = " ".join(f"*{e} *{e.upper()}" for e in self.conv.src_ext)
        paths = filedialog.askopenfilenames(parent=self.root, title=self.t("dlg_files", **self.fmt()),
                                            filetypes=[(self.conv.file_type[self.lang], patterns)])
        if paths:
            self.start(self.conv.collect(paths))

    def pick_folder(self):
        d = filedialog.askdirectory(parent=self.root, title=self.t("dlg_folder", **self.fmt()))
        if not d:
            return
        files = self.conv.collect([d])
        if not files:
            messagebox.showinfo(APP_NAME, self.t("no_files", **self.fmt()), parent=self.root)
            return
        self.start(files)

    # --- praca ----------------------------------------------------------------------------

    def start(self, files):
        if not files or self.worker:
            return
        self.files = files
        self.run_conv = self.conv   # opisy wyników na liście zawsze od konwertera, który je zrobił
        self.outputs = []
        self.cancel.clear()
        self.tree.delete(*self.tree.get_children())
        self.rows = [self.tree.insert("", "end", text="  " + p.name) for p in files]
        self.row_state = [("st_wait", {}, "wait") for _ in files]
        self.current = None
        self.eta_seconds = None
        self._set_title("working")
        self._set_subtitle("working_sub")
        self.progress_box.pack(fill="x", before=self.tree.master)
        self.file_bar["value"] = self.all_bar["value"] = 0
        self.percent.config(text="0%")
        self.file_label.config(text="")
        for b in (self.btn_open, self.btn_again, self.btn_menu):
            b.pack_forget()
        self.btn_stop.pack(side="left")
        self._show("work")

        self.sizes = [p.stat().st_size if p.exists() else 0 for p in files]
        self.total_bytes = sum(self.sizes) or 1
        self.started = time.monotonic()
        self.worker = threading.Thread(target=self._work, args=(self.conv,), daemon=True)
        self.worker.start()

    def _work(self, conv):
        results = []
        for i, src in enumerate(self.files):
            if self.cancel.is_set():
                results.append(("cancel", None))
                self.events.put(("status", i, "st_skipped", {}, "wait"))
                continue
            dst = conv.output_for(src)
            if dst.exists() and dst.stat().st_size > 0:
                results.append(("skip", dst))
                self.events.put(("status", i, "st_skip", {}, "ok"))
                self.events.put(("progress", i, 1.0))
                continue
            self.events.put(("begin", i))
            try:
                info = conv.convert(src, dst, lambda fr, i=i: self.events.put(("progress", i, fr)), self.cancel)
                results.append(("ok", dst))
                self.events.put(("status", i, "st_ok", {"info": info}, "ok"))
            except converters.Cancelled:
                results.append(("cancel", None))
                self.events.put(("status", i, "st_cancel", {}, "err"))
            except converters.ConvertError as e:
                results.append(("err", (src, e)))
                self.events.put(("status", i, "st_err", {}, "err"))
            except Exception as e:  # nieoczekiwany błąd – nie może zatrzymać pozostałych plików
                results.append(("err", (src, converters.ConvertError("unexpected", repr(e)))))
                self.events.put(("status", i, "st_err", {}, "err"))
        self.events.put(("done", results))

    def _poll(self):
        last_progress = None
        try:
            while True:
                ev = self.events.get_nowait()
                kind = ev[0]
                if kind == "begin":
                    i = self.current = ev[1]
                    self.file_label.config(text=self.t("file_n", i=i + 1, n=len(self.files),
                                                       name=self.files[i].name))
                    self._set_row(i, "st_run", {}, "run")
                    self.tree.see(self.rows[i])
                elif kind == "progress":
                    last_progress = ev[1:]
                elif kind == "status":
                    self._set_row(*ev[1:])
                elif kind == "done":
                    self._finish(ev[1])
        except queue.Empty:
            pass
        if last_progress and self.worker:
            self._show_progress(*last_progress)
        self.root.after(100, self._poll)

    def _set_row(self, i, key, kw, tag):
        self.row_state[i] = (key, kw, tag)
        self._render_row(i)

    def _render_row(self, i):
        key, kw, tag = self.row_state[i]
        text = self.t(key, **{k: v for k, v in kw.items() if k != "info"})
        if "info" in kw:
            extra = self.run_conv.describe(kw["info"], self.lang)
            if extra:
                text += f"  ({extra})"
        self.tree.item(self.rows[i], values=(text,), tags=(tag,))

    def _show_progress(self, i, frac):
        frac = max(0.0, min(frac, 1.0))
        self.file_bar["value"] = frac * 1000
        self.percent.config(text=f"{int(frac * 100)}%")
        if frac < 1 and self.row_state[i][0] in ("st_run", "st_run_pct"):
            self._set_row(i, "st_run_pct", {"p": int(frac * 100)}, "run")
        done = sum(self.sizes[:i]) + self.sizes[i] * frac
        total = done / self.total_bytes
        self.all_bar["value"] = total * 1000
        elapsed = time.monotonic() - self.started
        if total > 0.02 and elapsed > 3:
            self.eta_seconds = elapsed / total * (1 - total)
            self._show_eta()

    def _finish(self, results):
        self.worker = None
        self.current = None
        ok = [r for k, r in results if k in ("ok", "skip")]
        errors = [r for k, r in results if k == "err"]
        cancelled = any(k == "cancel" for k, _ in results)
        self.outputs = ok
        self.btn_stop.pack_forget()
        self.progress_box.pack_forget()
        if ok:
            self.btn_open.pack(side="left", padx=(0, 12))
        self.btn_again.pack(side="left", padx=(0, 12))
        self.btn_menu.pack(side="left")

        if cancelled:
            self._set_title("done_cancel")
            self._set_subtitle("done_cancel_sub", n=len(ok))
        elif errors:
            self._set_title("done_err", RED)
            self._set_subtitle("done_err_sub", ok=len(ok), n=len(results))
        else:
            self._set_title("done_ok", GREEN)
            self._set_subtitle("done_ok_sub", n=len(ok))
        self.root.bell()
        if errors:
            msg = "\n\n".join(f"• {src.name}\n   {e.message(self.lang)}" for src, e in errors[:8])
            if len(errors) > 8:
                msg += "\n\n" + self.t("errors_more", n=len(errors) - 8)
            messagebox.showwarning(APP_NAME, self.t("errors_list") + "\n\n" + msg, parent=self.root)

    def stop(self):
        if self.worker and messagebox.askyesno(APP_NAME, self.t("ask_stop"), parent=self.root):
            self.cancel.set()
            self._set_title("stopping")

    def open_folder(self):
        if not self.outputs:
            return
        target = self.outputs[0]
        if target.exists():
            subprocess.Popen(["explorer", "/select,", str(target)])
        else:
            os.startfile(target.parent)

    def on_close(self):
        if self.worker:
            if not messagebox.askyesno(APP_NAME, self.t("ask_close"), parent=self.root):
                return
            self.cancel.set()
            self.worker.join(timeout=5)
        self.root.destroy()


def main():
    if os.name == "nt":
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # ostre napisy na ekranach ze skalowaniem
        except (AttributeError, OSError):
            pass
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_NAME)
        except (AttributeError, OSError):
            pass
    root = tk.Tk()
    App(root, sys.argv[1:])
    try:  # ekran „Starting...” z wersji jednoplikowej (PyInstaller --splash)
        import pyi_splash
        pyi_splash.close()
    except ImportError:
        pass
    root.mainloop()


if __name__ == "__main__":
    main()

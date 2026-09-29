# Third-party notices

The source code in this repository is released under the [MIT License](LICENSE).
The portable `FreeUniversalConverterKit.exe` from the Releases page also contains the following third-party software.

## FFmpeg (used for DAV → MP4)

- The executable bundles an unmodified `ffmpeg.exe` (FFmpeg 7.1, "essentials" build by gyan.dev,
  distributed with the [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) Python package).
- FreeUniversalConverterKit runs it as a separate program; it is not linked into the program's code.
- This FFmpeg build is licensed under the **GNU General Public License version 3** –
  see [licenses/FFmpeg-GPL-3.0.txt](licenses/FFmpeg-GPL-3.0.txt).
- FFmpeg is a trademark of Fabrice Bellard, originator of the FFmpeg project.
- Source code:
  - FFmpeg 7.1: <https://ffmpeg.org/releases/ffmpeg-7.1.tar.xz> (project page: <https://ffmpeg.org>)
  - build scripts and sources of the libraries used in this build: <https://www.gyan.dev/ffmpeg/builds/>

If you need the exact sources and cannot get them from the links above, open an issue in this repository.

## Pillow (used for image conversions, e.g. WEBP → PNG)

[Pillow](https://python-pillow.org) 12 – MIT-CMU License. The Pillow package also contains libraries such as
libwebp, libpng, zlib, libjpeg-turbo and FreeType under their own permissive licenses –
all listed in [licenses/Pillow-LICENSE.txt](licenses/Pillow-LICENSE.txt).

## Python and the Python standard library (incl. Tkinter, Tcl/Tk)

- Python 3.12 – [Python Software Foundation License](https://docs.python.org/3/license.html)
- Tcl/Tk – [Tcl/Tk license](https://www.tcl.tk/software/tcltk/license.html) (BSD-style)

## PyInstaller

The executable is packaged with [PyInstaller](https://pyinstaller.org). Its bootloader is licensed under
the GPL version 2 or later **with a special exception** that allows distributing programs built with it
under any license.

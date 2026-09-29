"""Command-line use without the window:  python cli.py <files and/or folders> [...]

Every file is converted by the converter that matches its extension (.dav → .mp4, .webp → .png, ...).
"""
import sys

import converters


def main(paths):
    jobs = [(c, f) for c in converters.CONVERTERS for f in c.collect(paths)]
    if not jobs:
        known = ", ".join(e for c in converters.CONVERTERS for e in c.src_ext)
        sys.exit(f"Usage: python cli.py <file | folder> [...]   (supported: {known})")
    ok = 0
    for i, (conv, src) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] {conv.label}  {src.name} ... ", end="", flush=True)
        dst = conv.output_for(src)
        if dst.exists() and dst.stat().st_size > 0:
            print("already converted")
            ok += 1
            continue
        try:
            info = conv.convert(src, dst)
            extra = conv.describe(info, "en")
            print("OK" + (f" ({extra})" if extra else ""))
            ok += 1
        except converters.ConvertError as e:
            last = e.details.strip().splitlines()[-1] if e.details.strip() else ""
            print(f"FAILED: {e.message('en')}" + (f"\n    {last}" if last else ""))
    print(f"Done: {ok}/{len(jobs)}")
    return ok == len(jobs)


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1:]) else 1)

#!/usr/bin/env python3
"""Deterministic evidence-preparation helper for District Grading & Evidence.

Mechanical only: render evidence once, create contact sheets, and optionally create
repeated grid-cell band contact sheets. It never OCRs, grades, or infers student identity.
"""
from __future__ import annotations
import argparse, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path

VERSION = "district-grading-evidence-review/1.0"

try:
    from PIL import Image, ImageDraw, ImageOps
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"Pillow is required: {exc}")


def render_pdf(pdf: Path, out_dir: Path, dpi: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []
    # Prefer PyMuPDF when present.
    try:
        import fitz  # type: ignore
        doc = fitz.open(str(pdf))
        scale = dpi / 72.0
        matrix = fitz.Matrix(scale, scale)
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            p = out_dir / f"page-{i:03d}.png"
            pix.save(str(p))
            pages.append(p)
        return pages
    except Exception:
        pass

    # Fallback to pdftoppm if available.
    exe = shutil.which("pdftoppm")
    if not exe:
        raise RuntimeError("Need PyMuPDF (fitz) or pdftoppm to render PDF evidence.")
    prefix = out_dir / "page"
    subprocess.run([exe, "-png", "-r", str(dpi), str(pdf), str(prefix)], check=True)
    raw = sorted(out_dir.glob("page-*.png"))
    for i, old in enumerate(raw, 1):
        new = out_dir / f"page-{i:03d}.png"
        if old != new:
            old.rename(new)
        pages.append(new)
    return pages


def render_image(src: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    p = out_dir / "page-001.png"
    im.save(p)
    return [p]


def make_contact(paths: list[Path], out: Path, cols: int = 4, thumb_w: int = 360,
                 label_prefix: str = "P") -> None:
    if not paths:
        return
    cards = []
    for i, p in enumerate(paths, 1):
        im = Image.open(p).convert("RGB")
        ratio = thumb_w / im.width
        thumb = im.resize((thumb_w, max(1, int(im.height * ratio))))
        label_h = 28
        card = Image.new("RGB", (thumb_w, thumb.height + label_h), "white")
        card.paste(thumb, (0, label_h))
        d = ImageDraw.Draw(card)
        d.text((6, 6), f"{label_prefix}{i}", fill="black")
        cards.append(card)
    card_w = max(c.width for c in cards)
    card_h = max(c.height for c in cards)
    rows = math.ceil(len(cards) / cols)
    sheet = Image.new("RGB", (cols * card_w, rows * card_h), "white")
    for i, c in enumerate(cards):
        sheet.paste(c, ((i % cols) * card_w, (i // cols) * card_h))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, optimize=True)


def parse_grid(value: str) -> tuple[int, int]:
    try:
        a, b = value.lower().split("x", 1)
        cols, rows = int(a), int(b)
        if cols < 1 or rows < 1:
            raise ValueError
        return cols, rows
    except Exception:
        raise argparse.ArgumentTypeError("grid must look like 2x3")


def parse_pair(value: str) -> tuple[float, float]:
    try:
        a, b = value.split(",", 1)
        a, b = float(a), float(b)
        if not (0 <= a < b <= 1):
            raise ValueError
        return a, b
    except Exception:
        raise argparse.ArgumentTypeError("range must look like 0.09,0.92 and stay within 0..1")


def make_grid_band_contact(paths: list[Path], out: Path, grid: tuple[int, int],
                           x_range: tuple[float, float], y_range: tuple[float, float],
                           band_px: int, cols: int = 4) -> None:
    gc, gr = grid
    crops = []
    for page_index, p in enumerate(paths, 1):
        im = Image.open(p).convert("RGB")
        w, h = im.size
        xl, xr = int(w * x_range[0]), int(w * x_range[1])
        yt, yb = int(h * y_range[0]), int(h * y_range[1])
        x_edges = [round(xl + (xr-xl)*i/gc) for i in range(gc+1)]
        y_edges = [round(yt + (yb-yt)*i/gr) for i in range(gr+1)]
        for r in range(gr):
            for c in range(gc):
                crop = im.crop((x_edges[c], y_edges[r], x_edges[c+1], min(y_edges[r] + band_px, h)))
                crop.thumbnail((420, 150))
                canvas = Image.new("RGB", (430, 175), "white")
                canvas.paste(crop, (5, 20))
                d = ImageDraw.Draw(canvas)
                d.text((5, 3), f"P{page_index} C{c+1}R{r+1}", fill="black")
                crops.append(canvas)
    rows = math.ceil(len(crops) / cols)
    sheet = Image.new("RGB", (cols*430, rows*175), "white")
    for i, crop in enumerate(crops):
        sheet.paste(crop, ((i % cols)*430, (i // cols)*175))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True, help="Evidence PDF/image. Repeat for multiple inputs.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=120)
    ap.add_argument("--contact-cols", type=int, default=4)
    ap.add_argument("--packet-pages", type=int, default=0, help="When known, create one contact sheet per consecutive packet.")
    ap.add_argument("--grid-band", type=parse_grid, help="Optional repeated cell grid, e.g. 2x3.")
    ap.add_argument("--grid-x", type=parse_pair, default=(0.0, 1.0))
    ap.add_argument("--grid-y", type=parse_pair, default=(0.0, 1.0))
    ap.add_argument("--band-px", type=int, default=150)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"version": VERSION, "sources": [], "total_pages": 0, "packet_pages": args.packet_pages or None}
    global_pages: list[Path] = []

    for src_index, raw in enumerate(args.input, 1):
        src = Path(raw)
        if not src.exists():
            raise SystemExit(f"Evidence file not found: {src}")
        page_dir = out / "pages" / f"source-{src_index:02d}"
        if src.suffix.lower() == ".pdf":
            pages = render_pdf(src, page_dir, args.dpi)
        else:
            pages = render_image(src, page_dir)
        global_pages.extend(pages)
        manifest["sources"].append({
            "path": str(src), "pages": len(pages),
            "rendered": [str(p.relative_to(out)) for p in pages]
        })

    manifest["total_pages"] = len(global_pages)
    make_contact(global_pages, out / "contact_all.png", args.contact_cols, label_prefix="P")

    if args.packet_pages:
        packets = []
        for i in range(0, len(global_pages), args.packet_pages):
            packet = global_pages[i:i+args.packet_pages]
            n = i // args.packet_pages + 1
            p = out / "packets" / f"packet-{n:02d}.png"
            make_contact(packet, p, min(args.contact_cols, max(1, len(packet))), label_prefix=f"S{n}-P")
            packets.append({"packet": n, "page_start": i+1, "page_end": i+len(packet), "contact": str(p.relative_to(out))})
        manifest["packets"] = packets

    if args.grid_band:
        if args.packet_pages:
            band_outputs=[]
            for i in range(0, len(global_pages), args.packet_pages):
                packet = global_pages[i:i+args.packet_pages]
                n = i // args.packet_pages + 1
                p = out / "grid_bands" / f"packet-{n:02d}.png"
                make_grid_band_contact(packet, p, args.grid_band, args.grid_x, args.grid_y, args.band_px, args.contact_cols)
                band_outputs.append(str(p.relative_to(out)))
            manifest["grid_band_contacts"] = band_outputs
        else:
            p = out / "grid_bands" / "all.png"
            make_grid_band_contact(global_pages, p, args.grid_band, args.grid_x, args.grid_y, args.band_px, args.contact_cols)
            manifest["grid_band_contacts"] = [str(p.relative_to(out))]

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status":"PASS", "version":VERSION, "pages":len(global_pages), "out":str(out)}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

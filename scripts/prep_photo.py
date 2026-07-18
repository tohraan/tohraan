#!/usr/bin/env python3
"""Prep a source photo for ASCII conversion.

Removes the background, boosts local contrast (CLAHE), and composites
onto pure white so the background maps to the blank end of the ASCII
density ramp. Run once per photo:

    python scripts/prep_photo.py source-photo.jpg
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(src_path: Path, out_path: Path) -> None:
    cutout_bytes = remove(src_path.read_bytes())
    cutout = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")

    rgb = np.array(cutout.convert("RGB"))
    alpha = np.array(cutout.split()[-1])

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    boosted = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB)

    alpha_f = (alpha.astype(np.float32) / 255.0)[..., None]
    white = np.full_like(boosted, 255)
    composited = (boosted.astype(np.float32) * alpha_f + white.astype(np.float32) * (1 - alpha_f))
    composited = composited.astype(np.uint8)

    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)
    Image.fromarray(gray, mode="L").save(out_path)
    print(f"wrote {out_path}")


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: prep_photo.py <source-photo.jpg> [output.png]", file=sys.stderr)
        sys.exit(1)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "source-prepped.png"
    prep_photo(src, out)


if __name__ == "__main__":
    main()

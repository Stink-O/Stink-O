#!/usr/bin/env python3
"""Prep a photo for ASCII conversion: remove background, boost contrast,
composite onto white so brightness maps cleanly onto the character ramp.

Usage: python scripts/prep_photo.py source-photo.png
Writes: source-prepped.png (grayscale)
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.png"
    img = Image.open(src).convert("RGBA")

    # Isolate the subject (u2netp is the small model; plenty for a portrait)
    session = new_session("u2net")
    cut = remove(img, session=session)

    # Composite onto pure white so the background washes to spaces
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, cut).convert("L")

    # CLAHE for local contrast so fur/face detail survives the ramp
    arr = np.array(flat)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    arr = clahe.apply(arr)

    # Keep the background white — CLAHE can pull it slightly grey
    mask = np.array(cut.split()[3])
    arr[mask < 120] = 255

    Image.fromarray(arr).save("source-prepped.png")
    print(f"wrote source-prepped.png ({arr.shape[1]}x{arr.shape[0]})")


if __name__ == "__main__":
    main()

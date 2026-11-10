"""Prueba del entorno: limpia la marca de la esquina de una imagen (inpainting) y genera un PDF A4.
Uso: tools/.venv/bin/python tools/prueba.py [imagen] [salida_dir]"""
import sys
from pathlib import Path
import cv2, numpy as np, pymupdf as fitz

src = Path(sys.argv[1] if len(sys.argv) > 1 else "_originales/img/carrusel-zash.jpg")
out = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/claude-1000/prueba"); out.mkdir(parents=True, exist_ok=True)

img = cv2.imread(str(src)); h, w = img.shape[:2]
# Máscara de la esquina inferior derecha donde Gemini pone ✦
mask = np.zeros((h, w), np.uint8)
mask[int(h*.93):, int(w*.93):] = 255
limpia = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)
png = out / "limpia.jpg"; cv2.imwrite(str(png), limpia, [cv2.IMWRITE_JPEG_QUALITY, 90])

doc = fitz.open(); page = doc.new_page(width=595.28, height=841.89)  # A4 en puntos
page.insert_image(fitz.Rect(40, 40, 555, 40 + 515*h/w), filename=str(png))
page.insert_text((40, 800), "Prueba del entorno de tools/", fontsize=12)
doc.save(out / "prueba.pdf")
print("OK:", png, out / "prueba.pdf")

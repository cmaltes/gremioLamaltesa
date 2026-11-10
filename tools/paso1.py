"""Paso 1: quita la marca ✦, sube la resolución ×2, unifica el color de las escenas y escribe JPG + miniatura.
Uso: tools/.venv/bin/python tools/paso1.py <carpeta_media_del_docx> <salida>
Requiere tools/bin/realesrgan-ncnn-vulkan (con su carpeta models/)."""
import sys, subprocess, tempfile
from pathlib import Path
import cv2, numpy as np
sys.path.insert(0, str(Path(__file__).parent)); import marca

MEDIA, SAL = Path(sys.argv[1]), Path(sys.argv[2])
RE = Path(__file__).parent / "bin" / "realesrgan-ncnn-vulkan"
ESCENAS = {1: "tienda-mizzen", 2: "diana-glitch", 3: "carrusel-zash", 4: "noria-gart"}
MAPAS = {5: "feria", 6: "cueva-oso-lechuza", 7: "feria-variante", 8: "encrucijada", 9: "bosque-emboscada"}
FUERZA_COLOR = 0.6

def subir(im, modelo):
    """×4 con Real-ESRGAN y vuelta a ×2 con interpolación de área."""
    with tempfile.TemporaryDirectory() as t:
        a, b = Path(t, "a.png"), Path(t, "b.png"); cv2.imwrite(str(a), im)
        subprocess.run([str(RE), "-i", str(a), "-o", str(b), "-n", modelo, "-s", "4", "-t", "200"], check=True, capture_output=True)
        g = cv2.imread(str(b))
    h, w = im.shape[:2]
    return cv2.resize(g, (w*2, h*2), interpolation=cv2.INTER_AREA)

def guardar(im, nombre, carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(carpeta / f"{nombre}.jpg"), im, [cv2.IMWRITE_JPEG_QUALITY, 85, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])
    h, w = im.shape[:2]; f = 640 / max(h, w)
    cv2.imwrite(str(carpeta / f"{nombre}-min.jpg"), cv2.resize(im, (round(w*f), round(h*f)), interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 82, cv2.IMWRITE_JPEG_PROGRESSIVE, 1])
    print(nombre, im.shape[1], "x", im.shape[0], (carpeta / f"{nombre}.jpg").stat().st_size // 1024, "KB", flush=True)

orig = {i: cv2.imread(str(MEDIA / f"image{i}.png")) for i in range(1, 10)}
tpl = marca.plantilla([orig[i] for i in ESCENAS])

# Escenas: sin marca, ×2 y color común
limpias = {i: subir(marca.quitar(orig[i], tpl), "realesrgan-x4plus") for i in ESCENAS}
labs = {i: cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32) for i, im in limpias.items()}
mu = np.mean([l.reshape(-1, 3).mean(0) for l in labs.values()], 0)
sd = np.mean([l.reshape(-1, 3).std(0) for l in labs.values()], 0)
for i, l in labs.items():
    m, s = l.reshape(-1, 3).mean(0), l.reshape(-1, 3).std(0)
    obj = (l - m) / s * sd + mu
    out = l * (1 - FUERZA_COLOR) + obj * FUERZA_COLOR
    out = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    guardar(out, ESCENAS[i], SAL / "img")

# Mapas: sin marca y ×2 (el de 2048 px ya es grande: solo se limpia)
for i, n in MAPAS.items():
    im = marca.quitar(orig[i], tpl, mapa=True)
    if im.shape[1] < 2000: im = subir(im, "realesrgan-x4plus-anime")
    guardar(im, n, SAL / "mapas")

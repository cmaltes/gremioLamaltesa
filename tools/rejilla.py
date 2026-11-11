"""Paso 5: mide la cuadrícula dibujada por la IA en un mapa (líneas finas oscuras largas).
Uso: tools/.venv/bin/python tools/rejilla.py <mapa.jpg> [--guardar salida.png]"""
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d

def lineas(g, eje):
    """posiciones (px) de las líneas a lo largo del eje 'x' (verticales) o 'y' (horizontales)."""
    a = g if eje == "x" else g.T                       # a[fila, col]; buscamos columnas
    vec = (a[:, 4:-4] < (a[:, :-8] + a[:, 8:]) / 2 - 18)  # más oscuro que ±4 px a los lados
    vec = np.pad(vec, ((0, 0), (4, 4)))
    # solo cuenta si la oscura se mantiene en vertical: filtro de rachas largas
    larga = uniform_filter1d(vec.astype(float), 41, axis=0) > .8
    perfil = larga.sum(0).astype(float)
    return perfil

def picos(perfil, minimo):
    n = len(perfil); out = []
    for i in range(n):
        if perfil[i] >= minimo and perfil[i] == perfil[max(0, i - 8): i + 9].max():
            out.append(i)
    return out

if __name__ == "__main__":
    g = np.array(Image.open(sys.argv[1]).convert("L"), float)
    for eje in ("x", "y"):
        p = lineas(g, eje); L = g.shape[0 if eje == "x" else 1]
        pk = picos(p, L * .12)
        d = np.diff(pk)
        print(eje, len(pk), "líneas; paso mediano", np.median(d) if len(d) else None, "mín/máx", (d.min(), d.max()) if len(d) else None)
        print("  ", pk)


def modelo(pk, p0):
    """ajusta pos = a + k*paso a las líneas que cuadran con el paso aproximado p0; devuelve (a, paso, inliers)."""
    pk = np.array(pk, float); a0 = pk[0]
    for _ in range(4):
        k = np.round((pk - a0) / p0); res = pk - (a0 + k * p0)
        ok = np.abs(res) < p0 * .12
        A = np.vstack([np.ones(ok.sum()), k[ok]]).T
        a0, p0 = np.linalg.lstsq(A, pk[ok], rcond=None)[0]
    return a0, p0, int(ok.sum())

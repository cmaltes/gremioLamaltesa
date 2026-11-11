"""Paso 5: conserva la cuadrícula dibujada por la IA y corrige solo lo que está mal.
 1. Detecta las líneas finas largas de cada eje y las ordena en una rejilla ideal (casilla = paso mediano).
 2. Líneas sobrantes (a media casilla, dobles…) → se borran con inpainting.
 3. Pasos irregulares (80…93 px) → se deforma la imagen por tramos para que cada línea caiga en su sitio (casillas todas iguales).
 4. Líneas que faltan (o todas, si se pasa una imagen base repintada sin rejilla) → se dibujan con el mismo estilo.
Uso como módulo: procesar(ruta_mapa, base=None) → (imagen RGB con casillas cuadradas, columnas, filas, px_por_casilla, informe)"""
import sys, os
import numpy as np, cv2
from PIL import Image
from scipy.ndimage import uniform_filter1d, binary_dilation
sys.path.insert(0, os.path.dirname(__file__))
from rejilla import picos

def perfil_eje(g, eje):
    a = g if eje == "x" else g.T
    vec = np.pad(a[:, 6:-6] < (a[:, :-12] + a[:, 12:]) / 2 - 12, ((0, 0), (6, 6)))
    larga = uniform_filter1d(vec.astype(float), 25, axis=0) > .7
    return a, vec | larga, larga.sum(0).astype(float)

def ordenar(pk, perfil, p0):
    """lista de (posición, k) de líneas válidas + lista de posiciones sobrantes. k = índice en la rejilla ideal."""
    # fusiona picos pegados (a menos de 8 px) quedándose con el más fuerte
    fus = []
    for c in pk:
        if fus and c - fus[-1] < 8:
            if perfil[c] > perfil[fus[-1]]: fus[-1] = c
        else: fus.append(c)
    gaps = np.diff(fus); p = float(np.median(gaps[(gaps > .8 * p0) & (gaps < 1.2 * p0)])) if len(gaps) else p0
    ok = [(fus[0], 0)]; extra = []
    for i, c in enumerate(fus[1:], 1):
        g = c - ok[-1][0]; nk = int(round(g / p))
        encaja = nk >= 1 and abs(g - nk * p) <= .22 * p * max(1, nk ** .5)
        # si la rejilla «salta de fase» (todas las líneas siguientes quedan desplazadas), se acepta la línea si la siguiente encaja con ella
        sigue = i + 1 < len(fus) and abs((fus[i + 1] - c) - p) <= .12 * p
        if nk >= 1 and (encaja or sigue): ok.append((c, ok[-1][1] + nk))
        else: extra.append(c)
    return ok, extra, p

def eje(g, nombre, p0):
    a, mask, perfil = perfil_eje(g, nombre)
    pk = picos(perfil, a.shape[0] * .30)
    ok, extra, p = ordenar(pk, perfil, p0)
    cm = np.zeros(a.shape[1], bool)
    for c in extra: cm[max(0, c - 3): c + 4] = True
    m = binary_dilation(mask & cm[None, :], np.ones((1, 3)))
    return ok, extra, p, (m if nombre == "x" else m.T)

def anclas(ok, N, p, P):
    """anclas (origen, destino) para deformar un eje; devuelve (src, dst, n_celdas, k_inicio, virtuales, k_total)."""
    k0, k1 = ok[0][1], ok[-1][1]
    kk = np.arange(k0, k1 + 1); pos = np.interp(kk, [k for _, k in ok], [c for c, _ in ok])
    ks, ke = k0, k1
    if ok[0][0] > .65 * p: ks -= 1; pos = np.r_[pos[0] - p, pos]; kk = np.r_[ks, kk]       # la 1.ª casilla está al menos medio llena: se completa
    if N - ok[-1][0] > .65 * p: ke += 1; pos = np.r_[pos, pos[-1] + p]; kk = np.r_[kk, ke]
    dst = (kk - ks) * P
    return pos, dst, ke - ks, kk, {k for k in kk if k not in {k for _, k in ok}}

def procesar(ruta, base=None, p0=84):
    im = np.array(Image.open(ruta).convert("RGB")); g = im.mean(2); H, W = g.shape
    okx, exx, px, mx = eje(g, "x", p0); oky, exy, py, my = eje(g, "y", p0)
    P = int(round((px + py) / 2))
    sx, dx, nc, kx, vx = anclas(okx, W, px, P); sy, dy, nr, ky, vy = anclas(oky, H, py, P)
    # imagen a deformar: la original sin las líneas sobrantes, o la base repintada (sin rejilla)
    if base is None:
        m = ((mx | my) * 255).astype(np.uint8)
        img = cv2.inpaint(im, m, 3, cv2.INPAINT_TELEA) if m.any() else im
    else:
        img = np.array(Image.open(base).convert("RGB").resize((W, H), Image.LANCZOS))
    pad = int(2 * max(px, py)); imp = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REFLECT)
    xs = np.interp(np.arange(nc * P), dx, sx) + pad; ys = np.interp(np.arange(nr * P), dy, sy) + pad
    out = cv2.remap(imp, np.broadcast_to(xs[None, :], (nr * P, nc * P)).astype(np.float32), np.broadcast_to(ys[:, None], (nr * P, nc * P)).astype(np.float32), cv2.INTER_CUBIC)
    # líneas que faltan (o todas con base repintada) con el estilo de las de la IA
    lin = np.zeros(out.shape[:2], np.float32); w = max(2, round(P * .02))
    for i, k in enumerate(kx):
        if base is not None or k in vx: lin[:, max(0, i * P - w // 2): i * P + w // 2 + 1] = 1
    for i, k in enumerate(ky):
        if base is not None or k in vy: lin[max(0, i * P - w // 2): i * P + w // 2 + 1, :] = 1
    lin = cv2.GaussianBlur(lin, (0, 0), .7)[..., None] * (.7 if base is not None else .85)
    out = (out * (1 - lin) + np.array([28, 28, 28], np.float32) * lin).astype(np.uint8)
    info = dict(p_x=round(px, 1), p_y=round(py, 1), P=P, lineas_x=len(okx), lineas_y=len(oky), sobrantes_x=exx, sobrantes_y=exy,
                faltan_x=sorted(int(k) for k in vx), faltan_y=sorted(int(k) for k in vy),
                paso_min_max_x=(int(np.diff([c for c, _ in okx]).min()), int(np.diff([c for c, _ in okx]).max())),
                paso_min_max_y=(int(np.diff([c for c, _ in oky]).min()), int(np.diff([c for c, _ in oky]).max())))
    return Image.fromarray(out), nc, nr, P, info

if __name__ == "__main__":
    img, nc, nr, P, info = procesar(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None, float(sys.argv[4]) if len(sys.argv) > 4 else 84)
    img.save(sys.argv[2]); print(nc, "x", nr, "casillas;", P, "px/casilla;", info)

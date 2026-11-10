"""Quita la marca ✦ de Gemini (esquina inferior derecha) por inpainting."""
import cv2, numpy as np

BOX = 110  # lado de la región de búsqueda desde la esquina

def _hp(im):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    return g - cv2.GaussianBlur(g, (0, 0), 12)

def plantilla(imagenes_oscuras):
    """Forma de la estrella, promediada de imágenes oscuras donde se ve limpia."""
    acc = None
    for im in imagenes_oscuras:
        h, w = im.shape[:2]
        reg = _hp(im)[h-BOX-20:h-20, w-BOX-20:w-20]
        acc = reg if acc is None else acc + reg
    acc /= len(imagenes_oscuras)
    t = (acc > 0.35 * acc.max()).astype(np.uint8)  # 1 = estrella
    ys, xs = np.nonzero(t)
    return np.ascontiguousarray(t[ys.min():ys.max()+1, xs.min():xs.max()+1])

def mascara(im, tpl, dilatar=8):
    h, w = im.shape[:2]
    escala = 2 if w >= 2000 else 1   # en 2048 px la marca mide el doble
    tp = cv2.resize(tpl, None, fx=escala, fy=escala, interpolation=cv2.INTER_NEAREST) if escala > 1 else tpl
    S = 2 * BOX if escala > 1 else BOX
    y_ini, x_ini = h - S - 40, w - S - 40
    reg = np.ascontiguousarray(_hp(im)[y_ini:, x_ini:], dtype=np.float32)
    t = np.ascontiguousarray(tp.astype(np.float32))
    r = cv2.matchTemplate(reg, t, cv2.TM_CCOEFF_NORMED)
    _, mx, _, (x, y) = cv2.minMaxLoc(r)
    m = np.zeros(im.shape[:2], np.uint8)
    y0, x0 = y_ini + y, x_ini + x
    m[y0:y0+tp.shape[0], x0:x0+tp.shape[1]] = tp * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*dilatar*escala+1,)*2)
    return cv2.dilate(m, k)

ALFA = 0.5  # opacidad medida de la marca (blanco)

def _desmezclar(im, m, alfa):
    f = im.astype(np.float32)
    o = np.clip((f - alfa * 255) / (1 - alfa), 0, 255)
    out = f.copy(); out[m] = o[m]
    return out.astype(np.uint8)

def quitar(im, tpl, mapa=False):
    """Quita la marca. La posición es fija (-80 px de la esquina; -160 en 2048).
    - Ilustraciones (fondo oscuro y liso): se deshace la mezcla (a≈0,5) y se repara el borde.
    - Mapas (fondo con mucha textura, opacidad variable): inpainting con la estrella dilatada."""
    m = mascara(im, tpl, dilatar=0) > 0
    esc = 2 if im.shape[1] >= 2000 else 1
    mu = m.astype(np.uint8)
    if mapa:
        # afina la posición (±4 px): la estrella es más clara que su entorno inmediato
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
        er = np.ones((5*esc, 5*esc), np.uint8); an = np.ones((11*esc, 11*esc), np.uint8)
        mejor = None
        for dy in range(-4*esc, 4*esc+1):
            for dx in range(-4*esc, 4*esc+1):
                s_ = np.roll(np.roll(mu, dy, 0), dx, 1)
                dentro = cv2.erode(s_, er) > 0
                fuera = (cv2.dilate(s_, an) - cv2.dilate(s_, np.ones((5*esc, 5*esc), np.uint8))) > 0
                sc = g[dentro].mean() - g[fuera].mean()
                if mejor is None or sc > mejor[0]: mejor = (sc, s_)
        mu = mejor[1]
        grande = cv2.dilate(mu, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*5*esc+1,)*2))
        return cv2.inpaint(im, grande * 255, 4 * esc, cv2.INPAINT_TELEA)
    k = np.ones((2*3*esc+1,)*2, np.uint8)
    anillo = cv2.dilate(mu, k) - cv2.erode(mu, k)
    return cv2.inpaint(_desmezclar(im, m, ALFA), anillo * 255, 3, cv2.INPAINT_TELEA)

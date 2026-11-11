"""Música de fondo en bucle, sintetizada con numpy (sin modelos ni descargas).

Uso: tools/.venv/bin/python tools/musica_ambiente.py [1|2|3|todas]

Cada pista dura exactamente 10 minutos y es CIRCULAR: las notas se suman con
"wrap" al principio, los ruidos son periódicos (se generan en el dominio de la
frecuencia) y la reverb es una convolución circular. Por eso el bucle no tiene
corte audible. Salida: public/aventuras/la-feria-del-misterio/musica/fondo-capitulo-N.mp3
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import fft as sfft
from scipy.io import wavfile

SR = 32000
T = 600  # segundos
N = SR * T
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "public/aventuras/la-feria-del-misterio/musica"
TMP = Path("/tmp/claude-1000/-home-fernando-Desarrollo-gremioLamaltesa/cf4d94b4-a2d7-4765-846f-dff2327d975f/scratchpad")
TMP.mkdir(parents=True, exist_ok=True)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def ciclos(f):
    """Ajusta f a un número entero de ciclos en T (para que sea periódico)."""
    return max(1, round(f * T)) / T


class Bus:
    def __init__(self):
        self.l = np.zeros(N, np.float32)
        self.r = np.zeros(N, np.float32)

    def add(self, t0, sig, vol=1.0, pan=0.0):
        """Suma sig empezando en t0 s, con wrap circular."""
        i = int(t0 * SR) % N
        n = len(sig)
        gl = vol * np.cos((pan + 1) * np.pi / 4)
        gr = vol * np.sin((pan + 1) * np.pi / 4)
        sig = sig.astype(np.float32)
        while n > 0:
            k = min(n, N - i)
            self.l[i:i + k] += gl * sig[:k]
            self.r[i:i + k] += gr * sig[:k]
            sig = sig[k:]
            n -= k
            i = 0


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(d, a=0.01, r=0.1):
    n = int(d * SR)
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


# ---------- instrumentos ----------
def campanilla(f, d=2.5):
    t = tt(d)
    s = np.zeros_like(t)
    for r, a, k in [(1, 1, 2.0), (2.76, .5, 3.0), (5.4, .25, 4.5), (8.93, .12, 6.0)]:
        s += a * np.sin(2 * np.pi * f * r * t) * np.exp(-k * t)
    return s * 0.5


def cajita(f, d=1.6):
    t = tt(d)
    s = np.zeros_like(t)
    for r, a, k in [(1, 1, 2.2), (2.01, .35, 3.5), (4.02, .15, 6.0), (6.0, .07, 9.0)]:
        s += a * np.sin(2 * np.pi * f * r * t) * np.exp(-k * t)
    s[:40] *= np.linspace(0, 1, 40)
    return s * 0.5


def pluck(f, d=0.9, n=6, k=4.0):
    t = tt(d)
    s = np.zeros_like(t)
    for h in range(1, n + 1):
        s += np.sin(2 * np.pi * f * h * t) / h * np.exp(-(k + h * 1.2) * t)
    s[:30] *= np.linspace(0, 1, 30)
    return s * 0.6


def bajo(f, d=1.0):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) * np.exp(-3 * t)
    return s * np.exp(-2.2 * t) * env(d, 0.01, 0.05) * 0.8


def pad(f, d, a=0.8, r=1.2, arm=7, det=(0.0, 0.004, -0.004), vib=0.0):
    t = tt(d)
    s = np.zeros_like(t)
    for dt in det:
        ph = 2 * np.pi * f * (1 + dt) * t
        if vib:
            ph = ph + vib * np.sin(2 * np.pi * 5 * t)
        for h in range(1, arm + 1):
            s += np.sin(ph * h + h) / h ** 1.4
    return s * env(d, a, r) / len(det) * 0.55


def bombo(d=0.5, f0=130, f1=42):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 1.1


def tom(d=0.7, f0=170, f1=75):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 14)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    s += 0.25 * np.random.randn(len(t)) * np.exp(-t * 40)
    return s * 0.9


def gota(d=0.35):
    t = tt(d)
    f = 1100 + 900 * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * 0.45


def buho(d=0.7):
    t = tt(d)
    f = 400 - 40 * t / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.3 * np.sin(2 * ph)
    return s * np.sin(np.pi * t / d) ** 1.5 * 0.4


def corno(f, d):
    """Metal suave: saw filtrada con ataque lento."""
    return pad(f, d, a=min(0.5, d * .3), r=min(0.8, d * .4), arm=5, det=(0.0, 0.003), vib=0.4) * 1.2


# ---------- ruidos periódicos ----------
def ruido(banda, pend=0.0, seed=0):
    """Ruido estéreo periódico con forma espectral banda=(f_lo, f_hi). Devuelve (l, r) rms=1."""
    rng = np.random.default_rng(seed)
    nf = N // 2 + 1
    fr = np.arange(nf) * SR / N
    lo, hi = banda
    mag = np.where((fr >= lo) & (fr <= hi), 1.0, 0.0)
    mag = np.convolve(mag, np.ones(2001) / 2001, mode="same")  # bordes suaves
    mag = mag * (np.maximum(fr, 1) / 1000.0) ** pend
    out = []
    for _ in range(2):
        ph = rng.uniform(0, 2 * np.pi, nf)
        x = sfft.irfft(mag * np.exp(1j * ph), n=N, workers=-1)
        out.append((x / np.sqrt(np.mean(x ** 2))).astype(np.float32))
    return out


def mod_periodica(rng, f_lo, f_hi, prof=0.5, partes=4):
    """Modulación de amplitud periódica (suma de senos con ciclos enteros) en [1-prof, 1]."""
    t = np.arange(N, dtype=np.float64) / SR
    m = np.zeros(N)
    for _ in range(partes):
        f = ciclos(rng.uniform(f_lo, f_hi))
        m += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    m = m / partes * 1.6
    m = (m - m.min()) / (m.max() - m.min())
    return (1 - prof + prof * m).astype(np.float32)


def arco(k, fase=0.0):
    """Intensidad 0..1 periódica con k ciclos por pista."""
    t = np.arange(N, dtype=np.float64) / SR
    return (0.5 + 0.5 * np.cos(2 * np.pi * (k * t / T + fase))).astype(np.float32)


def arco_en(t, k, fase=0.0):
    return 0.5 + 0.5 * np.cos(2 * np.pi * (k * t / T + fase))


# ---------- reverb circular ----------
def reverb(bus, tau=2.0, mezcla=0.3, seed=1):
    rng = np.random.default_rng(seed)
    n = int(tau * 3 * SR)
    t = np.arange(n) / SR
    res = []
    for x in (bus.l, bus.r):
        ir = rng.standard_normal(n) * np.exp(-t / tau)
        # tono más oscuro con el tiempo
        from scipy.signal import lfilter
        ir = lfilter([0.25], [1, -0.75], ir)
        ir[0] = 0
        X = sfft.rfft(x, workers=-1)
        IR = sfft.rfft(ir, n=N, workers=-1)
        y = sfft.irfft(X * IR, n=N, workers=-1)
        y *= np.sqrt(np.mean(x ** 2) / max(np.mean(y ** 2), 1e-12))
        res.append(((1 - mezcla) * x + mezcla * y * 1.4).astype(np.float32))
    bus.l, bus.r = res


def exportar(bus, nombre, pico=0.85):
    st = np.stack([bus.l, bus.r], 1)
    st = np.tanh(st * 1.1) if np.max(np.abs(st)) > 1 else st
    st = st / np.max(np.abs(st)) * pico
    wav = TMP / f"{nombre}.wav"
    wavfile.write(wav, SR, (st * 32767).astype(np.int16))
    mp3 = SALIDA / f"{nombre}.mp3"
    SALIDA.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "96k", "-ar", "32000", str(mp3)], check=True)
    wav.unlink()
    print("OK", mp3, f"{mp3.stat().st_size / 1e6:.1f} MB")


def poner_ruido(bus, banda, vol, mod=None, pend=0.0, seed=0, mono=False):
    l, r = ruido(banda, pend, seed)
    if mod is not None:
        l, r = l * mod, r * mod
    bus.l += vol * l
    bus.r += vol * (l if mono else r)


# ---------- instrumentos y efectos nuevos ----------
def calliope(f, d):
    t = tt(d)
    ph = 2 * np.pi * f * t + 0.004 * np.sin(2 * np.pi * 5.5 * t)
    s = sum(np.sin(ph * h) / h for h in (1, 3, 5, 7, 9))
    s += 0.35 * np.sin(2 * np.pi * f * 2 * t)
    e = env(d, 0.006, min(0.06, d * .3)) * (0.75 + 0.25 * np.exp(-t * 8))
    return s * e * 0.35


def acordeon(f, d):
    t = tt(d)
    s = np.zeros_like(t)
    for dt in (0, 0.006):
        ph = 2 * np.pi * f * (1 + dt) * t
        s += sum(np.sin(ph * h) / h ** 1.1 for h in range(1, 7))
    return s * env(d, 0.02, min(0.08, d * .4)) * (0.85 + 0.15 * np.sin(2 * np.pi * 6 * t)) * 0.22


def tablilla(d=0.08, f=950):
    t = tt(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 70) * 0.7


def caja(d=0.14):
    from scipy.signal import butter, sosfilt
    r = np.random.randn(int(d * SR))
    r = sosfilt(butter(2, 1800, "hp", fs=SR, output="sos"), r)
    return (r * np.exp(-np.arange(len(r)) / SR * 30) + 0.5 * tablilla(d, 190)[:len(r)]) * 0.35


def risa(f0=330, n=5, gap=0.17):
    """Risa sintetizada: 'ja-ja-ja' con formantes de la 'a'."""
    d = n * gap + 0.25
    out = np.zeros(int(d * SR))
    for k in range(n):
        dur = 0.14
        tl = tt(dur)
        f = f0 * (1 - 0.035 * k) * (1 + 0.12 * (1 - tl / dur))
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = np.zeros_like(tl)
        for h in range(1, 20):
            fh = h * f0
            if fh > 4200:
                break
            w = np.exp(-((fh - 800) / 260) ** 2) + 0.55 * np.exp(-((fh - 1300) / 300) ** 2) + 0.08
            s += w * np.sin(h * ph) / h ** 0.5
        s *= np.sin(np.pi * tl / dur) ** 1.2 * (1 - 0.1 * k)
        i = int(k * gap * SR)
        out[i:i + len(s)] += s
    return out * 0.16


def silbato(f0=600, f1=1900, d=0.55):
    t = tt(d)
    f = f0 + (f1 - f0) * (t / d) ** 1.3
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + 0.12 * np.sin(2 * ph)) * np.sin(np.pi * t / d) ** 0.7 * 0.3


def ruleta(f_ding):
    """Rueda de la fortuna: clicks que se frenan y un ding final."""
    ts, t, gap = [], 0.0, 0.05
    while t < 2.0:
        ts.append(t)
        t += gap
        gap *= 1.17
    out = np.zeros(int((t + 2.5) * SR))
    for x in ts:
        c = tablilla(0.03, 2200) * 0.6
        i = int(x * SR)
        out[i:i + len(c)] += c
    dg = campanilla(f_ding, 2.2) * 1.6
    i = int(t * SR)
    out[i:i + len(dg)] += dg
    return out


def ping(d=0.5):
    t = tt(d)
    f = 2600 - 900 * (t / d) ** 0.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.35


def globo(d=0.12):
    t = tt(d)
    r = np.random.randn(len(t)) * np.exp(-t * 90) * 0.5
    return r + np.sin(2 * np.pi * 240 * t) * np.exp(-t * 40) * 0.6


def trompeta(f, d):
    return pad(f, d, a=0.02, r=min(0.15, d * .4), arm=9, det=(0.0, 0.003), vib=0.25) * 1.5


def grillo(dur=12.0, f=4300):
    out = np.zeros(int(dur * SR))
    p = tt(0.022)
    pulso = np.sin(2 * np.pi * f * p) * np.sin(np.pi * p / 0.022) ** 2 * 0.5
    t = 0.0
    while t < dur - 0.3:
        for k in range(3):
            i = int((t + k * 0.04) * SR)
            out[i:i + len(pulso)] += pulso * (0.7 + 0.3 * (k == 1))
        t += np.random.uniform(0.5, 0.62)
    return out


def rana():
    out = np.zeros(int(0.7 * SR))
    for k in range(np.random.randint(2, 4)):
        d = 0.13
        t = tt(d)
        f = np.random.uniform(150, 230)
        s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.3 * np.sin(6 * np.pi * f * t))
        s *= (0.5 + 0.5 * np.sin(2 * np.pi * 70 * t)) * np.sin(np.pi * t / d)
        i = int(k * 0.2 * SR)
        out[i:i + len(s)] += s
    return out * 0.3


def pajaro():
    n = np.random.randint(3, 7)
    base = np.random.uniform(2300, 3800)
    out = np.zeros(int(n * 0.14 * SR) + 3000)
    for k in range(n):
        d = np.random.uniform(.06, .1)
        t = tt(d)
        f = base * (1 + np.random.uniform(-.2, .3)) * (1 + 0.35 * (t / d) * np.random.choice([-1, 1]))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)
        i = int(k * 0.13 * SR)
        out[i:i + len(s)] += s
    return out * 0.2


def cuco():
    out = np.zeros(int(2.4 * SR))
    for k in range(np.random.randint(2, 4)):
        for j, f in enumerate((784, 622)):
            d = 0.22 if j else 0.18
            t = tt(d)
            s = (np.sin(2 * np.pi * f * t) + 0.15 * np.sin(4 * np.pi * f * t)) * np.sin(np.pi * t / d) ** 0.6
            i = int((k * 0.75 + j * 0.24) * SR)
            out[i:i + len(s)] += s
    return out * 0.22


def buho_ul(f=380, d=0.9):
    """Búho 'u-hu... huuu'."""
    out = np.zeros(int((d + 1.5) * SR))
    for ini, dur, ff in [(0, 0.16, f * 0.9), (0.28, 0.2, f), (0.9, 0.7, f * 0.93)]:
        t = tt(dur)
        fr = ff * (1 - 0.06 * t / dur)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        s = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.sin(np.pi * t / dur) ** 1.3
        i = int(ini * SR)
        out[i:i + len(s)] += s
    return out * 0.45


def flauta(f, d):
    t = tt(d)
    ph = 2 * np.pi * f * t + 0.006 * np.sin(2 * np.pi * 5 * t) * np.minimum(1, t * 2)
    s = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    return s * env(d, min(0.25, d * .3), min(0.6, d * .5)) * 0.3


def timbal(d=0.9, f0=110, f1=48):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 12)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    return s * 1.2


def caja_fuerte(d=0.25):
    from scipy.signal import butter, sosfilt
    r = np.random.randn(int(d * SR))
    r = sosfilt(butter(2, 1200, "hp", fs=SR, output="sos"), r)
    return r * np.exp(-np.arange(len(r)) / SR * 16) * 0.55 + 0.4 * tablilla(d, 200)[:len(r)]


def impacto():
    t = tt(2.5)
    b = np.sin(2 * np.pi * (38 + 60 * np.exp(-t * 6)) * t) * np.exp(-t * 2.2)
    r = np.random.randn(len(t)) * np.exp(-t * 6) * 0.35
    return (b + r) * 1.0


def rugido(d=1.8):
    t = tt(d)
    f = 75 + 25 * np.sin(np.pi * t / d) + 6 * np.sin(2 * np.pi * 9 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(ph * h) / h ** 0.8 for h in range(1, 12))
    s *= (0.65 + 0.35 * np.sin(2 * np.pi * 28 * t)) * np.sin(np.pi * t / d) ** 0.8
    return s * 0.28


def tremolo(f, d):
    t = tt(d)
    return pad(f, d, a=0.5, r=0.8, arm=5, det=(0, .006, -.006)) * (0.55 + 0.45 * np.sin(2 * np.pi * 8.5 * t))


def subida(d=6.0):
    from scipy.signal import butter, sosfilt
    r = np.random.randn(int(d * SR))
    r = sosfilt(butter(2, 2500, "hp", fs=SR, output="sos"), r)
    return r * (np.linspace(0, 1, len(r)) ** 2.2) * 0.35


def melodia_gen(rng, acordes_barra, escala, tonos, idx0, final):
    """Melodía por compases (2/4 = 4 corcheas). Devuelve [(corchea_inicio, indice_escala, duracion_corcheas)]."""
    pats = [(1, 1, 1, 1), (2, 1, 1), (1, 1, 2), (2, 2), (3, 1), (1, 2, 1)]
    notas, idx, direc = [], idx0, 1
    for b, ac in enumerate(acordes_barra):
        ultimo = b == len(acordes_barra) - 1
        pat = (4,) if (ultimo and final) else pats[int(rng.integers(0, len(pats)))]
        pos = 0
        for j, dur in enumerate(pat):
            fuerte = j == 0
            if fuerte or (ultimo and final):
                cand = [i for i, n in enumerate(escala) if n % 12 in tonos[ac]]
                if ultimo and final:
                    cand = [i for i, n in enumerate(escala) if n % 12 == tonos[ac][0] % 12 or n % 12 == tonos[ac][0]]
                idx = min(cand, key=lambda i: abs(i - idx) + rng.random())
            else:
                if rng.random() < 0.25:
                    direc *= -1
                idx = int(np.clip(idx + direc, 0, len(escala) - 1))
            notas.append((b * 4 + pos, idx, dur))
            pos += dur
    return notas


# ============ Capítulo 1: la feria ============
def cap1():
    rng = np.random.default_rng(11)
    np.random.seed(11)
    beat = 60 / 128  # polka a 128 bpm (2/4)
    bar = 2 * beat
    nbars = int(round(T / bar))  # 640
    ocho = beat / 2
    bus = Bus()
    D, G, A, Bm = "D", "G", "A", "Bm"
    tonos = {D: [62 % 12, 66 % 12, 69 % 12], G: [67 % 12, 71 % 12, 62 % 12], A: [69 % 12, 73 % 12, 64 % 12], Bm: [71 % 12, 62 % 12, 66 % 12]}
    tonos = {k: [x for x in v] for k, v in tonos.items()}
    raiz = {D: 38, G: 43, A: 45, Bm: 47}
    triada = {D: [62, 66, 69], G: [62, 67, 71], A: [61, 64, 69], Bm: [62, 66, 71]}
    secA = [D, D, A, A, D, D, A, D]
    secB = [G, G, D, Bm, A, A, D, D]
    escala = [n for o in (60, 72, 84) for n in (o + 2, o + 4, o + 6, o + 7, o + 9, o + 11, o + 13)]  # D mayor
    escala = [n + 0 for n in escala if 66 <= n <= 90]
    escala.sort()
    tonos_n = {k: [n % 12 for n in v] for k, v in {D: [62, 66, 69], G: [67, 71, 74], A: [69, 73, 76], Bm: [71, 74, 78]}.items()}
    # 4 melodías de 16 compases (A, B) que se alternan
    tunes = []
    for s in range(4):
        r = np.random.default_rng(100 + s)
        a1 = melodia_gen(r, secA[:4], escala, tonos_n, len(escala) // 2, False)
        a2 = melodia_gen(r, secA[4:], escala, tonos_n, len(escala) // 2, True)
        b1 = melodia_gen(r, secB[:4], escala, tonos_n, len(escala) // 2 + 1, False)
        b2 = melodia_gen(r, secB[4:], escala, tonos_n, len(escala) // 2, True)
        tunes.append((a1 + [(x + 16, i, d) for x, i, d in a2] + [(x + 32, i, d) for x, i, d in b1] + [(x + 48, i, d) for x, i, d in b2]))
    orden = [0, 0, 1, 1, 2, 2, 3, 3, 0, 2]  # nbars/16 = 40 bloques
    acordes16 = secA + secB
    inten = lambda t: float(arco_en(t, 5))
    for blk in range(nbars // 16):
        tune = tunes[orden[blk % len(orden)]]
        t_blk = blk * 16 * bar
        i_blk = inten(t_blk + 8 * bar)
        # melodía: calliope + campanilla
        for e0, idx, dur in tune:
            tn = t_blk + e0 * ocho
            f = hz(escala[idx])
            bus.add(tn, calliope(f, dur * ocho * 0.92), 0.2, -0.15)
            if i_blk > 0.45:
                bus.add(tn, campanilla(f * 2, 1.2) * 0.5, 0.12, 0.5)
        # acompañamiento
        for b in range(16):
            t0 = t_blk + b * bar
            ac = acordes16[b]
            i = inten(t0)
            bus.add(t0, bajo(hz(raiz[ac]), 0.35) * 1.3, 0.55, -0.3)  # "oom"
            for n in triada[ac]:  # "pah" a contratiempo
                bus.add(t0 + beat, acordeon(hz(n), beat * 0.8), 0.17, rng.uniform(-.5, .5))
            if i > 0.35:
                bus.add(t0 + beat, caja(), 0.35, 0.2)
            if i > 0.55:
                bus.add(t0 + ocho, tablilla(), 0.18, 0.4)
                bus.add(t0 + 1.5 * beat, tablilla(0.08, 1250), 0.15, -0.4)
            if i > 0.75 and b % 2 == 0:
                bus.add(t0, campanilla(hz(triada[ac][0] + 36), 1.5), 0.1, rng.uniform(-.7, .7))
    # efectos de la feria, repartidos al azar
    dmay = [86, 90, 93, 98, 102]
    for _ in range(70):
        bus.add(rng.uniform(0, T), campanilla(hz(rng.choice(dmay)), 2.2), 0.14, rng.uniform(-.9, .9))
    for _ in range(40):
        pit = rng.uniform(260, 460)
        bus.add(rng.uniform(0, T), risa(pit, int(rng.integers(4, 8))), 0.9, rng.uniform(-.9, .9))
    for _ in range(26):
        bus.add(rng.uniform(0, T), silbato(rng.uniform(500, 800), rng.uniform(1500, 2300)), 0.55, rng.uniform(-.9, .9))
    for _ in range(14):
        bus.add(rng.uniform(0, T), ruleta(hz(rng.choice(dmay))), 0.45, rng.uniform(-.8, .8))
    for _ in range(30):
        p = rng.uniform(-.9, .9)
        tp = rng.uniform(0, T)
        bus.add(tp, ping(), 0.6, p)
        bus.add(tp + 0.25, ping(), 0.2, p)
    for _ in range(18):
        bus.add(rng.uniform(0, T), globo(), 0.7, rng.uniform(-.9, .9))
    for _ in range(12):  # fanfarria de circo
        tf = rng.uniform(0, T)
        for j, n in enumerate([62, 66, 69, 74]):
            bus.add(tf + j * 0.16, trompeta(hz(n + 12), 0.2 if j < 3 else 0.9), 0.25, 0.0)
    reverb(bus, tau=1.4, mezcla=0.22)
    exportar(bus, "fondo-capitulo-1")


# ============ Capítulo 2: el camino y la cueva ============
def cap2():
    rng = np.random.default_rng(22)
    np.random.seed(22)
    beat = 60 / 64
    bar = 4 * beat
    nbars = int(round(T / bar))  # 160
    bus = Bus()
    t = np.arange(N, dtype=np.float64) / SR
    # zumbido grave muy suave (periódico)
    for f, a, k in [(73.42, 0.6, 2), (110.0, 0.35, 3)]:
        ff = ciclos(f)
        am = 0.6 + 0.4 * np.cos(2 * np.pi * (k * t / T + rng.random()))
        s = sum(np.sin(2 * np.pi * ciclos(ff * h) * t + h) / h ** 1.8 for h in (1, 2, 3))
        bus.l += (a * 0.06 * s * am).astype(np.float32)
        bus.r += (a * 0.06 * s * am).astype(np.float32)
    # progresión Dm - Bb - F - C (2 compases cada uno) y melodía suave
    prog = [([62, 65, 69], 38), ([58, 62, 65], 34 + 12), ([60, 65, 69], 41), ([60, 64, 67], 36)]
    penta = [62, 65, 67, 69, 72, 74, 77, 79]  # Re menor pentatónica
    idx = 3
    inten = lambda tt_: float(arco_en(tt_, 4))
    for b in range(nbars):
        t0 = b * bar
        ac, bj = prog[(b // 2) % 4]
        i = inten(t0)
        if b % 2 == 0:
            for n in ac:
                bus.add(t0, pad(hz(n), 2 * bar + 1.0, 1.2, 1.5, 4), 0.08, rng.uniform(-.6, .6))
            bus.add(t0, bajo(hz(bj), 3.0) * 0.8, 0.25, 0)
        if b % 2 == 0 and rng.random() < 0.9:
            # frase de flauta: 2-4 notas largas
            tn = t0 + rng.choice([0, 0, beat])
            for _ in range(int(rng.integers(2, 5))):
                if tn > t0 + 2 * bar - 0.5:
                    break
                cand = [k for k, n in enumerate(penta) if n % 12 in [m % 12 for m in ac]]
                if rng.random() < 0.6:
                    idx = min(cand, key=lambda k: abs(k - idx) + rng.random())
                else:
                    idx = int(np.clip(idx + rng.choice([-1, 1]), 0, len(penta) - 1))
                dur = float(rng.choice([1, 1.5, 2, 3])) * beat
                bus.add(tn, flauta(hz(penta[idx]), dur), 0.22, rng.uniform(-.3, .3))
                if rng.random() < 0.5:
                    bus.add(tn + 0.5 * beat, campanilla(hz(penta[idx] + 12), 3.0), 0.07, 0.6)
                tn += dur + float(rng.choice([0, 0, beat * .5]))
    # animales del bosque
    for _ in range(70):  # búhos, constantes y respondiendo
        th = rng.uniform(0, T)
        f = rng.choice([300, 340, 380, 430])
        p = rng.uniform(-.85, .85)
        bus.add(th, buho_ul(f), 0.5, p)
        if rng.random() < 0.6:
            bus.add(th + rng.uniform(2.5, 5), buho_ul(f * 1.12), 0.38, -p)
    for _ in range(45):
        bus.add(rng.uniform(0, T), grillo(rng.uniform(8, 18), rng.uniform(4000, 4600)), 0.13, rng.uniform(-.9, .9))
    for _ in range(35):
        bus.add(rng.uniform(0, T), rana(), 0.5, rng.uniform(-.9, .9))
    for _ in range(26):
        bus.add(rng.uniform(0, T), pajaro(), 0.45, rng.uniform(-.9, .9))
    for _ in range(6):
        bus.add(rng.uniform(0, T), cuco(), 0.4, rng.uniform(-.7, .7))
    for _ in range(int(T / 10)):  # goteo de la cueva
        tg = rng.uniform(0, T)
        p = rng.uniform(-.9, .9)
        g = gota()
        bus.add(tg, g, rng.uniform(.2, .45), p)
        bus.add(tg + 0.21, g, 0.1, p * .8)
    reverb(bus, tau=3.0, mezcla=0.38)
    exportar(bus, "fondo-capitulo-2")


# ============ Capítulo 3: el jefe final (gótico, tétrico) ============
def organo(f, d, lengueta=False, a=0.05, r=0.35):
    t = tt(d)
    pesos = [(0.5, .5), (1, 1.0), (2, .55), (3, .35), (4, .3), (6, .18), (8, .1)]
    if lengueta:
        pesos += [(5, .25), (7, .2), (9, .12)]
    s = sum(w * np.sin(2 * np.pi * f * h * t + h) for h, w in pesos)
    s *= 1 + 0.04 * np.sin(2 * np.pi * 5.2 * t)
    return s * env(d, a, min(r, d * .5)) * 0.18


def campana_gotica(f, d=7.0):
    t = tt(d)
    s = np.zeros_like(t)
    for r, a, k in [(0.5, 0.7, 0.5), (1, 1, 0.7), (1.19, .6, 0.9), (1.5, .35, 1.2), (2.0, .4, 1.4), (2.51, .2, 2.0), (3.2, .12, 2.8)]:
        s += a * np.sin(2 * np.pi * f * r * t) * np.exp(-k * t)
    s[:60] *= np.linspace(0, 1, 60)
    return s * 0.55


def coro(f, d, vocal="o", a=0.7, r=1.0):
    """Voz coral: armónicos pesados por formantes de la vocal."""
    t = tt(d)
    F = {"o": (500, 900), "a": (750, 1150), "u": (350, 700)}[vocal]
    s = np.zeros_like(t)
    for dt in (0.0, 0.007, -0.006):
        vib = 0.012 * np.sin(2 * np.pi * (5.1 + 0.4 * dt * 100) * t + dt * 90) * np.minimum(1, t / 1.2)
        ph = 2 * np.pi * np.cumsum(f * (1 + dt) * (1 + vib)) / SR
        for h in range(1, 16):
            fh = h * f
            if fh > 3500:
                break
            w = np.exp(-((fh - F[0]) / 200) ** 2) + 0.7 * np.exp(-((fh - F[1]) / 260) ** 2) + 0.05
            s += w * np.sin(h * ph + h * dt * 50) / h ** 0.4
    return s * env(d, a, r) / 3 * 0.12


def piano(f, d=1.4):
    t = tt(d)
    s = np.zeros_like(t)
    for h in range(1, 9):
        s += np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h * h)) / h ** 1.1 * np.exp(-(1.6 + 0.9 * h) * t)
    s[:25] *= np.linspace(0, 1, 25)
    return s * 0.55


def gong(f=62, d=6.0):
    t = tt(d)
    s = np.zeros_like(t)
    for r, a, k in [(1, 1, .7), (1.47, .6, .9), (2.09, .5, 1.1), (2.56, .4, 1.5), (3.4, .25, 2.0)]:
        s += a * np.sin(2 * np.pi * f * r * t * (1 + 0.01 * np.sin(2 * np.pi * 0.7 * t))) * np.exp(-k * t)
    s[:40] *= np.linspace(0, 1, 40)
    return s * 0.7


def cap3():
    rng = np.random.default_rng(33)
    np.random.seed(33)
    beat = 60 / 96
    bar = 4 * beat  # 2.5 s
    nbars = int(round(T / bar))  # 240
    ocho = beat / 2
    bus = Bus()
    # re menor armónica: Dm Bb A Dm | Gm Dm A Dm
    prog = [
        ([50, 53, 57, 62], 26), ([46, 50, 53, 58], 22), ([45, 49, 52, 57], 21), ([50, 53, 57, 62], 26),
        ([43, 46, 50, 55], 19), ([50, 53, 57, 62], 26), ([45, 49, 52, 57], 21), ([50, 53, 57, 62], 26),
    ]
    motivo = [
        [(0, 69, 3), (3, 74, 1), (4, 77, 2), (6, 76, 2)],
        [(0, 74, 4), (4, 70, 2), (6, 72, 2)],
        [(0, 73, 3), (3, 76, 1), (4, 81, 2), (6, 79, 2)],
        [(0, 77, 4), (4, 74, 4)],
        [(0, 70, 3), (3, 74, 1), (4, 79, 2), (6, 77, 2)],
        [(0, 74, 4), (4, 69, 2), (6, 70, 2)],
        [(0, 73, 2), (2, 76, 2), (4, 81, 2), (6, 80, 2)],
        [(0, 74, 8)],
    ]
    inten = lambda t: 0.2 + 0.8 * float(arco_en(t, 3))
    for b in range(nbars):
        t0 = b * bar
        ac, bj = prog[b % 8]
        i = inten(t0)
        # órgano de iglesia: pedal grave y acorde sostenido
        bus.add(t0, organo(hz(bj), bar + 0.5, a=0.3, r=0.8), 0.5, 0)
        for n in ac[1:]:
            bus.add(t0, organo(hz(n), bar + 0.4, a=0.25, r=0.7), 0.3, rng.uniform(-.4, .4))
        # campana fúnebre
        if b % 2 == 0 or i > 0.55:
            bus.add(t0, campana_gotica(hz(bj + 12) if b % 4 else hz(bj + 24)), 0.35, 0.15)
        # piano ominoso: arpegio
        if i > 0.15:
            orden = [0, 1, 2, 3, 2, 1, 2, 1]
            for k in range(8):
                if k % 2 == 0 or i > 0.6:
                    bus.add(t0 + k * ocho, piano(hz(ac[orden[k] if orden[k] else 0] + 12), 1.2), 0.1 + 0.05 * i, -0.4 + 0.1 * k / 2)
        # tema gótico: órgano de lengüeta (+ coro cuando sube)
        for e0, n, d in motivo[b % 8]:
            bus.add(t0 + e0 * ocho, organo(hz(n), d * ocho * 1.02, lengueta=True, a=0.03, r=0.25), 0.28, 0.1)
            if i > 0.5:
                bus.add(t0 + e0 * ocho, coro(hz(n - 12), d * ocho + 0.3, "o" if d > 2 else "a", a=0.15, r=0.5), 0.55, -0.1)
        # coro sostenido, grave y lento
        if b % 2 == 0 and i > 0.35:
            for n, v in zip(ac[:3], ("o", "u", "o")):
                bus.add(t0, coro(hz(n), 2 * bar + 0.5, v), 0.8, rng.uniform(-.5, .5))
        # percusión grave y solemne
        if i > 0.3:
            bus.add(t0, timbal(1.3, 100, 42), 0.75, 0)
            if i > 0.55:
                bus.add(t0 + 2 * beat, timbal(1.0, 100, 46), 0.55, 0)
        if i > 0.65:
            for k in range(8):
                bus.add(t0 + k * ocho, bajo(hz(bj + 12), 0.28) * 0.7, 0.2, 0.0)
        if i > 0.8 and b % 2 == 1:
            bus.add(t0 + 3 * beat, tom(0.7, 120, 60), 0.35, 0.2)
            bus.add(t0 + 3.5 * beat, tom(0.6, 110, 55), 0.35, -0.2)
        # cuerdas bajas con trémolo cada cierto tiempo (tensión sorda, no estridente)
        if b % 8 == 4 and i > 0.4:
            bus.add(t0, tremolo(hz(50), 2 * bar), 0.08, -0.3)
            bus.add(t0, tremolo(hz(56), 2 * bar), 0.06, 0.3)  # tritono
        if b % 16 == 0 and i > 0.5:
            bus.add(t0, gong(), 0.7, 0)
    reverb(bus, tau=3.4, mezcla=0.45)  # iglesia / catedral
    exportar(bus, "fondo-capitulo-3")


if __name__ == "__main__":
    que = sys.argv[1] if len(sys.argv) > 1 else "todas"
    for n, f in [("1", cap1), ("2", cap2), ("3", cap3)]:
        if que in (n, "todas"):
            print("capítulo", n)
            f()

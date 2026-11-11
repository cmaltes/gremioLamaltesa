"""Paso 5 (árboles): repinta un mapa por teselas con SD1.5 img2img + IP-Adapter, usando de referencia un recorte de la feria
(copas oscuras de acuarela con contorno). Uso: tools/.venv-ia/bin/python tools/ia_arboles.py <entrada> <salida.png> [fuerza] [escala_ip] [tesela]
Entorno: SOLO="x,y" para generar una sola tesela (prueba)."""
import sys, os, torch
import numpy as np
from pathlib import Path
from PIL import Image
DT = torch.float32
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from transformers import CLIPVisionModelWithProjection

ent, sal = Path(sys.argv[1]), Path(sys.argv[2])
fuerza = float(sys.argv[3]) if len(sys.argv) > 3 else .5
esc = float(sys.argv[4]) if len(sys.argv) > 4 else .6
T = int(sys.argv[5]) if len(sys.argv) > 5 else 640
SOL = 128; PASO = T - SOL
M = Path(__file__).parent.parent / "public/aventuras/la-feria-del-misterio/mapas"
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=DT)
pipe = StableDiffusionImg2ImgPipeline.from_pretrained("Lykon/dreamshaper-8", torch_dtype=DT, image_encoder=enc, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min")
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.safetensors"); pipe.set_ip_adapter_scale(esc)
pipe.enable_sequential_cpu_offload(); pipe.vae.enable_slicing()
ref = Image.open(M / "feria.jpg").convert("RGB").crop((0, 0, 700, 700)).resize((448, 448))
prompt = ("top-down fantasy battle map, dense forest canopy seen from above, rounded tree crowns, dark muted green painterly watercolor, "
          "thick dark ink outlines, hand drawn, same style as reference, no trunks visible, no grid, no text")
neg = "house, hut, roof, building, cabin, door, side view, trunks, pixel art, bright saturated colors, orange, yellow, grid lines, text, watermark, people, photo, 3d render, blurry"
im = Image.open(ent).convert("RGB"); W, H = im.size
xs = list(range(0, max(1, W - T) + 1, PASO)); ys = list(range(0, max(1, H - T) + 1, PASO))
if xs[-1] != W - T: xs.append(W - T)
if ys[-1] != H - T: ys.append(H - T)
acc = np.zeros((H, W, 3), np.float32); pes = np.zeros((H, W, 1), np.float32)
r = np.minimum(np.arange(T) + 1, T - np.arange(T)).astype(np.float32); r = np.minimum(r / SOL, 1)
peso = (r[:, None] * r[None, :])[..., None]
solo = os.environ.get("SOLO")
for y in ys:
    for x in xs:
        if solo and solo != f"{x},{y}": continue
        t = im.crop((x, y, x + T, y + T))
        o = pipe(prompt=prompt, negative_prompt=neg, image=t, ip_adapter_image=ref, strength=fuerza, num_inference_steps=30, guidance_scale=6.5,
                 generator=torch.Generator("cpu").manual_seed(7)).images[0]
        a = np.array(o, np.float32); acc[y:y + T, x:x + T] += a * peso; pes[y:y + T, x:x + T] += peso
        print("tesela", x, y, flush=True)
        if solo: o.save(sal); sys.exit()
Image.fromarray((acc / np.maximum(pes, 1e-6)).astype(np.uint8)).save(sal); print("OK", sal)

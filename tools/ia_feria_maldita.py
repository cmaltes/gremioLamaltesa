"""Repinta el mapa de la feria como una feria MALDITA (de noche, tétrica) por teselas con SD1.5 img2img + IP-Adapter.
Sale sin rejilla: la cuadrícula se vuelve a dibujar con mapas_pdf.py (misma geometría que feria.jpg).
Uso: tools/.venv-ia/bin/python tools/ia_feria_maldita.py [fuerza] [escala_ip]   → _originales/mapas/feria-maldita-ia-sin-rejilla.png"""
import sys, os, torch
import numpy as np
from pathlib import Path
from PIL import Image
DT = torch.float32
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from transformers import CLIPVisionModelWithProjection

RAIZ = Path(__file__).resolve().parent.parent
M = RAIZ / "public/aventuras/la-feria-del-misterio/mapas"
SAL = RAIZ / "_originales/mapas/feria-maldita-ia-sin-rejilla.png"
fuerza = float(sys.argv[1]) if len(sys.argv) > 1 else .55
esc = float(sys.argv[2]) if len(sys.argv) > 2 else .35
T = 640; SOL = 128; PASO = T - SOL
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=DT)
pipe = StableDiffusionImg2ImgPipeline.from_pretrained("Lykon/dreamshaper-8", torch_dtype=DT, image_encoder=enc, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min")
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.safetensors"); pipe.set_ip_adapter_scale(esc)
pipe.enable_sequential_cpu_offload(); pipe.vae.enable_slicing()
prompt = ("top-down fantasy battle map of a cursed haunted fairground at night, sinister purple and sickly green moonlight, dark gloomy muted colors, "
          "dead twisted trees, creeping thorny vines, torn tattered tents, rusty broken ferris wheel, cracked carousel, glowing violet lanterns, cobwebs, "
          "hand drawn painterly with thick dark ink outlines, same layout and style as the input, no grid, no text, no people")
neg = "bright, cheerful, saturated, daylight, sunny, grid lines, text, watermark, people, characters, photo, 3d render, blurry, gore, blood"
im = Image.open(M / "feria.jpg").convert("RGB"); W, H = im.size
ref = im.crop((900, 0, 1700, 800)).resize((448, 448))
xs = list(range(0, max(1, W - T) + 1, PASO)); ys = list(range(0, max(1, H - T) + 1, PASO))
if xs[-1] != W - T: xs.append(W - T)
if ys[-1] != H - T: ys.append(H - T)
acc = np.zeros((H, W, 3), np.float32); pes = np.zeros((H, W, 1), np.float32)
r = np.minimum(np.arange(T) + 1, T - np.arange(T)).astype(np.float32); r = np.minimum(r / SOL, 1)
peso = (r[:, None] * r[None, :])[..., None]
for y in ys:
    for x in xs:
        t = im.crop((x, y, x + T, y + T))
        o = pipe(prompt=prompt, negative_prompt=neg, image=t, ip_adapter_image=ref, strength=fuerza, num_inference_steps=30, guidance_scale=7,
                 generator=torch.Generator("cpu").manual_seed(7)).images[0]
        a = np.array(o, np.float32); acc[y:y + T, x:x + T] += a * peso; pes[y:y + T, x:x + T] += peso
        print("tesela", x, y, flush=True)
out = (acc / np.maximum(pes, 1e-6))
Image.fromarray(out.astype(np.uint8)).save(SAL); print("OK", SAL)

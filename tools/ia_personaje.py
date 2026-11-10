"""Genera un personaje con SD1.5 + IP-Adapter (estilo de referencia).
Uso: tools/.venv-ia/bin/python tools/ia_personaje.py <salida.png> "<prompt>" [semilla] [escala_ip]"""
import sys, os, torch
from pathlib import Path
from PIL import Image
DT = torch.float32
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from transformers import CLIPVisionModelWithProjection

out, prompt = Path(sys.argv[1]), sys.argv[2]
semilla = int(sys.argv[3]) if len(sys.argv) > 3 else 1
esc = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
REF = Path(__file__).parent.parent / "public/aventuras/la-feria-del-misterio/personajes"
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=DT)
pipe = StableDiffusionPipeline.from_pretrained("Lykon/dreamshaper-8", torch_dtype=DT, image_encoder=enc, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min")
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.safetensors")
pipe.set_ip_adapter_scale(esc)
pipe.enable_sequential_cpu_offload(); pipe.vae.enable_slicing(); pass
import os
def cuerpo(n, fondo=(200, 200, 205)):  # recorte de cuerpo entero sobre gris liso, 512x768
    r = Image.open(REF / f"{n}.png").convert("RGBA"); r.thumbnail((470, 730))
    l = Image.new("RGB", (512, 768), fondo); l.paste(r, ((512 - r.width) // 2, 768 - r.height - 15), r); return l
ref = cuerpo(os.environ.get("REF", "glitch"))
neg = "close-up, portrait, bust, waist up, cropped, 3d render, cgi, plastic, smooth skin, airbrushed, anime, cartoon flat, photo, cut off, cropped, out of frame, text, watermark, signature, frame, border, blurry, lowres, deformed hands, extra fingers, extra limbs, ugly, photo background, ground, shadow"
# fp32 + offload secuencial: en la GTX 1650 el fp16 da NaN (imágenes negras) y el fp32 normal no cabe en 4 GB
img = pipe(prompt=prompt, negative_prompt=neg, ip_adapter_image=ref, width=int(os.environ.get("W", 512)), height=int(os.environ.get("H", 768)), num_inference_steps=28, guidance_scale=6.5,
           generator=torch.Generator("cpu").manual_seed(semilla)).images[0]
img.save(out); print("OK", out)

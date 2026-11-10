"""Amplía por arriba y por abajo un personaje cortado (outpainting con SD1.5 inpainting, fp32 + offload).
Uso: tools/.venv-ia/bin/python tools/ia_extender.py <entrada.png> <salida.png> "<prompt de lo que falta>" [arriba] [abajo] [semilla]"""
import sys, torch
import numpy as np
from PIL import Image, ImageFilter
from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler

ent, sal, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
arr = int(sys.argv[4]) if len(sys.argv) > 4 else 128
aba = int(sys.argv[5]) if len(sys.argv) > 5 else 256
semilla = int(sys.argv[6]) if len(sys.argv) > 6 else 1
im = Image.open(ent).convert("RGB"); w, h = im.size
H = h + arr + aba
# lienzo: se rellena lo nuevo con el color medio del borde (arriba/abajo) y se pinta solo lo nuevo (+ 24 px de solape)
lienzo = Image.new("RGB", (w, H))
lienzo.paste(im.crop((0, 0, w, 1)).resize((w, arr)), (0, 0)) if arr else None
lienzo.paste(im.crop((0, h - 1, w, h)).resize((w, aba)), (0, arr + h)) if aba else None
lienzo.paste(im, (0, arr))
mask = Image.new("L", (w, H), 0); m = np.array(mask)
if arr: m[: arr + 24] = 255
if aba: m[arr + h - 24:] = 255
mask = Image.fromarray(m).filter(ImageFilter.GaussianBlur(6))
pipe = StableDiffusionInpaintPipeline.from_pretrained("Lykon/dreamshaper-8-inpainting", torch_dtype=torch.float32, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min")
pipe.enable_sequential_cpu_offload()
neg = "close-up, portrait, cropped, text, watermark, blurry, deformed, extra limbs, floor shadow, 3d render, plastic"
out = pipe(prompt=prompt, negative_prompt=neg, image=lienzo, mask_image=mask, width=w, height=H, num_inference_steps=30, guidance_scale=7,
           generator=torch.Generator("cpu").manual_seed(semilla)).images[0]
out.save(sal); print("OK", sal, out.size)

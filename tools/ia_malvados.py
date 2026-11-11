"""Versiones MALVADAS de los kobolds (img2img + IP-Adapter sobre el personaje original).
Uso: tools/.venv-ia/bin/python tools/ia_malvados.py [nombre ...]   (por defecto: glitch gart zash mizzen)
Salida: _originales/personajes/malvados/<nombre>-s<semilla>.png (512x768 sobre gris). Luego: tools/malvados_recortar.py"""
import sys, os, torch
from pathlib import Path
from PIL import Image
DT = torch.float32
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from transformers import CLIPVisionModelWithProjection

RAIZ = Path(__file__).resolve().parent.parent
REF = RAIZ / "public/aventuras/la-feria-del-misterio/personajes"
SAL = RAIZ / "_originales/personajes/malvados"; SAL.mkdir(parents=True, exist_ok=True)
FUERZA = float(os.environ.get("FUERZA", .62)); SEMILLAS = [int(x) for x in os.environ.get("SEMILLAS", "1,2,3").split(",")]
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=DT)
pipe = StableDiffusionImg2ImgPipeline.from_pretrained("Lykon/dreamshaper-8", torch_dtype=DT, image_encoder=enc, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min")
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.safetensors"); pipe.set_ip_adapter_scale(float(os.environ.get("IP", .45)))
pipe.enable_sequential_cpu_offload(); pipe.vae.enable_slicing()

def cuerpo(n, fondo=(200, 200, 205)):
    r = Image.open(REF / f"{n}.png").convert("RGBA"); r.thumbnail((470, 730))
    l = Image.new("RGB", (512, 768), fondo); l.paste(r, ((512 - r.width) // 2, 768 - r.height - 15), r); return l

BASE = ("full body character illustration, corrupted evil character, grey-green sickly skin, glowing red eyes, wicked sharp-toothed grin, "
        "long pointed ears, dark purple sinister glow around him, same pose, ragged dark version of the same clothes, "
        "warm detailed digital painting, storybook fairground style, standing facing viewer, feet visible, plain light grey background, no ground shadow, menacing but kid friendly")
EXTRA = {
    "glitch": "dark violet velvet waistcoat with torn sleeves, tiny dark cap, cunning smirk",
    "gart": "big strong brute, dark patchwork vest stuffed and ripped, scowling",
    "zash": "small and fast, dark green cap and torn vest, nervous manic grin, jumpy",
    "alarico": "tall elegant sorcerer ringmaster in dark violet velvet coat with torn tails, sinister cracked mask-like grin, cold cruel stare, crackling dark magic in his hands",
    "mizzen": "thin hoarder, dark green cap, greedy hungry stare, shiny stolen trinkets",
}
neg = "close-up, portrait, bust, cropped, 3d render, cgi, plastic, anime, flat cartoon, photo, text, watermark, frame, blurry, lowres, deformed hands, extra fingers, extra limbs, gore, blood, photo background, ground, shadow, nsfw"
nombres = sys.argv[1:] or list(EXTRA)
for n in nombres:
    ini = cuerpo(n)
    for s in SEMILLAS:
        out = SAL / f"{n}-s{s}.png"
        if out.exists(): continue
        img = pipe(prompt=f"{BASE}, {EXTRA[n]}", negative_prompt=neg, image=ini, ip_adapter_image=ini, strength=FUERZA, num_inference_steps=30, guidance_scale=7,
                   generator=torch.Generator("cpu").manual_seed(s)).images[0]
        img.save(out); print("OK", out, flush=True)

"""Genera los retratos de los 10 héroes (chico y chica) con SD1.5 + IP-Adapter, de media figura, para las fichas.
Uso: tools/.venv-ia/bin/python tools/ia_heroes.py [semilla] [clase ...]   (salida: _originales/heroes/<clase>-<chico|chica>-s<semilla>.png)"""
import sys, torch
from pathlib import Path
from PIL import Image
DT = torch.float32
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from transformers import CLIPVisionModelWithProjection

RAIZ = Path(__file__).parent.parent
semilla = int(sys.argv[1]) if len(sys.argv) > 1 else 1
solo = sys.argv[2:]
import os
IPS = float(os.environ.get("IPS", .5))   # fuerza del IP-Adapter (más bajo = menos contagio de la referencia)
EXTRA = {"barbaro": "brown fur and red leather clothes, big axe clearly visible", "bardo": "colorful pink and yellow clothes, big feathered hat, lute clearly visible",
         "monje": "orange and white robes, bare forearms, fighting stance", "picaro": "dark gray and purple clothes, dagger clearly visible", "explorador": "big longbow clearly visible in the hand"} if os.environ.get("EXTRA") else {}
PELO = {"boy": "boy with short messy hair", "girl": "girl with long braided hair"} if os.environ.get("EXTRA") else {"boy": "boy", "girl": "girl"}
CLASES = {
    "guerrero": "warrior in shiny metal armor with a red plume, holding a round shield and a broad sword",
    "barbaro": "barbarian with a fur vest and wild hair, holding a huge two-handed axe, shouting happily",
    "explorador": "ranger in a green hooded cape holding a longbow, quiver of arrows on the back",
    "picaro": "rogue in a dark hood with a sly smile, holding a dagger, lockpicks on the belt",
    "mago": "wizard in a starry purple robe and pointed hat, holding a glowing wand and a spellbook",
    "clerigo": "cleric in a white and gold robe with a golden sun symbol, holding a mace, kind smile",
    "druida": "druid in a cloak made of leaves, holding a wooden staff and a small wooden flute, a little bird on the shoulder",
    "bardo": "bard with a feathered hat playing a lute, cheerful singing expression",
    "monje": "monk with a headband and simple robes in a martial arts pose, calm confident face",
    "paladin": "paladin in silver armor with a white cape, holding a shield with a sun emblem and a sword",
}
BASE = ("{sexo} young adventurer, {d}, oil painting style, visible brushwork, painterly textures, slightly caricatured expressive friendly face, "
        "storybook illustration, half-body portrait from head to hips, centered, plain light gray background")
NEG = ("full body, 3d render, cgi, plastic, smooth skin, airbrushed, anime, photo, text, watermark, signature, frame, border, blurry, lowres, deformed hands, "
       "extra fingers, extra limbs, ugly, nsfw, revealing clothes, child, toddler, old, beard" )
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=DT)
pipe = StableDiffusionPipeline.from_pretrained("Lykon/dreamshaper-8", torch_dtype=DT, image_encoder=enc, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++", final_sigmas_type="sigma_min")
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter_sd15.safetensors"); pipe.set_ip_adapter_scale(IPS)
pipe.enable_sequential_cpu_offload(); pipe.vae.enable_slicing()
ref = Image.open(RAIZ / "public/aventuras/la-feria-del-misterio/personajes/aerion-retrato.jpg").convert("RGB")
out = RAIZ / "_originales/heroes"; out.mkdir(parents=True, exist_ok=True)
for c, d in CLASES.items():
    if solo and c not in solo: continue
    for sexo, nombre in (("boy", "chico"), ("girl", "chica")):
        f = out / f"{c}-{nombre}-s{semilla}.png"
        if f.exists(): continue
        img = pipe(prompt=BASE.format(sexo=PELO[sexo], d=d + (', ' + EXTRA[c] if c in EXTRA else '')), negative_prompt=NEG, ip_adapter_image=ref, width=512, height=768, num_inference_steps=28, guidance_scale=6.5,
                   generator=torch.Generator("cpu").manual_seed(semilla)).images[0]
        img.save(f); print("OK", f.name, flush=True)

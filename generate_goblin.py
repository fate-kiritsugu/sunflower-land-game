from PIL import Image, ImageDraw
import math

# ── Cargar y recortar primer goblin ───────────────────────────
src    = Image.open('public/world/big_goblin.png').convert('RGBA')
goblin = src.crop((0, 0, 27, 35))

# ── Escalar 4x (pixel art, sin blur) ──────────────────────────
SCALE  = 4
GW, GH = 27 * SCALE, 35 * SCALE   # 108 x 140
big    = goblin.resize((GW, GH), Image.NEAREST)

# ── Puntos de corte (en pixels escalados) ─────────────────────
BODY_BOTTOM = 26 * SCALE   # fila donde terminan el torso
LEG_MID     = 13 * SCALE   # mitad horizontal para separar piernas

# Recortar partes
body     = big.crop((0,        0,        GW,       BODY_BOTTOM))
leg_l    = big.crop((0,        BODY_BOTTOM, LEG_MID, GH))
leg_r    = big.crop((LEG_MID,  BODY_BOTTOM, GW,      GH))

# ── Config animación ──────────────────────────────────────────
FRAMES     = 12
STEP_PX    = 6      # cuántos pixels se mueve cada pierna arriba/abajo
CANVAS_W   = GW + 20
CANVAS_H   = GH + STEP_PX * 2 + 20
BG         = (10, 10, 26, 255)

frames = []

for f in range(FRAMES):
    t     = f * (2 * math.pi / FRAMES)
    swing = math.sin(t)           # -1 .. 1

    # Pierna izquierda sube cuando derecha baja
    off_l = int(-swing * STEP_PX)
    off_r = int( swing * STEP_PX)

    img  = Image.new('RGBA', (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(img)

    # Origen del goblin dentro del canvas
    ox = (CANVAS_W - GW) // 2
    oy = STEP_PX + 5

    # ── Sombra ────────────────────────────────────────────────
    sx     = ox + GW // 2
    sy     = oy + GH + STEP_PX - 4
    s_rx   = 28 + int(swing * 4)
    draw.ellipse([sx - s_rx, sy - 5, sx + s_rx, sy + 5],
                 fill=(0, 0, 0, 100))

    # ── Cuerpo (estático) ─────────────────────────────────────
    img.alpha_composite(body, (ox, oy))

    # ── Pierna izquierda ──────────────────────────────────────
    img.alpha_composite(leg_l, (ox,          oy + BODY_BOTTOM + off_l))

    # ── Pierna derecha ────────────────────────────────────────
    img.alpha_composite(leg_r, (ox + LEG_MID, oy + BODY_BOTTOM + off_r))

    frames.append(img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=256))

# ── Guardar GIF ───────────────────────────────────────────────
out = 'goblin_walk.gif'
frames[0].save(
    out,
    save_all=True,
    append_images=frames[1:],
    duration=70,
    loop=0,
)
print(f"Listo: {out}  ({FRAMES} frames, {CANVAS_W}x{CANVAS_H}px)")

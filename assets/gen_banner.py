#!/usr/bin/env python3
"""Generate hypebot-rs banner — Signal Architecture philosophy. Second pass: refined."""

from PIL import Image, ImageDraw, ImageFont
import math
import random

W, H = 1280, 640
FONT_DIR = "/home/ubuntu/.claude/skills/canvas-design/canvas-fonts"

# === Color Protocol ===
BG_DEEP    = (5, 8, 18)
BG_MID     = (9, 14, 28)
CYAN       = (14, 165, 233)
GREEN      = (34, 197, 94)
GREEN_DIM  = (22, 163, 74)
RED_DIM    = (220, 38, 38)
VIOLET     = (139, 92, 246)
AMBER      = (245, 158, 11)
WHITE      = (248, 250, 252)
SLATE      = (148, 163, 184)
SLATE_DARK = (51, 65, 85)

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def create_banner():
    img = Image.new('RGB', (W, H), BG_DEEP)
    draw = ImageDraw.Draw(img)

    # === Background gradient (diagonal) ===
    for y in range(H):
        for x in range(0, W, 1):
            t = (x / W * 0.4 + y / H * 0.6)
            bg = lerp_color(BG_DEEP, (11, 18, 36), t)
            draw.point((x, y), fill=bg)

    # === Subtle dot grid ===
    for gx in range(24, W, 28):
        for gy in range(24, H, 28):
            dx = (gx - W * 0.65) / W
            dy = (gy - H * 0.40) / H
            dist = math.sqrt(dx * dx + dy * dy)
            opacity = max(0, 0.18 - dist * 0.2)
            if opacity > 0.005:
                c = lerp_color(BG_MID, CYAN, opacity * 0.5)
                draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=c)

    # === Scan lines (CRT feel) ===
    for y in range(0, H, 3):
        c = lerp_color(BG_MID, (255, 255, 255), 0.012)
        draw.line([(0, y), (W, y)], fill=c)

    # === Market data visualization (right side) ===
    random.seed(7)
    prices = []
    p = 100
    for i in range(55):
        change = random.gauss(0, 2.8)
        o = p
        p += change
        h = max(o, p) + abs(random.gauss(0, 1.5))
        l = min(o, p) - abs(random.gauss(0, 1.5))
        prices.append((o, h, l, p))

    chart_x_start = W * 0.50
    chart_x_end = W * 0.94
    chart_y_center = H * 0.36
    chart_height = 160
    bar_width = (chart_x_end - chart_x_start) / len(prices)

    all_highs = [p[1] for p in prices]
    all_lows = [p[2] for p in prices]
    price_min, price_max = min(all_lows), max(all_highs)
    price_range = price_max - price_min

    def price_to_y(price):
        return chart_y_center - ((price - (price_min + price_max) / 2) / price_range) * chart_height

    # Draw candles
    for i, (o, h, l, c) in enumerate(prices):
        x = chart_x_start + i * bar_width + bar_width / 2
        bullish = c >= o

        # Progressive reveal (fade in from left)
        fade = min(1.0, (i / len(prices)) * 1.8)
        base_alpha = 0.15 + fade * 0.55

        if bullish:
            body_color = lerp_color(BG_MID, GREEN, base_alpha)
            wick_color = lerp_color(BG_MID, GREEN, base_alpha * 0.5)
        else:
            body_color = lerp_color(BG_MID, RED_DIM, base_alpha * 0.7)
            wick_color = lerp_color(BG_MID, RED_DIM, base_alpha * 0.4)

        # Wick
        wick_x = int(x)
        draw.line([(wick_x, int(price_to_y(h))), (wick_x, int(price_to_y(l)))], fill=wick_color, width=1)

        # Body
        y_open = price_to_y(o)
        y_close = price_to_y(c)
        body_top = min(y_open, y_close)
        body_bot = max(y_open, y_close)
        if body_bot - body_top < 2:
            body_bot = body_top + 2
        bw = max(2, int(bar_width * 0.6))
        draw.rectangle([int(x - bw / 2), int(body_top), int(x + bw / 2), int(body_bot)], fill=body_color)

    # === Moving average line over candles ===
    closes = [p[3] for p in prices]
    ma_period = 8
    ma_values = []
    for i in range(len(closes)):
        if i < ma_period:
            ma_values.append(sum(closes[:i + 1]) / (i + 1))
        else:
            ma_values.append(sum(closes[i - ma_period + 1:i + 1]) / ma_period)

    for i in range(1, len(ma_values)):
        x1 = chart_x_start + (i - 1) * bar_width + bar_width / 2
        x2 = chart_x_start + i * bar_width + bar_width / 2
        y1 = price_to_y(ma_values[i - 1])
        y2 = price_to_y(ma_values[i])
        fade = min(1.0, i / len(ma_values) * 2)
        line_c = lerp_color(BG_MID, CYAN, 0.2 + fade * 0.4)
        draw.line([(int(x1), int(y1)), (int(x2), int(y2))], fill=line_c, width=2)

    # === Glow sources ===
    glow_img = Image.new('RGB', (W, H), (0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)

    def draw_radial_glow(target_draw, cx, cy, radius, color, peak=0.08):
        for r in range(radius, 0, -2):
            t = 1 - (r / radius)
            a = peak * t * t
            c = lerp_color((0, 0, 0), color, a)
            target_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    draw_radial_glow(glow_draw, int(W * 0.72), int(H * 0.30), 250, CYAN, 0.10)
    draw_radial_glow(glow_draw, int(W * 0.12), int(H * 0.85), 180, GREEN, 0.06)
    draw_radial_glow(glow_draw, int(W * 0.92), int(H * 0.75), 140, VIOLET, 0.06)

    # Screen-blend the glow
    from PIL import ImageChops
    img = ImageChops.add(img, glow_img)
    draw = ImageDraw.Draw(img)

    # === Horizontal signal lines ===
    for y_pct, color, alpha in [(0.165, CYAN, 0.04), (0.60, GREEN, 0.035), (0.82, VIOLET, 0.03)]:
        y = int(H * y_pct)
        c = lerp_color(BG_MID, color, alpha)
        draw.line([(40, y), (W - 40, y)], fill=c, width=1)
        # Bright pulse nodes
        for nx in [80, 280, 500, 720, 940, W - 80]:
            node_c = lerp_color(BG_MID, color, alpha * 4)
            draw.ellipse([nx - 2, y - 2, nx + 2, y + 2], fill=node_c)

    # === Typography ===
    font_title = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Bold.ttf", 72)
    font_sub = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Regular.ttf", 19)
    font_desc = ImageFont.truetype(f"{FONT_DIR}/InstrumentSans-Regular.ttf", 18)
    font_label = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Regular.ttf", 12)
    font_tag = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Bold.ttf", 11)

    title_x = 80
    title_y = 210

    # Title glow layers
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            dist = math.sqrt(dx * dx + dy * dy)
            a = max(0, 0.08 - dist * 0.02)
            gc = lerp_color(BG_MID, CYAN, a)
            draw.text((title_x + dx, title_y + dy), "hypebot-rs", font=font_title, fill=gc)

    draw.text((title_x, title_y), "hypebot-rs", font=font_title, fill=WHITE)

    # Subtitle
    sub_y = title_y + 86
    draw.text((title_x, sub_y), "Rust trading infrastructure for Hyperliquid", font=font_sub, fill=CYAN)

    # Accent line under subtitle
    sub_bbox = draw.textbbox((title_x, sub_y), "Rust trading infrastructure for Hyperliquid", font=font_sub)
    line_y = sub_y + 30
    draw.line([(title_x, line_y), (sub_bbox[2], line_y)], fill=lerp_color(BG_MID, CYAN, 0.15), width=1)

    # Description
    desc_y = line_y + 16
    desc_lines = [
        "Typed market feeds · Serialized execution · Long-running resilience",
        "Built as a service system, not a script",
    ]
    for i, line in enumerate(desc_lines):
        draw.text((title_x, desc_y + i * 26), line, font=font_desc, fill=SLATE)

    # === Bottom status indicators ===
    indicators = [
        ("RUNTIME", CYAN, "heartbeat / reconnect / stale detection"),
        ("EXECUTION", GREEN, "serialized order flow / nonce safety"),
        ("STRATEGY", VIOLET, "breakout-retest / ATR / ADX / BB / volume"),
    ]

    ind_y = int(H * 0.78)

    for i, (label, color, desc) in enumerate(indicators):
        x = 80 + i * 380

        # Glowing status dot
        for r in range(8, 0, -1):
            a = 0.05 + (1 - r / 8) * 0.35
            dc = lerp_color(BG_MID, color, a)
            draw.ellipse([x - r + 4, ind_y - r + 4, x + r + 4, ind_y + r + 4], fill=dc)

        # Label
        draw.text((x + 18, ind_y - 4), label, font=font_tag, fill=color)

        # Description
        desc_c = lerp_color(BG_MID, color, 0.45)
        draw.text((x + 18, ind_y + 12), desc, font=font_label, fill=desc_c)

    # === Top-right badge ===
    tag_text = "PRIVATE SOURCE / PUBLIC SHOWCASE"
    bbox = draw.textbbox((0, 0), tag_text, font=font_label)
    tw = bbox[2] - bbox[0]
    tag_x = W - 80 - tw - 16
    tag_y = 36

    # Badge background
    draw.rounded_rectangle(
        [tag_x - 8, tag_y - 6, tag_x + tw + 8, tag_y + 18],
        radius=4,
        fill=lerp_color(BG_MID, CYAN, 0.06),
        outline=lerp_color(BG_MID, CYAN, 0.15)
    )
    draw.text((tag_x, tag_y), tag_text, font=font_label, fill=lerp_color(BG_MID, CYAN, 0.6))

    # === Corner registration marks ===
    mark_c = lerp_color(BG_MID, SLATE, 0.12)
    for cx, cy in [(32, 32), (W - 32, 32), (32, H - 32), (W - 32, H - 32)]:
        draw.line([(cx - 6, cy), (cx + 6, cy)], fill=mark_c, width=1)
        draw.line([(cx, cy - 6), (cx, cy + 6)], fill=mark_c, width=1)

    # === Outer frame ===
    frame_c = lerp_color(BG_MID, SLATE, 0.05)
    draw.rectangle([18, 18, W - 19, H - 19], outline=frame_c, width=1)

    # === Version marker (bottom right) ===
    ver_text = "v0.1 · active build"
    draw.text((W - 80 - draw.textbbox((0, 0), ver_text, font=font_label)[2], H - 42),
              ver_text, font=font_label, fill=lerp_color(BG_MID, SLATE, 0.25))

    return img


if __name__ == "__main__":
    img = create_banner()
    img.save("/home/ubuntu/hypebot-rs-showcase/assets/banner.png", quality=95)
    print("Banner saved.")

#!/usr/bin/env python3
"""Generate hypebot-rs architecture diagram — Signal Architecture philosophy."""

from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1200, 800
FONT_DIR = "/home/ubuntu/.claude/skills/canvas-design/canvas-fonts"

# === Color Protocol ===
BG_DEEP   = (5, 8, 18)
BG_MID    = (9, 14, 28)
BG_PANEL  = (11, 18, 34)
CYAN      = (14, 165, 233)
GREEN     = (34, 197, 94)
VIOLET    = (139, 92, 246)
AMBER     = (245, 158, 11)
RED       = (239, 68, 68)
SKY       = (56, 189, 248)
WHITE     = (248, 250, 252)
SLATE     = (148, 163, 184)
SLATE_DIM = (71, 85, 105)

def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def create_architecture():
    img = Image.new('RGB', (W, H), BG_DEEP)
    draw = ImageDraw.Draw(img)

    # === Background gradient ===
    for y in range(H):
        t = y / H
        bg = lerp(BG_DEEP, (10, 16, 32), t)
        draw.line([(0, y), (W, y)], fill=bg)

    # === Subtle grid ===
    for x in range(0, W, 24):
        draw.line([(x, 0), (x, H)], fill=lerp(BG_DEEP, SLATE, 0.015), width=1)
    for y in range(0, H, 24):
        draw.line([(0, y), (W, y)], fill=lerp(BG_DEEP, SLATE, 0.015), width=1)

    # === Scan lines ===
    for y in range(0, H, 3):
        draw.line([(0, y), (W, y)], fill=lerp(BG_DEEP, WHITE, 0.008))

    # === Fonts ===
    font_title = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Bold.ttf", 28)
    font_subtitle = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Regular.ttf", 14)
    font_comp = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Bold.ttf", 18)
    font_desc = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Regular.ttf", 11)
    font_label = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Regular.ttf", 10)
    font_layer = ImageFont.truetype(f"{FONT_DIR}/GeistMono-Bold.ttf", 10)

    # === Title area ===
    draw.text((56, 36), "hypebot-rs", font=font_title, fill=WHITE)
    draw.text((56, 68), "architecture overview", font=font_subtitle, fill=lerp(BG_MID, CYAN, 0.6))

    # Accent line under title
    draw.line([(56, 90), (340, 90)], fill=lerp(BG_MID, CYAN, 0.2), width=1)

    # === Helper: draw a component box ===
    def draw_component(x, y, w, h, label, desc, color, desc2=None):
        # Background with slight gradient
        for row in range(h):
            t = row / h
            bg = lerp(lerp(BG_DEEP, color, 0.06), lerp(BG_DEEP, color, 0.03), t)
            draw.line([(x, y + row), (x + w, y + row)], fill=bg)

        # Border
        border_c = lerp(BG_MID, color, 0.45)
        draw.rounded_rectangle([x, y, x + w, y + h], radius=8, outline=border_c, width=2)

        # Inner glow at top
        for i in range(3):
            glow = lerp(BG_MID, color, 0.08 - i * 0.02)
            draw.line([(x + 4, y + 2 + i), (x + w - 4, y + 2 + i)], fill=glow)

        # Status dot
        dot_x = x + 14
        dot_y = y + 16
        for r in range(6, 0, -1):
            a = 0.1 + (1 - r / 6) * 0.5
            dc = lerp(BG_MID, color, a)
            draw.ellipse([dot_x - r, dot_y - r, dot_x + r, dot_y + r], fill=dc)

        # Label
        draw.text((x + 26, y + 10), label, font=font_comp, fill=WHITE)

        # Description
        desc_c = lerp(BG_MID, color, 0.55)
        draw.text((x + 14, y + 36), desc, font=font_desc, fill=desc_c)
        if desc2:
            draw.text((x + 14, y + 52), desc2, font=font_desc, fill=lerp(BG_MID, color, 0.4))

    # === Helper: draw arrow ===
    def draw_arrow(x1, y1, x2, y2, color, weight=2, dashed=False):
        line_c = lerp(BG_MID, color, 0.35)

        if dashed:
            # Dashed line
            length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            dash_len = 8
            gap_len = 6
            if length == 0:
                return
            dx = (x2 - x1) / length
            dy = (y2 - y1) / length
            pos = 0
            while pos < length:
                sx = x1 + dx * pos
                sy = y1 + dy * pos
                end = min(pos + dash_len, length)
                ex = x1 + dx * end
                ey = y1 + dy * end
                draw.line([(int(sx), int(sy)), (int(ex), int(ey))], fill=line_c, width=weight)
                pos += dash_len + gap_len
        else:
            draw.line([(x1, y1), (x2, y2)], fill=line_c, width=weight)

        # Arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_len = 8
        arrow_angle = 0.45
        ax1 = x2 - arrow_len * math.cos(angle - arrow_angle)
        ay1 = y2 - arrow_len * math.sin(angle - arrow_angle)
        ax2 = x2 - arrow_len * math.cos(angle + arrow_angle)
        ay2 = y2 - arrow_len * math.sin(angle + arrow_angle)
        head_c = lerp(BG_MID, color, 0.5)
        draw.polygon([(x2, y2), (int(ax1), int(ay1)), (int(ax2), int(ay2))], fill=head_c)

    # === Layer labels (left margin) ===
    layers = [
        (130, "TRANSPORT", CYAN),
        (258, "PROCESSING", SKY),
        (390, "EXECUTION", GREEN),
        (548, "INFRASTRUCTURE", AMBER),
    ]

    for ly, label, color in layers:
        lc = lerp(BG_MID, color, 0.3)
        draw.text((24, ly), label, font=font_layer, fill=lc)
        # Vertical accent
        draw.line([(18, ly - 2), (18, ly + 12)], fill=lerp(BG_MID, color, 0.4), width=2)

    # === LAYER 1: TRANSPORT ===
    # HlWsClient
    draw_component(110, 118, 240, 72,
                   "HlWsClient", "websocket lifecycle manager",
                   CYAN, "subscribe · heartbeat · reconnect")

    # REST Client
    draw_component(400, 118, 200, 72,
                   "REST", "HTTP order interface",
                   CYAN, "placement · cancel · query")

    # === LAYER 2: PROCESSING ===
    # MarketFeed
    draw_component(110, 244, 220, 72,
                   "MarketFeed", "typed event pipeline",
                   SKY, "candles · trades · orderbook")

    # SymbolRunner
    draw_component(380, 244, 240, 72,
                   "SymbolRunner", "per-symbol lifecycle group",
                   SKY, "warmup · feed · strategy · watchdog")

    # Strategy
    draw_component(670, 244, 220, 72,
                   "Strategy", "signal generation layer",
                   VIOLET, "breakout-retest · filters · gates")

    # === LAYER 3: EXECUTION ===
    # OrderExecutor
    draw_component(200, 378, 260, 72,
                   "OrderExecutor", "serialized exchange calls",
                   GREEN, "nonce safety · race-condition guard")

    # Position Manager (implicit)
    draw_component(510, 378, 230, 72,
                   "PositionMgr", "order state tracking",
                   GREEN, "open · filled · canceled · failed")

    # === LAYER 4: INFRASTRUCTURE ===
    # State
    draw_component(110, 536, 200, 72,
                   "State", "persistent local context",
                   AMBER, "survive restarts · restore setup")

    # Watchdog
    draw_component(360, 536, 200, 72,
                   "Watchdog", "runtime health monitor",
                   RED, "stale feed · HTTP errors · recovery")

    # Notifications
    draw_component(610, 536, 220, 72,
                   "Notifications", "Discord pipeline",
                   SKY, "trade alerts · status · errors")

    # DryRun
    draw_component(880, 536, 180, 72,
                   "DryRun", "simulation mode",
                   SLATE, "safe testing · no real orders")

    # === ARROWS ===
    # Transport → Processing
    draw_arrow(230, 190, 220, 244, CYAN)       # HlWsClient → MarketFeed
    draw_arrow(500, 190, 500, 244, CYAN)        # REST → SymbolRunner

    # Processing flow
    draw_arrow(330, 280, 380, 280, SKY)          # MarketFeed → SymbolRunner
    draw_arrow(620, 280, 670, 280, VIOLET)       # SymbolRunner → Strategy

    # Strategy → back to SymbolRunner (signal)
    draw_arrow(780, 316, 780, 350, VIOLET, dashed=True)  # signal down
    draw_arrow(780, 350, 510, 350, GREEN, dashed=True)    # signal to execution area

    # Processing → Execution
    draw_arrow(500, 316, 330, 378, GREEN)        # SymbolRunner → OrderExecutor
    draw_arrow(500, 316, 620, 378, GREEN)        # SymbolRunner → PositionMgr

    # Execution → Transport (order calls)
    draw_arrow(260, 378, 450, 190, CYAN, dashed=True)  # OrderExecutor → REST

    # Execution → Infrastructure
    draw_arrow(330, 450, 210, 536, AMBER)       # OrderExecutor → State
    draw_arrow(625, 450, 720, 536, SKY)         # PositionMgr → Notifications

    # SymbolRunner → Infrastructure
    draw_arrow(440, 316, 460, 536, RED, dashed=True)    # SymbolRunner → Watchdog

    # DryRun connection
    draw_arrow(880, 572, 740, 450, SLATE, dashed=True)  # DryRun → PositionMgr

    # === Right side: Strategy detail panel ===
    panel_x, panel_y = 920, 118
    panel_w, panel_h = 240, 282

    # Panel background
    for row in range(panel_h):
        t = row / panel_h
        bg = lerp((8, 12, 24), (12, 16, 30), t)
        draw.line([(panel_x, panel_y + row), (panel_x + panel_w, panel_y + row)], fill=bg)

    draw.rounded_rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],
                           radius=8, outline=lerp(BG_MID, VIOLET, 0.3), width=1)

    # Panel title
    draw.text((panel_x + 14, panel_y + 12), "STRATEGY FILTERS", font=font_layer, fill=VIOLET)
    draw.line([(panel_x + 14, panel_y + 28), (panel_x + panel_w - 14, panel_y + 28)],
              fill=lerp(BG_MID, VIOLET, 0.15), width=1)

    filters = [
        ("01", "Structure break detection"),
        ("02", "Retest confirmation window"),
        ("03", "ADX trend strength gate"),
        ("04", "ATR-based buffer & stop"),
        ("05", "Bollinger Band width"),
        ("06", "Volume ratio check"),
        ("07", "Time filter & cooldown"),
        ("08", "Entry signal compose"),
    ]

    for i, (num, label) in enumerate(filters):
        fy = panel_y + 42 + i * 28
        # Number
        num_c = lerp(BG_MID, VIOLET, 0.5)
        draw.text((panel_x + 14, fy), num, font=font_label, fill=num_c)
        # Dot
        dot_c = lerp(BG_MID, VIOLET, 0.35)
        draw.ellipse([panel_x + 36, fy + 3, panel_x + 40, fy + 7], fill=dot_c)
        # Label
        draw.text((panel_x + 46, fy), label, font=font_label, fill=lerp(BG_MID, WHITE, 0.55))

    # Pipeline flow indicator (vertical line connecting filters)
    pipe_x = panel_x + 38
    draw.line([(pipe_x, panel_y + 48), (pipe_x, panel_y + 42 + 7 * 28 + 6)],
              fill=lerp(BG_MID, VIOLET, 0.12), width=1)

    # === Bottom bar ===
    bar_y = H - 44
    draw.line([(40, bar_y), (W - 40, bar_y)], fill=lerp(BG_MID, SLATE, 0.08), width=1)

    # Bottom labels
    draw.text((56, bar_y + 10), "hypebot-rs · architecture v0.1", font=font_label,
              fill=lerp(BG_MID, SLATE, 0.3))

    legend_items = [
        ("data flow", CYAN),
        ("signal path", VIOLET),
        ("execution", GREEN),
        ("feedback", SLATE),
    ]
    lx = W - 56
    for label, color in reversed(legend_items):
        bbox = draw.textbbox((0, 0), label, font=font_label)
        tw = bbox[2] - bbox[0]
        lx -= tw + 24
        draw.ellipse([lx, bar_y + 14, lx + 6, bar_y + 20], fill=lerp(BG_MID, color, 0.6))
        draw.text((lx + 10, bar_y + 10), label, font=font_label, fill=lerp(BG_MID, color, 0.5))

    # === Corner marks ===
    mark_c = lerp(BG_MID, SLATE, 0.1)
    for cx, cy in [(28, 28), (W - 28, 28), (28, H - 28), (W - 28, H - 28)]:
        draw.line([(cx - 5, cy), (cx + 5, cy)], fill=mark_c, width=1)
        draw.line([(cx, cy - 5), (cx, cy + 5)], fill=mark_c, width=1)

    # === Outer frame ===
    draw.rectangle([16, 16, W - 17, H - 17], outline=lerp(BG_MID, SLATE, 0.04), width=1)

    return img


if __name__ == "__main__":
    img = create_architecture()
    img.save("/home/ubuntu/hypebot-rs-showcase/assets/architecture.png", quality=95)
    print("Architecture diagram saved.")

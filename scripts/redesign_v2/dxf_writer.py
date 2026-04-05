#!/usr/bin/env python3
"""
大鱼TT 310 封箱 V2 — DXF 切割图生成器
Pure Python DXF generator for acrylic panel cutting
Output: DXF files ready for laser cutting
"""
import os

OUT_DIR = '/vol1/1000/projects/3d-printing/dayu-tt-all-in-one/enclosure/dxf_v2'
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# DXF CONSTANTS
# ============================================================
DXF_HEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  0
ENDSEC
  0
SECTION
  2
TABLES
  0
TABLE
  2
LAYER
 70
3
  0
LAYER
  2
CUT
 70
0
 62
1
  6
CONTINUOUS
  0
LAYER
  2
SCORE
 70
0
 62
3
  6
CONTINUOUS
  0
LAYER
  2
TEXT
 70
0
 62
7
  6
CONTINUOUS
  0
LAYER
  2
ORIGIN
 70
0
 62
4
  6
CONTINUOUS
  0
ENDSEC
  0
SECTION
  2
ENTITIES
"""

DXF_FOOTER = """  0
ENDSEC
  0
EOF
"""

def make_line(x1, y1, x2, y2, layer='CUT'):
    return f"  0\nLINE\n  8\n{layer}\n 10\n{x1:.3f}\n 20\n{y1:.3f}\n 30\n0.0\n 11\n{x2:.3f}\n 21\n{y2:.3f}\n 31\n0.0\n"

def make_rect(x, y, w, h, layer='CUT'):
    """Draw rectangle at (x,y) with width w, height h (lower-left corner)"""
    entities = []
    entities.append(make_line(x, y, x + w, y, layer))
    entities.append(make_line(x + w, y, x + w, y + h, layer))
    entities.append(make_line(x + w, y + h, x, y + h, layer))
    entities.append(make_line(x, y + h, x, y, layer))
    return ''.join(entities)

def make_circle(cx, cy, r, layer='CUT'):
    return f"  0\nCIRCLE\n  8\n{layer}\n 10\n{cx:.3f}\n 20\n{cy:.3f}\n 30\n0.0\n 40\n{r:.3f}\n"

def make_arc(cx, cy, r, start_angle, end_angle, layer='CUT'):
    return f"  0\nARC\n  8\n{layer}\n 10\n{cx:.3f}\n 20\n{cy:.3f}\n 30\n0.0\n 40\n{r:.3f}\n 50\n{start_angle:.3f}\n 51\n{end_angle:.3f}\n"

def make_text(x, y, text, height=3.0, layer='TEXT'):
    return f"  0\nTEXT\n  8\n{layer}\n 10\n{x:.3f}\n 20\n{y:.3f}\n 30\n0.0\n 40\n{height:.3f}\n  1\n{text}\n"

def write_dxf(filename, content):
    full = DXF_HEADER + content + DXF_FOOTER
    path = os.path.join(OUT_DIR, filename)
    with open(path, 'w') as f:
        f.write(full)
    print(f"  ✓ {filename}")

def panel_label(x, y, name, material, thickness, qty=1):
    """Generate text labels for a panel"""
    lines = []
    lines.append(make_text(x, y, name, height=5.0))
    lines.append(make_text(x, y - 6, f"{material} t={thickness}mm", height=3.0))
    lines.append(make_text(x, y - 10, f"QTY: {qty}", height=3.0))
    lines.append(make_text(x, y - 14, f"DAYU TT310 V2", height=2.5))
    return ''.join(lines)

# ============================================================
# PANEL DEFINITIONS
# Based on: STEP analysis + layout (760mm Z height)
# ============================================================

def gen_side_panel_x():
    """Side panel X2 — 520mm × 770mm — for left and right"""
    w, h = 520.0, 770.0
    t = 4.0
    content = ""
    
    # Main outline
    content += make_rect(0, 0, w, h)
    
    # Corner mounting holes (4× M3 for bottom brackets)
    corners = [(15, 15), (w - 15, 15), (15, h - 15), (w - 15, h - 15)]
    for cx, cy in corners:
        content += make_circle(cx, cy, 3.5)  # M3 clearance hole
    
    # Panel clip holes (along vertical edges, every 100mm from Z=100 to Z=700)
    for y in range(100, 700, 100):
        content += make_circle(10, y, 3.5)  # left edge
        content += make_circle(w - 10, y, 3.5)  # right edge
    
    # Ventilation pattern (optional, scored lines) — middle zone
    vent_x0, vent_x1 = w * 0.3, w * 0.7
    vent_y0, vent_y1 = h * 0.1, h * 0.5
    for y in range(int(vent_y0), int(vent_y1), 15):
        content += make_line(vent_x0, y, vent_x1, y, 'SCORE')
    
    # Cable entry hole (center-left, at Z=150mm from bottom)
    content += make_circle(80, 150, 20)  # main cable entry
    content += make_circle(80, 190, 7)   # auxiliary 1
    content += make_circle(80, 205, 6)   # auxiliary 2
    
    # Label
    content += panel_label(15, h - 20, "SIDE_PANEL_X2", "PMMA透明", f"{t}mm", qty=2)
    
    # Origin crosshair
    content += make_line(-5, 0, 5, 0, 'ORIGIN')
    content += make_line(0, -5, 0, 5, 'ORIGIN')
    
    write_dxf('SIDE_PANEL_X2_520x770x4.DXF', content)

def gen_side_panel_y():
    """Side panel Y2 — 530mm × 770mm — for front and back"""
    w, h = 530.0, 770.0
    t = 4.0
    content = ""
    
    content += make_rect(0, 0, w, h)
    
    # Corner holes
    corners = [(15, 15), (w - 15, 15), (15, h - 15), (w - 15, h - 15)]
    for cx, cy in corners:
        content += make_circle(cx, cy, 3.5)
    
    # Panel clip holes
    for y in range(100, 700, 100):
        content += make_circle(10, y, 3.5)
        content += make_circle(w - 10, y, 3.5)
    
    # Fan vent pattern (for top section, if needed)
    fan_cx, fan_cy = w / 2, h - 80
    content += make_circle(fan_cx, fan_cy, 60)  # 120mm fan cutout
    content += make_circle(fan_cx, fan_cy, 52.5)  # mounting holes circle
    
    # 4× fan mounting holes
    import math
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        fx = fan_cx + 52.5 * math.cos(rad)
        fy = fan_cy + 52.5 * math.sin(rad)
        content += make_circle(fx, fy, 1.75)  # M3 tap hole
    
    # Label
    content += panel_label(15, h - 20, "SIDE_PANEL_Y2", "PMMA透明", f"{t}mm", qty=2)
    
    write_dxf('SIDE_PANEL_Y2_530x770x4.DXF', content)

def gen_top_panel():
    """Top panel — 520mm × 530mm"""
    w, h = 520.0, 530.0
    t = 3.0
    content = ""
    
    content += make_rect(0, 0, w, h)
    
    # Corner mounting holes (4×)
    corners = [(15, 15), (w - 15, 15), (15, h - 15), (w - 15, h - 15)]
    for cx, cy in corners:
        content += make_circle(cx, cy, 3.5)
    
    # Panel clip holes around perimeter
    for x in range(50, int(w), 100):
        content += make_circle(x, 10, 3.5)
        content += make_circle(x, h - 10, 3.5)
    for y in range(50, int(h), 100):
        content += make_circle(10, y, 3.5)
        content += make_circle(w - 10, y, 3.5)
    
    # 120mm fan cutout (centered)
    fan_cx, fan_cy = w / 2, h / 2
    content += make_circle(fan_cx, fan_cy, 60)  # outer
    content += make_circle(fan_cx, fan_cy, 52.5)  # mounting circle
    
    import math
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        fx = fan_cx + 52.5 * math.cos(rad)
        fy = fan_cy + 52.5 * math.sin(rad)
        content += make_circle(fx, fy, 1.75)
    
    # Label
    content += panel_label(15, h - 20, "TOP_PANEL", "PMMA透明", f"{t}mm", qty=1)
    
    write_dxf('TOP_PANEL_520x530x3.DXF', content)

def gen_bottom_panel():
    """Bottom panel — 520mm × 530mm × 5mm (reinforced)"""
    w, h = 520.0, 530.0
    t = 5.0
    content = ""
    
    content += make_rect(0, 0, w, h)
    
    # Corner holes for bottom brackets
    corners = [(15, 15), (w - 15, 15), (15, h - 15), (w - 15, h - 15)]
    for cx, cy in corners:
        content += make_circle(cx, cy, 3.5)
    
    # Bottom bracket mounting holes (at 2020 frame positions)
    # Frame is at X=20, X=w-20, Y=20, Y=h-20
    frame_x = [20.0, w - 20.0]
    frame_y = [20.0, h - 20.0]
    for fx in frame_x:
        for fy in frame_y:
            # M3 bolt holes for bracket
            for dx in [-12, 0, 12]:
                for dy in [-8, 0, 8]:
                    content += make_circle(fx + dx, fy + dy, 1.5)
    
    # Cable entry holes
    content += make_circle(80, 80, 20)
    content += make_circle(80, 115, 7)
    content += make_circle(80, 128, 6)
    
    # Ventilation slots (bottom edge)
    for i in range(4):
        x = 150 + i * 60
        content += make_rect(x, 0, 40, 5)  # intake slots
    
    # Label
    content += panel_label(15, h - 20, "BOTTOM_PANEL", "PMMA透明", f"{t}mm(加厚)", qty=1)
    
    write_dxf('BOTTOM_PANEL_520x530x5.DXF', content)

def gen_back_panel():
    """Back panel — 530mm × 770mm"""
    w, h = 530.0, 770.0
    t = 3.0
    content = ""
    
    content += make_rect(0, 0, w, h)
    
    # Corner holes
    corners = [(15, 15), (w - 15, 15), (15, h - 15), (w - 15, h - 15)]
    for cx, cy in corners:
        content += make_circle(cx, cy, 3.5)
    
    # Panel clip holes
    for y in range(100, 700, 100):
        content += make_circle(10, y, 3.5)
        content += make_circle(w - 10, y, 3.5)
    
    # Power connector hole (lower right)
    content += make_circle(w - 80, 80, 20)
    
    # Data cable hole
    content += make_circle(w - 80, 120, 12)
    
    # Exhaust fan hole (optional upper right)
    content += make_circle(w - 80, h - 80, 40)
    
    # Label
    content += panel_label(15, h - 20, "BACK_PANEL", "PMMA透明", f"{t}mm", qty=1)
    
    write_dxf('BACK_PANEL_530x770x3.DXF', content)

def gen_front_door():
    """Front door panel — 520mm × 745mm × 5mm"""
    w, h = 520.0, 745.0
    t = 5.0
    content = ""
    
    content += make_rect(0, 0, w, h)
    
    # Hinge cutouts (left side, 3×)
    hinge_x = 15  # X position on left edge
    hinge_y_positions = [120, h / 2, h - 120]
    for hy in hinge_y_positions:
        # Hinge hole (rectangular cutout)
        content += make_rect(hinge_x - 5, hy - 15, 15, 30)
        # Hinge pin hole
        content += make_circle(hinge_x - 5, hy, 3)
    
    # Magnet holder holes (right side, 3 pairs)
    magnet_x = w - 15
    magnet_y_positions = [150, h / 2, h - 150]
    for mhy in magnet_y_positions:
        # Magnet recess hole
        content += make_circle(magnet_x, mhy, 7)
        content += make_circle(magnet_x, mhy, 5)  # inner (magnet)
    
    # Handle cutout (center right)
    handle_x = w * 0.85
    handle_y = h / 2
    content += make_rect(handle_x - 5, handle_y - 30, 10, 60)
    
    # Panel clip holes (top and bottom)
    for x in range(50, int(w - 50), 80):
        content += make_circle(x, 10, 3.5)
        content += make_circle(x, h - 10, 3.5)
    
    # Label
    content += panel_label(15, h - 20, "FRONT_DOOR", "PMMA透明", f"{t}mm(加厚)", qty=1)
    content += make_text(15, 20, "← 铰链侧", height=4.0)
    
    write_dxf('FRONT_DOOR_520x745x5.DXF', content)

def gen_door_handle():
    """Door handle — 3D print file (STL), but provide DXF outline"""
    w, h = 80.0, 30.0
    content = ""
    
    # Outer profile
    content += make_rect(0, 0, w, h)
    
    # Mounting holes (2× M3)
    content += make_circle(12, h / 2, 1.75)
    content += make_circle(w - 12, h / 2, 1.75)
    
    # Label
    content += make_text(5, h + 5, "DOOR_HANDLE", height=3.0)
    
    write_dxf('DOOR_HANDLE_OUTLINE.DXF', content)

if __name__ == '__main__':
    print("=" * 60)
    print("大鱼TT 310 封箱 V2 — DXF 切割图生成")
    print(f"输出目录: {OUT_DIR}")
    print("=" * 60)
    
    gen_side_panel_x()
    gen_side_panel_y()
    gen_top_panel()
    gen_bottom_panel()
    gen_back_panel()
    gen_front_door()
    gen_door_handle()
    
    print("\n" + "=" * 60)
    print("✓ 全部 7 张 DXF 切割图已生成!")
    print(f"  目录: {OUT_DIR}")
    print("=" * 60)

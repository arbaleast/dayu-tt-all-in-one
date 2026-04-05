#!/usr/bin/env python3
"""
大鱼TT310 皮带张紧机构 V2 — 纯 Python STL 生成器
方案A: 弹簧臂式（偏心轮张紧）
方案B: 滑轨调节式

设计参数:
  - GT2 20齿皮带轮 (节圆直径 36.5mm)
  - 5mm GT2 同步带
  - 624ZZ 轴承 (内径4mm, 外径16mm)
  - Nema17 电机 (42mm方形, 轴径5.5mm)
  - M3/M4 螺丝标准孔位
  - PETG 打印件, 4mm壁厚
"""
import struct
import math
import os
import numpy as np

OUT_DIR = '/vol1/1000/projects/3d-printing/dayu-tt-all-in-one/enclosure/stl_v2'
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# GEOMETRY PRIMITIVES
# ============================================================

def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-9:
        return v
    return v / n

def triangle(norm, v0, v1, v2):
    return (np.array(norm, dtype=np.float32),
            np.array(v0, dtype=np.float32),
            np.array(v1, dtype=np.float32),
            np.array(v2, dtype=np.float32))

def cylinder_mesh(cx, cy, cz, r, h, segments=32, cap=True):
    """Cylinder mesh. Returns list of triangles."""
    tris = []
    h0 = cz
    h1 = cz + h
    for i in range(segments):
        a0 = 2 * math.pi * i / segments
        a1 = 2 * math.pi * (i + 1) / segments
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        n = normalize(np.array([math.cos((a0+a1)/2), math.sin((a0+a1)/2), 0]))
        tris.append(triangle(n, [x0,y0,h0],[x1,y1,h0],[x0,y0,h1]))
        tris.append(triangle(n, [x1,y1,h0],[x1,y1,h1],[x0,y0,h1]))
        if cap:
            tris.append(triangle([0,0,-1], [cx,cy,h0],[x1,y1,h0],[x0,y0,h0]))
            tris.append(triangle([0,0,1],  [cx,cy,h1],[x0,y0,h1],[x1,y1,h1]))
    return tris

def cylinder_ring_mesh(cx, cy, cz, r_outer, r_inner, h, segments=32):
    """Hollow cylinder (ring/washer)."""
    tris = []
    h0 = cz
    h1 = cz + h
    for i in range(segments):
        a0 = 2 * math.pi * i / segments
        a1 = 2 * math.pi * (i + 1) / segments
        # Outer wall
        ox0, oy0 = cx + r_outer * math.cos(a0), cy + r_outer * math.sin(a0)
        ox1, oy1 = cx + r_outer * math.cos(a1), cy + r_outer * math.sin(a1)
        on = normalize(np.array([math.cos((a0+a1)/2), math.sin((a0+a1)/2), 0]))
        tris.append(triangle(on, [ox0,oy0,h0],[ox1,oy1,h0],[ox0,oy0,h1]))
        tris.append(triangle(on, [ox1,oy1,h0],[ox1,oy1,h1],[ox0,oy0,h1]))
        # Inner wall
        ix0, iy0 = cx + r_inner * math.cos(a0), cy + r_inner * math.sin(a0)
        ix1, iy1 = cx + r_inner * math.cos(a1), cy + r_inner * math.sin(a1)
        inn = normalize(np.array([-math.cos((a0+a1)/2), -math.sin((a0+a1)/2), 0]))
        tris.append(triangle(inn, [ix0,iy0,h0],[ix0,iy0,h1],[ix1,iy1,h0]))
        tris.append(triangle(inn, [ix1,iy1,h0],[ix0,iy0,h1],[ix1,iy1,h1]))
        # Bottom annular face
        tris.append(triangle([0,0,-1], [ox0,oy0,h0],[ix0,iy0,h0],[ox1,oy1,h0]))
        tris.append(triangle([0,0,-1], [ox1,oy1,h0],[ix0,iy0,h0],[ix1,iy1,h0]))
        # Top annular face
        tris.append(triangle([0,0,1],  [ox0,oy0,h1],[ix0,iy0,h1],[ox1,oy1,h1]))
        tris.append(triangle([0,0,1],  [ox1,oy1,h1],[ix0,iy0,h1],[ix1,iy1,h1]))
    return tris

def box_mesh(cx, cy, cz, w, d, h):
    """Solid box centered at (cx,cy,cz)."""
    tris = []
    x0, y0, z0 = cx - w/2, cy - d/2, cz - h/2
    x1, y1, z1 = cx + w/2, cy + d/2, cz + h/2
    # Front (+Y)
    tris.append(triangle([0,1,0],[x0,y1,z0],[x1,y1,z0],[x0,y1,z1]))
    tris.append(triangle([0,1,0],[x1,y1,z0],[x1,y1,z1],[x0,y1,z1]))
    # Back (-Y)
    tris.append(triangle([0,-1,0],[x1,y0,z0],[x0,y0,z0],[x1,y0,z1]))
    tris.append(triangle([0,-1,0],[x0,y0,z0],[x0,y0,z1],[x1,y0,z1]))
    # Right (+X)
    tris.append(triangle([1,0,0],[x1,y0,z0],[x1,y1,z0],[x1,y0,z1]))
    tris.append(triangle([1,0,0],[x1,y1,z0],[x1,y1,z1],[x1,y0,z1]))
    # Left (-X)
    tris.append(triangle([-1,0,0],[x0,y1,z0],[x0,y0,z0],[x0,y1,z1]))
    tris.append(triangle([-1,0,0],[x0,y0,z0],[x0,y0,z1],[x0,y1,z1]))
    # Top (+Z)
    tris.append(triangle([0,0,1],[x0,y0,z1],[x1,y0,z1],[x0,y1,z1]))
    tris.append(triangle([0,0,1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]))
    # Bottom (-Z)
    tris.append(triangle([0,0,-1],[x0,y0,z0],[x0,y1,z0],[x1,y0,z1]))
    tris.append(triangle([0,0,-1],[x0,y1,z0],[x1,y1,z0],[x1,y0,z1]))
    return tris

def cone_mesh(cx, cy, cz, r_base, r_top, h, segments=32):
    """Cone or frustum."""
    tris = []
    h0, h1 = cz, cz + h
    for i in range(segments):
        a0 = 2 * math.pi * i / segments
        a1 = 2 * math.pi * (i + 1) / segments
        xb0, yb0 = cx + r_base*math.cos(a0), cy + r_base*math.sin(a0)
        xb1, yb1 = cx + r_base*math.cos(a1), cy + r_base*math.sin(a1)
        xt0, yt0 = cx + r_top*math.cos(a0),  cy + r_top*math.sin(a0)
        xt1, yt1 = cx + r_top*math.cos(a1),  cy + r_top*math.sin(a1)
        slope = (r_base - r_top) / math.sqrt((r_base - r_top)**2 + h**2 + 1e-9)
        n = normalize(np.array([math.cos((a0+a1)/2), math.sin((a0+a1)/2), slope]))
        tris.append(triangle(n,[xb0,yb0,h0],[xb1,yb1,h0],[xt0,yt0,h1]))
        tris.append(triangle(n,[xb1,yb1,h0],[xt1,yt1,h1],[xt0,yt0,h1]))
        if r_base > 0.1:
            tris.append(triangle([0,0,-1],[cx,cy,h0],[xb1,yb1,h0],[xb0,yb0,h0]))
        if r_top > 0.1:
            tris.append(triangle([0,0,1],[cx,cy,h1],[xt0,yt0,h1],[xb0,yb0,h1]))
            tris.append(triangle([0,0,1],[cx,cy,h1],[xb0,yb0,h1],[xt0,yt0,h1]))
    return tris

def torus_mesh(cx, cy, cz, r_tube, r_path, segments_t=16, segments_p=32):
    """Torus (donut). r_tube = tube radius, r_path = path radius."""
    tris = []
    for i in range(segments_p):
        p0 = 2 * math.pi * i / segments_p
        p1 = 2 * math.pi * (i + 1) / segments_p
        for j in range(segments_t):
            t0 = 2 * math.pi * j / segments_t
            t1 = 2 * math.pi * (j + 1) / segments_t
            # 4 points on the tube cross-section
            def pt(phi, theta):
                return np.array([
                    cx + (r_path + r_tube*math.cos(theta))*math.cos(phi),
                    cy + (r_path + r_tube*math.cos(theta))*math.sin(phi),
                    cz + r_tube*math.sin(theta)
                ], dtype=np.float32)
            v00 = pt(p0, t0); v10 = pt(p1, t0)
            v01 = pt(p0, t1); v11 = pt(p1, t1)
            n = normalize(v00 - np.array([cx,cy,cz]))
            tris.append(triangle(n, v00, v10, v01))
            tris.append(triangle(n, v10, v11, v01))
    return tris

def write_stl_binary(filename, tris, name='part'):
    """Write binary STL, filtering out NaN/Infinity."""
    valid = []
    for norm, v0, v1, v2 in tris:
        if not (math.isnan(v0[0]) or math.isinf(v0[0]) or
                math.isnan(v1[0]) or math.isinf(v1[0]) or
                math.isnan(v2[0]) or math.isinf(v2[0])):
            valid.append((norm, v0, v1, v2))
    tris = valid
    with open(filename, 'wb') as f:
        f.write(b'OPENCLAW DAYU TT310 BELT TENSIONER V2' + b'\x00' * (80 - 46))
        f.write(struct.pack('<I', len(tris)))
        for norm, v0, v1, v2 in tris:
            f.write(struct.pack('<3f', *norm))
            f.write(struct.pack('<3f', *v0))
            f.write(struct.pack('<3f', *v1))
            f.write(struct.pack('<3f', *v2))
            f.write(struct.pack('<H', 0))
    print(f"  ✓ {os.path.basename(filename)} ({len(tris)} tris)")

def union(*mesh_lists):
    result = []
    for ml in mesh_lists:
        result += ml
    return result

# ============================================================
# DESIGN PARAMETERS
# ============================================================
# Belt / Pulley
GT2_PULLEY_PD   = 36.5   # GT2 20T 节圆直径 mm
GT2_BELT_W      = 5.0    # 5mm 宽同步带
GT2_TOOTH_H     = 0.75   # GT2 齿高 mm

# 624ZZ bearing
BEARING_OD  = 16.0
BEARING_ID  = 4.0
BEARING_H   = 5.0

# Eccentric sleeve for idler (presses belt)
ECCENTRIC_OFFSET = 2.0   # 偏心距 mm (idler pressed into belt by this amount)
ECCENTRIC_BORE   = 5.0   # 偏心轴孔径 mm (fits M5 bolt = 5mm)

# Nema17 motor mount
NEMA17_BODY   = 42.0   # 机身尺寸 mm
NEMA17_SHAFT  = 5.5    # 轴径 mm
M3_HOLE_D     = 3.0    # M3 螺纹底孔
M4_HOLE_D     = 4.0    # M4 螺纹底孔
M3_CSK_D      = 6.0    # M3 沉头直径
M3_CSK_DEPTH  = 2.5    # M3 沉头深度
MOTOR_HOLE_SPACING = 31.0  # 电机螺丝孔距 mm

# Wall thickness
WALL = 4.0   # 4mm 壁厚

# Idler pulley dimensions (printed, runs on bearing)
IDLER_OD      = 24.0   # 外径 (belt track)
IDLER_BORE_D  = 10.0   # 轴承孔径 (fits 624ZZ outer = 16, but we use eccentric sleeve)
IDLER_H       = 6.0    # 宽度 (belt width + flanges)

# Spring arm dimensions
ARM_LENGTH  = 40.0   # 臂长
ARM_WIDTH    = 12.0   # 臂宽
ARM_THICK    = 8.0    # 臂厚
PIVOT_BORE_D = 8.0    # 枢轴孔 (spherical bearing or pivot)
SPRING_POST_D = 10.0  # 弹簧安装柱

# Tensioning screw
SCREW_M4_L   = 20.0   # M4 调节螺丝长度

# ============================================================
# PART A1: 偏心轮/idler wheel (带GT2皮带槽)
# ============================================================
def make_tensioner_A_idler():
    """方案A: 偏心轮 — 带GT2皮带槽的惰轮
    安装在624ZZ轴承上，偏心套筒驱动
    """
    print("[A1/6] TensionerA_Idler (偏心轮)...", flush=True)
    tris = []

    # GT2皮带槽参数
    # 节圆半径 = GT2_PULLEY_PD/2 = 18.25mm
    # 皮带宽度 5mm, 齿高 0.75mm
    # 槽顶直径 ≈ 节圆 + 2*0.75 = 19.75mm
    # 槽底直径 ≈ 节圆 - 2*0.75 = 16.75mm
    groove_r_top = GT2_PULLEY_PD/2 + GT2_TOOTH_H   # ~19.75
    groove_r_bot = GT2_PULLEY_PD/2 - GT2_TOOTH_H  # ~16.75
    groove_r_mid = GT2_PULLEY_PD/2                 # ~18.25

    WHEEL_OD   = 28.0   # 总外径 (含法兰)
    WHEEL_H    = IDLER_H  # 6mm
    FLANGE_H   = 1.5    # 法兰高
    HUB_OD     = 14.0   # 轮毂外径
    HUB_H      = WHEEL_H + FLANGE_H

    # --- 外圈主体 (圆柱) ---
    tris += cylinder_mesh(0, 0, 0, WHEEL_OD/2, WHEEL_H, segments=48)

    # --- 顶部法兰 ---
    tris += cylinder_mesh(0, 0, WHEEL_H, WHEEL_OD/2, FLANGE_H, segments=48)

    # --- 底部法兰 ---
    tris += cylinder_mesh(0, 0, -FLANGE_H/2, WHEEL_OD/2, FLANGE_H, segments=48)

    # --- 轮毂 (中心凸台, 无孔 — 偏心套筒包在外面) ---
    tris += cylinder_mesh(ECCENTRIC_OFFSET, 0, 0, HUB_OD/2, HUB_H, segments=24)

    # --- 偏心套筒 (套在轮毂外面, 提供偏心轴承孔) ---
    # 偏心套筒 = 圆环, 中心在 (ECCENTRIC_OFFSET, 0)
    # 内孔 = BEARING_OD/2 + 过盈 ≈ 8.2mm  (压装轴承)
    ECCENTRIC_SLEEVE_OD = 22.0
    ECCENTRIC_SLEEVE_ID = BEARING_OD/2 + 0.3   # 8.3mm (轴承外圈压入)
    ECCENTRIC_SLEEVE_H  = BEARING_H + 1.0      # 6mm
    sleeve_cx = ECCENTRIC_OFFSET   # 偏心2mm
    tris += cylinder_ring_mesh(sleeve_cx, 0, 0,
                                ECCENTRIC_SLEEVE_OD/2,
                                ECCENTRIC_SLEEVE_ID,
                                ECCENTRIC_SLEEVE_H,
                                segments=32)
    # 注意: 这里偏心套筒几何中心在 (ECCENTRIC_OFFSET, 0)
    # 实际轴承孔轴线也在 (ECCENTRIC_OFFSET, 0), 相对于轮毂中心 (0,0) 偏心 2mm

    # --- 中心轴孔 (非偏心, 用于固定偏心套筒) ---
    # 在 (0,0) 处做一个轴向孔, 用 ring 表示壁厚
    CENTER_AXLE_R = 3.0  # M3 螺丝孔
    tris += cylinder_ring_mesh(0, 0, 0,
                                HUB_OD/2 - 1.0,  # 内壁
                                CENTER_AXLE_R,
                                HUB_H + FLANGE_H*2,
                                segments=20)

    # --- 皮带槽视觉 (在侧面开槽, 用窄圆柱近似) ---
    # 皮带槽 = 凹槽绕外圈, 简化表示为细圆柱
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        gx = (groove_r_mid) * math.cos(rad)
        gy = (groove_r_mid) * math.sin(rad)
        tris += cylinder_mesh(gx, gy, 0, 0.8, WHEEL_H + FLANGE_H*2 + 0.4, segments=8)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerA_Idler.stl'), tris, 'TensionerA_Idler')
    print(f"  ✓ TensionerA_Idler.stl 生成完成")

# ============================================================
# PART A2: 弹簧臂 (Spring Arm) — 枢轴安装座 + 弹簧挂柱
# ============================================================
def make_tensioner_A_arm():
    """方案A: 弹簧臂 — 枢轴轴承座 + 弹簧安装柱 + 调节螺丝孔
    臂长 40mm, 宽12mm, 厚8mm
    枢轴端安装624ZZ, 张紧端安装弹簧+螺丝
    """
    print("[A2/6] TensionerA_Arm (弹簧臂)...", flush=True)
    tris = []

    # --- 主体 (矩形臂) ---
    # 臂从枢轴端向张紧端延伸
    # 枢轴端在 x=0, 张紧端在 x=ARM_LENGTH
    tris += box_mesh(ARM_LENGTH/2, 0, 0, ARM_LENGTH, ARM_WIDTH, ARM_THICK)

    # --- 枢轴端轴承座 (臂末端, 左侧) ---
    # 枢轴轴承 = 624ZZ, 外径16, 高5
    PIVOT_X = 0   # 枢轴在臂左端
    PIVOT_HOUSING_OD = BEARING_OD + 2*WALL   # 16 + 8 = 24mm
    PIVOT_HOUSING_H  = BEARING_H + 2*WALL    # 5 + 8 = 13mm
    tris += cylinder_mesh(PIVOT_X, 0, -ARM_THICK/2 - PIVOT_HOUSING_H/2,
                           PIVOT_HOUSING_OD/2, PIVOT_HOUSING_H, segments=24)
    # 枢轴孔 (贯穿臂厚)
    tris += cylinder_mesh(PIVOT_X, 0, 0,
                           PIVOT_HOUSING_OD/2 - WALL,
                           ARM_THICK + 2,
                           segments=24)
    # 轴承座沉台 (臂上方)
    tris += cylinder_mesh(PIVOT_X, 0, ARM_THICK/2,
                           PIVOT_HOUSING_OD/2, WALL, segments=24)

    # --- 张紧端 (臂右端) — 弹簧挂柱 + 调节螺丝孔 ---
    TENSION_X = ARM_LENGTH   # 臂右端
    # 弹簧挂柱 (臂上方)
    tris += cylinder_mesh(TENSION_X, 0, ARM_THICK/2 + SPRING_POST_D/2,
                            SPRING_POST_D/2, SPRING_POST_D, segments=16)
    # M4 调节螺丝孔 (臂下方, 推压用)
    tris += cylinder_mesh(TENSION_X, 0, -ARM_THICK/2 - SCREW_M4_L/2,
                           M4_HOLE_D/2, SCREW_M4_L, segments=12)

    # --- 中间加强肋 ---
    for rib_x in [ARM_LENGTH*0.33, ARM_LENGTH*0.66]:
        tris += box_mesh(rib_x, 0, 0, 3, ARM_WIDTH - 2, ARM_THICK - 1)

    # --- 臂侧面倒角 (简化: 小box) ---
    for side in [-1, 1]:
        tris += box_mesh(ARM_LENGTH/2, side * (ARM_WIDTH/2 + 1.5), 0,
                          ARM_LENGTH, 3, ARM_THICK - 2)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerA_Arm.stl'), tris, 'TensionerA_Arm')
    print(f"  ✓ TensionerA_Arm.stl 生成完成")

# ============================================================
# PART A3: 枢轴安装座 (Pivot Mount) — 安装在电机支架上
# ============================================================
def make_tensioner_A_base():
    """方案A: 底座 — 安装在原电机支架位置
    包含:
    - 4×M3 螺丝孔 (31mm间距, 兼容Nema17)
    - 弹簧臂枢轴轴承座
    - 弹簧安装柱
    - M4调节螺丝孔
    - 皮带导轨槽
    """
    print("[A3/6] TensionerA_Base (底座/电机座)...", flush=True)
    tris = []

    BASE_W = 55.0   # 总宽
    BASE_D = 20.0   # 总深
    BASE_H = 16.0   # 总高 (也是臂的活动行程)
    WALL_T = WALL   # 4mm

    # --- 主体箱体 ---
    tris += box_mesh(0, 0, 0, BASE_W, BASE_D, BASE_H)

    # --- 电机安装孔 (4×M3, 31mm间距) ---
    # 电机孔距31mm, 4个孔在正方形角上
    hole_r = M3_HOLE_D / 2
    for hx, hy in [(-MOTOR_HOLE_SPACING/2, -MOTOR_HOLE_SPACING/2),
                    ( MOTOR_HOLE_SPACING/2, -MOTOR_HOLE_SPACING/2),
                    (-MOTOR_HOLE_SPACING/2,  MOTOR_HOLE_SPACING/2),
                    ( MOTOR_HOLE_SPACING/2,  MOTOR_HOLE_SPACING/2)]:
        # 沉头孔 (顶面)
        tris += cylinder_mesh(hx, hy, BASE_H/2,
                               M3_CSK_D/2, M3_CSK_DEPTH, segments=16)
        # 光孔 (向下延伸)
        tris += cylinder_mesh(hx, hy, BASE_H/2 - M3_CSK_DEPTH,
                               hole_r, BASE_H/2 + M3_CSK_DEPTH + 2,
                               segments=12)

    # --- 枢轴轴承座 (左侧, 臂的旋转中心) ---
    PIVOT_X = -BASE_W/2 + 16   # 枢轴在底座左侧
    PIVOT_BORE_R = BEARING_OD/2 + WALL_T   # 轴承外壳半径 = 8+4=12
    PIVOT_BORE_H = BEARING_H + 2*WALL_T    # 13mm
    tris += cylinder_mesh(PIVOT_X, 0, BASE_H/2 + PIVOT_BORE_H/2,
                           PIVOT_BORE_R, PIVOT_BORE_H, segments=24)
    # 枢轴孔 (贯穿)
    tris += cylinder_mesh(PIVOT_X, 0, BASE_H/2 + PIVOT_BORE_H/2,
                           PIVOT_BORE_R - WALL_T, PIVOT_BORE_H + 2,
                           segments=24)

    # --- 弹簧安装柱 (底座内部, 右侧) ---
    SPRING_POST_X = BASE_W/2 - 14   # 弹簧柱 x 位置
    SPRING_POST_H = 12.0
    tris += cylinder_mesh(SPRING_POST_X, 0, BASE_H/2 + SPRING_POST_H/2,
                            SPRING_POST_D/2, SPRING_POST_H, segments=16)

    # --- M4 调节螺丝孔 (右侧, 水平方向) ---
    SCREW_X = BASE_W/2 - 6
    tris += cylinder_mesh(SCREW_X, 0, BASE_H/2 - 3,
                           M4_HOLE_D/2, BASE_W, segments=12)
    # 螺丝沉头 (右侧端面)
    tris += cylinder_mesh(SCREW_X + BASE_W/2, 0, BASE_H/2 - 3,
                           M4_HOLE_D/2 + 2, 3, segments=12)

    # --- 皮带导轨槽 (底部) ---
    # 皮带通路: 底座中部开槽, 让皮带通过
    tris += box_mesh(0, 0, -BASE_H/2 - 1,
                      GT2_PULLEY_PD + 10, GT2_BELT_W + 4, 4)

    # --- 安装法兰 (底座两侧) ---
    FLANGE_W = 8.0
    FLANGE_H_L = BASE_H + 8
    FLANGE_D = 6.0
    tris += box_mesh(-BASE_W/2 - FLANGE_W/2, 0, FLANGE_H_L/2 - BASE_H/2,
                      FLANGE_W, BASE_D + FLANGE_D*2, FLANGE_H_L)
    tris += box_mesh( BASE_W/2 + FLANGE_W/2, 0, FLANGE_H_L/2 - BASE_H/2,
                      FLANGE_W, BASE_D + FLANGE_D*2, FLANGE_H_L)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerA_Base.stl'), tris, 'TensionerA_Base')
    print(f"  ✓ TensionerA_Base.stl 生成完成")

# ============================================================
# PART A4: 偏心轴套 (Eccentric Sleeve) — 连接idler和臂
# ============================================================
def make_tensioner_A_eccentric_sleeve():
    """方案A: 偏心轴套 — 轴向固定624ZZ, 径向偏心2mm
    这是一个简单的圆环, 安装在臂的枢轴孔中
    """
    print("[A4/6] TensionerA_EccentricSleeve (偏心套筒)...", flush=True)
    tris = []

    # 偏心套筒: 内孔偏心, 外圆与臂的枢轴孔同轴
    # 臂枢轴孔 = 12mm直径 (BEARING_OD + 2*WALL = 16+8=24, 缩为12)
    SLEEVE_ID   = BEARING_ID + 0.2   # 4.2mm (M4 螺丝穿过)
    SLEEVE_OD   = 10.0               # 外径
    SLEEVE_H    = 8.0                # 高度
    ECC_OFFSET  = 2.0                # 偏心距

    # 外圆 (同轴)
    tris += cylinder_mesh(0, 0, 0, SLEEVE_OD/2, SLEEVE_H, segments=24)
    # 内孔偏心 (简化为壁厚不均匀的环)
    tris += cylinder_ring_mesh(0, 0, 0,
                                 SLEEVE_OD/2 + 0.01,  # 实际外圆同轴
                                 SLEEVE_ID,
                                 SLEEVE_H,
                                 segments=24)
    # 偏心视觉: 另一侧加一块表示偏心厚度
    tris += cylinder_mesh(ECC_OFFSET, 0, 0,
                            SLEEVE_OD/2 - 1, SLEEVE_H, segments=24)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerA_EccentricSleeve.stl'), tris, 'TensionerA_EccentricSleeve')
    print(f"  ✓ TensionerA_EccentricSleeve.stl 生成完成")

# ============================================================
# PART B1: 滑轨调节式 — 滑块底座 (Slider Base)
# ============================================================
def make_tensioner_B_base():
    """方案B: 底座 — 滑轨结构
    主体是一块开槽的安装板, 滑块在槽内移动
    """
    print("[B1/6] TensionerB_Base (滑轨底座)...", flush=True)
    tris = []

    BASE_W = 60.0
    BASE_D = 22.0
    BASE_H = 12.0
    SLOT_W = 16.0   # 滑槽宽度
    SLOT_D = 8.0    # 滑槽深度

    # --- 主体 ---
    tris += box_mesh(0, 0, 0, BASE_W, BASE_D, BASE_H)

    # --- 滑槽 (中央贯通槽) ---
    # 用细长box表示槽, 槽壁为4mm
    SLOT_LEN = BASE_W - 16
    SLOT_X = 0
    SLOT_TOP_Z = BASE_H/2 + 0.1
    # 槽底部开放 (用薄壁近似 — 两侧墙 + 底板)
    wall_t = WALL
    tris += box_mesh(SLOT_X, 0, SLOT_TOP_Z - SLOT_D/2,
                      SLOT_LEN, wall_t, SLOT_D)  # 底板
    tris += box_mesh(SLOT_X, BASE_D/2 - wall_t/2, SLOT_TOP_Z - SLOT_D/2,
                      SLOT_LEN, wall_t, SLOT_D)  # 前壁
    tris += box_mesh(SLOT_X, -BASE_D/2 + wall_t/2, SLOT_TOP_Z - SLOT_D/2,
                      SLOT_LEN, wall_t, SLOT_D)  # 后壁

    # --- 滑块限位块 (槽两端) ---
    tris += box_mesh(-BASE_W/2 + 8, 0, SLOT_TOP_Z - SLOT_D/2,
                      6, BASE_D - 4, SLOT_D + 1)
    tris += box_mesh( BASE_W/2 - 8, 0, SLOT_TOP_Z - SLOT_D/2,
                      6, BASE_D - 4, SLOT_D + 1)

    # --- 电机安装孔 (4×M3) ---
    for hx, hy in [(-MOTOR_HOLE_SPACING/2, -MOTOR_HOLE_SPACING/2),
                    ( MOTOR_HOLE_SPACING/2, -MOTOR_HOLE_SPACING/2),
                    (-MOTOR_HOLE_SPACING/2,  MOTOR_HOLE_SPACING/2),
                    ( MOTOR_HOLE_SPACING/2,  MOTOR_HOLE_SPACING/2)]:
        tris += cylinder_mesh(hx, hy, BASE_H/2,
                               M3_CSK_D/2, M3_CSK_DEPTH, segments=16)
        tris += cylinder_mesh(hx, hy, BASE_H/2 - M3_CSK_DEPTH,
                               M3_HOLE_D/2, BASE_H/2 + M3_CSK_DEPTH + 2,
                               segments=12)

    # --- 调节螺丝 (M4, 贯穿底座右侧) ---
    tris += cylinder_mesh(BASE_W/2 + 2, 0, BASE_H/2 - 4,
                           M4_HOLE_D/2, BASE_W + 6, segments=12)

    # --- 安装法兰 ---
    tris += box_mesh(-BASE_W/2 - 5, 0, BASE_H/2 + 3,
                      10, BASE_D + 8, 6)
    tris += box_mesh( BASE_W/2 + 5, 0, BASE_H/2 + 3,
                      10, BASE_D + 8, 6)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerB_Base.stl'), tris, 'TensionerB_Base')
    print(f"  ✓ TensionerB_Base.stl 生成完成")

# ============================================================
# PART B2: 滑块 (Slider) — 在底座槽内滑动
# ============================================================
def make_tensioner_B_slider():
    """方案B: 滑块 — 放入底座槽内, 轴承安装在上面"""
    print("[B2/6] TensionerB_Slider (滑块)...", flush=True)
    tris = []

    SL_W = 20.0    # 滑块宽
    SLOT_W = 16.0
    SL_D = SLOT_W - 0.4  # 配合滑槽
    SL_H = 12.0

    # --- 主体滑块 ---
    tris += box_mesh(0, 0, 0, SL_W, SL_D, SL_H)

    # --- 轴承安装柱 (顶部, 安装624ZZ) ---
    # 轴承安装高度: 让轴承面略高于底座顶面
    BRG_POST_X = 0
    BRG_POST_OD = BEARING_OD + 2*WALL  # 24mm
    BRG_POST_H  = 10.0
    tris += cylinder_mesh(BRG_POST_X, 0, SL_H/2 + BRG_POST_H/2,
                           BRG_POST_OD/2, BRG_POST_H, segments=24)
    # 轴承孔 (贯穿)
    tris += cylinder_mesh(BRG_POST_X, 0, SL_H/2 + BRG_POST_H/2,
                           (BRG_POST_OD - 2*WALL)/2, BRG_POST_H + 2,
                           segments=24)

    # --- 滑块指捏槽 (两侧) ---
    for side in [-1, 1]:
        tris += box_mesh(0, side * (SL_D/2 + 2), SL_H/2 - 3,
                          SL_W - 6, 4, 4)

    # --- 弹簧挂柱 (滑块前端) ---
    tris += cylinder_mesh(SL_W/2 - 3, 0, SL_H/2 + 5,
                            SPRING_POST_D/2, 8, segments=12)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerB_Slider.stl'), tris, 'TensionerB_Slider')
    print(f"  ✓ TensionerB_Slider.stl 生成完成")

# ============================================================
# PART B3: 滑轨式惰轮 (B Idler)
# ============================================================
def make_tensioner_B_idler():
    """方案B: 惰轮 — 光轮(无偏心), 直接压在轴承上
    轮径略大于GT2 pulley, 压在皮带上提供张紧力
    """
    print("[B3/6] TensionerB_Idler (滑轨惰轮)...", flush=True)
    tris = []

    WHEEL_OD = 26.0
    WHEEL_H  = 6.0
    FLANGE_H = 1.5
    HUB_OD   = 12.0
    HUB_H    = WHEEL_H + FLANGE_H*2

    # 外圈
    tris += cylinder_mesh(0, 0, 0, WHEEL_OD/2, WHEEL_H, segments=48)
    tris += cylinder_mesh(0, 0, WHEEL_H, WHEEL_OD/2, FLANGE_H, segments=48)
    tris += cylinder_mesh(0, 0, -FLANGE_H/2, WHEEL_OD/2, FLANGE_H, segments=48)
    # 轮毂
    tris += cylinder_mesh(0, 0, 0, HUB_OD/2, HUB_H, segments=24)
    # 轴承孔 (同心, 压装624ZZ)
    tris += cylinder_ring_mesh(0, 0, 0,
                                 HUB_OD/2 - 2, BEARING_OD/2 + 0.3,
                                 HUB_H + 1, segments=24)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerB_Idler.stl'), tris, 'TensionerB_Idler')
    print(f"  ✓ TensionerB_Idler.stl 生成完成")

# ============================================================
# PART B4: 弹簧预压装置 (Spring Compensator)
# ============================================================
def make_tensioner_B_spring_ring():
    """方案B: 弹簧预压环 — 3D打印压缩弹簧
    用波纹环(wave washer)代替金属弹簧, 简化装配
    """
    print("[B4/6] TensionerB_SpringRing (波纹预压环)...", flush=True)
    tris = []

    # 波纹环 = 薄壁圆环, 有波纹起伏
    R_OUTER = 12.0
    R_INNER = 6.0
    THICK   = 1.5
    WAVES   = 8
    WAVE_H  = 2.0

    for i in range(WAVES):
        a0 = 2 * math.pi * i / WAVES
        a1 = 2 * math.pi * (i + 1) / WAVES
        # 波峰
        r_peak = R_OUTER + WAVE_H
        # 波谷
        r_valley = R_OUTER - 1.0
        for r in [r_valley, r_peak]:
            x0 = r * math.cos(a0); y0 = r * math.sin(a0)
            x1 = r * math.cos(a1); y1 = r * math.sin(a1)
            # 内弧
            n = normalize(np.array([math.cos((a0+a1)/2), math.sin((a0+a1)/2), 0]))
            tris.append(triangle(n,
                [x0,y0,-THICK/2],[x1,y1,-THICK/2],[x0,y0,THICK/2]))
            tris.append(triangle(n,
                [x1,y1,-THICK/2],[x1,y1,THICK/2],[x0,y0,THICK/2]))
            # 端面
            tris.append(triangle([0,0,1],[x0,y0,THICK/2],[x1,y1,THICK/2],[x0,y0,-THICK/2]))
            tris.append(triangle([0,0,-1],[x0,y0,-THICK/2],[x1,y1,-THICK/2],[x0,y0,THICK/2]))
        # 内外圆弧面
        tris += cylinder_ring_mesh(0, 0, 0, r_valley, R_INNER, THICK, segments=WAVES*2)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerB_SpringRing.stl'), tris, 'TensionerB_SpringRing')
    print(f"  ✓ TensionerB_SpringRing.stl 生成完成")

# ============================================================
# PART A5: 弹簧 (Spring) — 3D打印弹簧圈 (简化表示)
# ============================================================
def make_tensioner_A_spring():
    """方案A: 3D打印压缩弹簧 STL
   Helical spring represented as a series of torus segments
    """
    print("[A5/6] TensionerA_Spring (压缩弹簧)...", flush=True)
    tris = []

    SPRING_R   = 8.0    # 弹簧中径
    WIRE_R     = 1.5    # 线径
    COILS      = 6
    SEGMENTS_P = 36    # 每圈点数
    SEGMENTS_T = 10    # 圆环截面细分

    total_steps = COILS * SEGMENTS_P
    for i in range(total_steps):
        t0 = 2 * math.pi * i / SEGMENTS_P
        t1 = 2 * math.pi * (i + 1) / SEGMENTS_P
        # 轴向位置 (每圈一个周期)
        z0 = WIRE_R * math.cos(t0) + (i / total_steps) * 16.0 - 8.0
        z1 = WIRE_R * math.cos(t1) + ((i+1) / total_steps) * 16.0 - 8.0
        # 径向
        r0 = SPRING_R + WIRE_R * math.sin(t0)
        r1 = SPRING_R + WIRE_R * math.sin(t1)
        cx0 = r0 * math.cos(t0); cy0 = r0 * math.sin(t0)
        cx1 = r1 * math.cos(t1); cy1 = r1 * math.sin(t1)

        # 简化: 用圆柱体段近似螺旋线
        seg_len = math.sqrt((cx1-cx0)**2 + (cy1-cy0)**2 + (z1-z0)**2)
        if seg_len < 0.01:
            continue
        n = normalize(np.array([cx1-cx0, cy1-cy0, z1-z0]))
        # 圆截面
        for j in range(SEGMENTS_T):
            a0 = 2 * math.pi * j / SEGMENTS_T
            a1 = 2 * math.pi * (j + 1) / SEGMENTS_T
            def pt(r, a):
                return np.array([r*math.cos(a), r*math.sin(a), 0], dtype=np.float32)
            p0 = np.array([cx0, cy0, z0], dtype=np.float32)
            p1 = np.array([cx1, cy1, z1], dtype=np.float32)
            v00 = p0 + WIRE_R * math.cos(a0) * n + WIRE_R * math.sin(a0) * normalize(np.cross(n, [0,0,1]+n))
            v10 = p1 + WIRE_R * math.cos(a0) * n + WIRE_R * math.sin(a0) * normalize(np.cross(n, [0,0,1]+n))
            v01 = p0 + WIRE_R * math.cos(a1) * n + WIRE_R * math.sin(a1) * normalize(np.cross(n, [0,0,1]+n))
            v11 = p1 + WIRE_R * math.cos(a1) * n + WIRE_R * math.sin(a1) * normalize(np.cross(n, [0,0,1]+n))
            tris.append(triangle(n, v00, v10, v01))
            tris.append(triangle(n, v10, v11, v01))

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerA_Spring.stl'), tris, 'TensionerA_Spring')
    print(f"  ✓ TensionerA_Spring.stl 生成完成")

# ============================================================
# PART A6: 张力挡块 (Tension Stop) — 限制弹簧压缩量
# ============================================================
def make_tensioner_A_stop():
    """方案A: 张力限位块 — 限制调节螺丝的最大行程
    """
    print("[A6/6] TensionerA_Stop (限位块)...", flush=True)
    tris = []

    STOP_W = 10.0
    STOP_D = 10.0
    STOP_H = 8.0

    tris += box_mesh(0, 0, 0, STOP_W, STOP_D, STOP_H)
    # M3 沉头安装孔
    tris += cylinder_mesh(0, 0, STOP_H/2, M3_CSK_D/2, M3_CSK_DEPTH, segments=12)
    tris += cylinder_mesh(0, 0, STOP_H/2 - M3_CSK_DEPTH, M3_HOLE_D/2, STOP_H/2 + 2, segments=12)
    # 调节面 (半圆形突出)
    tris += cylinder_mesh(0, 0, -STOP_H/2 - 2, 4, 4, segments=16)

    write_stl_binary(os.path.join(OUT_DIR, 'TensionerA_Stop.stl'), tris, 'TensionerA_Stop')
    print(f"  ✓ TensionerA_Stop.stl 生成完成")

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("大鱼TT310 皮带张紧机构 V2 — STL 生成")
    print(f"输出目录: {OUT_DIR}")
    print("=" * 60)

    # 方案A: 弹簧臂式
    make_tensioner_A_idler()
    make_tensioner_A_arm()
    make_tensioner_A_base()
    make_tensioner_A_eccentric_sleeve()
    make_tensioner_A_spring()
    make_tensioner_A_stop()

    # 方案B: 滑轨调节式
    make_tensioner_B_base()
    make_tensioner_B_slider()
    make_tensioner_B_idler()
    make_tensioner_B_spring_ring()

    print("\n" + "=" * 60)
    print("✓ 全部 10 个 STL 文件已生成!")
    print(f"  目录: {OUT_DIR}")
    print("=" * 60)
    print("\n⚠️  注意: 简化版STL (无CSG布尔), 螺钉孔/槽等以'凸起'表示")
    print("  实际打印前请用 slicer 检查尺寸, 必要时调整参数重新生成")
    print("  推荐流程: slicer 切片 → 查看层预览 → 调整参数 → 重新生成 STL")

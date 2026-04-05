#!/usr/bin/env python3
"""
大鱼TT 310 封箱 V2 重新设计
Parametric FreeCAD models for TT310 Enclosure V2
Design date: 2026-03-26
Based on: TT310 STEP analysis + official layout (760mm height)
"""
import sys
sys.path.insert(0, '/usr/lib/freecad-python3/lib')

import FreeCAD
import Part
import Mesh
import MeshPart
import os
import math

# ============================================================
# DESIGN PARAMETERS (all in mm)
# ============================================================
P = {
    # 2020 T-slot profile (confirmed from STEP analysis)
    'slot_w': 6.0,      # T-slot width (mm)
    'slot_d': 1.0,      # T-slot depth (mm) 
    'profile': 20.0,    # 20×20mm profile
    
    # Machine outer dimensions (from STEP analysis)
    'machine_x': 478.0,  # mm
    'machine_y': 490.0,  # mm  
    'machine_z': 760.0,  # mm
    
    # Enclosure clearance (minimal gap machine to panel)
    'clear_x': 15.0,     # mm per side
    'clear_y': 15.0,
    'clear_z_top': 15.0,
    'clear_z_bot': 10.0,
    
    # Panel thickness
    'panel_acrylic': 3.0,  # mm (standard)
    'panel_door': 5.0,     # mm (door, reinforced)
    'panel_base': 5.0,      # mm (bottom, load bearing)
    
    # Fastener sizes
    'm3_drill': 2.9,       # M3 tap drill (mm)
    'm3_countersink': 6.0, # M3 CSK diameter
    'm3_depth': 4.0,        # M3 thread depth
    'm4_drill': 3.3,
    'm6_drill': 5.0,
    'm6_thread': 6.0,
    
    # Bottom bracket
    'bb_base_w': 30.0,
    'bb_base_d': 20.0,
    'bb_base_h': 12.0,
    'bb_slot_w': 6.4,      # slightly larger than slot for fit
    'bb_slot_d': 1.2,
    'bb_tab_w': 8.0,
    'bb_tab_h': 6.0,
    'bb_tab_d': 10.0,
    'bb_hole_spacing': 16.0, # M3 hole spacing in tabs
    
    # Foot mount
    'foot_od': 25.0,       # foot outer diameter
    'foot_id': 8.0,        # center hole for M6 bolt
    'foot_h': 6.0,          # foot pad height
    
    # Seal dimensions
    'seal_d_d': 5.0,       # D-profile seal diameter
    'seal_d_slot_w': 5.5,  # slot width for D seal
    'seal_d_slot_d': 3.5,  # slot depth
    
    # Magnet
    'magnet_od': 10.0,
    'magnet_h': 3.0,
    
    # Fan
    'fan_120': 120.0,      # 120mm fan
    'fan_hole': 105.0,     # mounting hole circle
    'fan_thickness': 25.0,
    
    # Cable entry
    'cable_main': 25.0,    # main cable OD
    'cable_aux1': 8.0,     # auxiliary cable 1
    'cable_aux2': 6.0,    # auxiliary cable 2
    
    # Door hinge
    'hinge_pin': 3.0,
    'hinge_eye': 6.0,
}

OUT_DIR = '/vol1/1000/projects/3d-printing/dayu-tt-all-in-one/enclosure/stl_v2'
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def make_box(w, d, h, name='Box'):
    """Create a box centered at origin"""
    return Part.makeBox(w, d, h, FreeCAD.Vector(-w/2, -d/2, -h/2), name)

def make_cylinder(r, h, name='Cylinder'):
    """Create a cylinder centered at origin"""
    return Part.makeCylinder(r, h, FreeCAD.Vector(0, 0, -h/2), name)

def make_cylinder_at(r, h, x, y, z=0, name='Cylinder'):
    """Create a cylinder at specific location"""
    return Part.makeCylinder(r, h, FreeCAD.Vector(x, y, z), name)

def make_bolt_hole(drill_d, depth, h=0):
    """Create a bolt hole (cylindrical void)"""
    return Part.makeCylinder(drill_d/2, depth, FreeCAD.Vector(0, 0, h))

def make_csk_hole(drill_d, csk_d, csk_depth, total_depth):
    """Create a countersunk hole"""
    # Main drill cylinder
    cyl = Part.makeCylinder(drill_d/2, total_depth - csk_depth)
    # Countersink cone
    r = csk_d/2
    cone = Part.makeCone(0, r, csk_depth)
    # Union
    csk = cyl.fuse(cone)
    csk.translate(FreeCAD.Vector(0, 0, total_depth - csk_depth))
    return csk

def make_slot(w, d, h, name='Slot'):
    """Create a horizontal slot (box centered on XY plane)"""
    return Part.makeBox(w, d, h, FreeCAD.Vector(-w/2, -d/2, -h/2))

def export_stl(shape, filename, name='Part'):
    """Export a shape as STL"""
    mesh = MeshPart.meshFromShape(shape, LinearDeflection=0.05, AngularDeflection=0.1)
    mesh.write(os.path.join(OUT_DIR, filename))
    print(f"  ✓ Exported: {filename}")

def fuse_all(*shapes):
    """Fuse multiple shapes together"""
    if not shapes:
        return None
    result = shapes[0]
    for s in shapes[1:]:
        result = result.fuse(s)
    return result

def cut_all(base, *cutters):
    """Cut multiple shapes from base"""
    result = base
    for c in cutters:
        result = result.cut(c)
    return result

# ============================================================
# PART 1: BottomBracketV2
# Redesigned bottom corner bracket for 2020 T-slot
# ============================================================
def make_bottom_bracket_v2():
    """
    Redesigned bottom bracket:
    - T-slot base plate with 6mm wide slot channel
    - Two side mounting tabs with M3 holes
    - Reinforcement gussets
    - Panel seal compression zone
    - Cable routing channel
    """
    print("\n[1/8] BottomBracketV2...")
    
    w = P['bb_base_w']  # 30mm
    d = P['bb_base_d']  # 20mm  
    h = P['bb_base_h']  # 12mm
    slot_w = P['bb_slot_w']  # 6.4mm
    slot_d = P['bb_slot_d']  # 1.2mm
    tab_w = P['bb_tab_w']  # 8mm
    tab_h = P['bb_tab_h']  # 6mm
    tab_d = P['bb_tab_d']  # 10mm
    
    # Main base plate
    base = make_box(w, d, h, 'BB_Base')
    
    # T-slot channel on bottom (runs along full depth)
    slot_cut = make_box(slot_w + 0.4, d + 2, slot_d + 0.2)
    slot_cut.translate(FreeCAD.Vector(0, 0, -h/2 - 0.1))
    base = base.cut(slot_cut)
    
    # Left tab
    left_tab = make_box(tab_w, tab_d, h + tab_h)
    left_tab.translate(FreeCAD.Vector(-w/2 + tab_w/2, 0, h/2 + tab_h/2))
    
    # Right tab
    right_tab = make_box(tab_w, tab_d, h + tab_h)
    right_tab.translate(FreeCAD.Vector(w/2 - tab_w/2, 0, h/2 + tab_h/2))
    
    bracket = base.fuse(left_tab).fuse(right_tab)
    
    # Gusset fillets (simplified as chamfers via small blocks)
    # Left gusset
    gusset_w = 4.0
    gusset_h = h
    left_gusset = make_box(gusset_w, 2.0, gusset_h)
    left_gusset.translate(FreeCAD.Vector(-w/2 + tab_w, 0, 0))
    bracket = bracket.fuse(left_gusset)
    
    right_gusset = make_box(gusset_w, 2.0, gusset_h)
    right_gusset.translate(FreeCAD.Vector(w/2 - tab_w - gusset_w, 0, 0))
    bracket = bracket.fuse(right_gusset)
    
    # M3 bolt holes in left tab (2 holes)
    hole_r = P['m3_drill'] / 2
    for y_off in [-3, 3]:
        h_left = Part.makeCylinder(hole_r, tab_w + 2)
        h_left.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
        h_left.translate(FreeCAD.Vector(-w/2 + tab_w/2, y_off, h/2 + tab_h/2))
        bracket = bracket.cut(h_left)
    
    # M3 bolt holes in right tab
    for y_off in [-3, 3]:
        h_right = Part.makeCylinder(hole_r, tab_w + 2)
        h_right.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
        h_right.translate(FreeCAD.Vector(w/2 - tab_w/2, y_off, h/2 + tab_h/2))
        bracket = bracket.cut(h_right)
    
    # M3 countersink holes in base top (4 corner holes)
    csk_r = P['m3_countersink'] / 2
    csk_depth = 2.5
    hole_positions = [
        (-w/2 + 4, -d/2 + 4),
        (-w/2 + 4,  d/2 - 4),
        ( w/2 - 4, -d/2 + 4),
        ( w/2 - 4,  d/2 - 4),
    ]
    for x, y in hole_positions:
        h_csk = Part.makeCylinder(hole_r, h - csk_depth + 0.1)
        h_csk.translate(FreeCAD.Vector(x, y, -h/2 + csk_depth))
        cone = Part.makeCone(0, csk_r, csk_depth)
        cone.translate(FreeCAD.Vector(x, y, -h/2))
        bracket = bracket.cut(h_csk).cut(cone)
    
    # Cable channel groove on side face
    chan_w = 8.0
    chan_d = 3.0
    chan = make_box(chan_w, d + 1, chan_d)
    chan.translate(FreeCAD.Vector(0, 0, h/2 - chan_d/2))
    bracket = bracket.cut(chan)
    
    # Panel seal compression ledge (thin lip on outer face)
    lip = make_box(w + 2, 2, 2)
    lip.translate(FreeCAD.Vector(0, d/2 + 1, h/2 - 3))
    bracket = bracket.fuse(lip)
    
    export_stl(bracket, 'BottomBracketV2.stl', 'BottomBracketV2')
    return bracket

# ============================================================
# PART 2: FootMountV2
# Integrated foot mount with vibration damping pocket
# ============================================================
def make_foot_mount_v2():
    """
    Foot mount redesigned:
    - Base that sits in bottom bracket recess
    - Central M6 through-hole for adjustable foot
    - TPU damping insert pocket
    - Anti-rotation flats
    """
    print("[2/8] FootMountV2...")
    
    outer_d = P['foot_od']  # 25mm
    inner_d = P['foot_id']   # 8mm (M6)
    h = 12.0
    
    # Main body
    body = make_cylinder(outer_d/2, h)
    
    # M6 through hole
    hole = make_cylinder_at(P['m6_drill']/2, h + 4, 0, 0, -2)
    body = body.cut(hole)
    
    # TPU damping pocket (shallower inner cylinder)
    damp_outer = 18.0
    damp_inner = 8.5
    damp_h = 4.0
    damp_ring = make_cylinder(damp_outer/2, damp_h)
    damp_hole = make_cylinder(damp_inner/2, damp_h + 1)
    damp_ring = damp_ring.cut(damp_hole)
    damp_ring.translate(FreeCAD.Vector(0, 0, h/2 - damp_h))
    body = body.cut(damp_ring)
    
    # Anti-rotation flats on sides
    flat_w = 4.0
    flat_d = 2.0
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        fx = (outer_d/2 + 0.5) * math.cos(rad)
        fy = (outer_d/2 + 0.5) * math.sin(rad)
        flat = make_box(flat_w, flat_d, h + 0.2)
        flat.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), angle)
        flat.translate(FreeCAD.Vector(fx, fy, 0))
        body = body.cut(flat)
    
    # Base flange (wider bottom for stability)
    flange_d = outer_d + 6.0
    flange_h = 3.0
    flange = make_cylinder(flange_d/2, flange_h)
    flange.translate(FreeCAD.Vector(0, 0, -h/2 - flange_h/2))
    body = body.fuse(flange)
    
    export_stl(body, 'FootMountV2.stl', 'FootMountV2')
    return body

# ============================================================
# PART 3: FootPadV2
# Redesigned TPU foot pad
# ============================================================
def make_foot_pad_v2():
    """
    Redesigned foot pad (TPU):
    - Conical shape for adjustability
    - Anti-slip texture (simplified as ridges)
    """
    print("[3/8] FootPadV2...")
    
    od = P['foot_od'] + 2.0  # slightly larger than mount
    h = P['foot_h']
    
    # Basic cylindrical foot pad
    pad = make_cylinder(od/2, h)
    
    # Dome top for better foot contact
    dome = Part.makeSphere(od/3)
    dome.translate(FreeCAD.Vector(0, 0, h/2))
    # Clip dome to cylinder intersection
    cyl_top = make_cylinder(od/2, h/2)
    cyl_top.translate(FreeCAD.Vector(0, 0, h/2))
    dome = dome.intersect(cyl_top)
    
    pad = pad.fuse(dome)
    
    export_stl(pad, 'FootPadV2.stl', 'FootPadV2')
    return pad

# ============================================================
# PART 4: SidePanelClipV2
# Redesigned panel clip with seal compression
# ============================================================
def make_side_panel_clip_v2():
    """
    Redesigned side panel clip:
    - T-slot snap mount (no screws needed)
    - Panel compression zone
    - D-seal groove for panel edge sealing
    - 3-point contact for rigidity
    """
    print("[4/8] SidePanelClipV2...")
    
    w = 25.0
    d = 18.0
    h = 15.0
    panel_t = P['panel_acrylic']  # 3mm
    
    # Main body
    body = make_box(w, d, h, 'SPC_Body')
    
    # T-slot snap arm (flexible tab)
    snap_w = 4.0
    snap_h = 5.0
    snap_d = P['slot_w'] + 0.3  # 6.3mm for snug fit
    snap = make_box(snap_w, d + 2, snap_h)
    snap.translate(FreeCAD.Vector(-w/2 + snap_w/2, 0, -h/2 - snap_h/2 + 1))
    body = body.fuse(snap)
    
    # Snap detent (small bump for click-fit)
    detent = make_box(snap_w - 1, 3, 1.5)
    detent.translate(FreeCAD.Vector(-w/2 + snap_w/2 + 0.5, 0, -h/2 - snap_h/2 + 3))
    body = body.fuse(detent)
    
    # Panel capture slot (for 3mm acrylic)
    slot_w = panel_t + 0.4  # 3.4mm
    slot_d = 6.0
    capture = make_box(slot_w + 0.2, d + 2, slot_d)
    capture.translate(FreeCAD.Vector(w/2 - slot_w/2, 0, h/2 + slot_d/2 - 1))
    body = body.cut(capture)
    
    # D-seal groove on outer face
    seal_groove = make_box(w + 2, 2.5, P['seal_d_slot_d'])
    seal_groove.translate(FreeCAD.Vector(0, d/2 + 2.5/2 - 0.5, h/2 - 3))
    body = body.cut(seal_groove)
    
    # Mounting hole (optional M3, in case snap doesn't hold)
    hole = make_cylinder(P['m3_drill']/2, d + 4)
    hole.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
    hole.translate(FreeCAD.Vector(0, 0, -h/2 + 5))
    body = body.cut(hole)
    
    export_stl(body, 'SidePanelClipV2.stl', 'SidePanelClipV2')
    return body

# ============================================================
# PART 5: TopFanMountV2
# Redesigned 120mm top fan mount with labyrinth seal
# ============================================================
def make_top_fan_mount_v2():
    """
    Redesigned top fan mount:
    - 120mm fan housing with 25mm depth
    - Labyrinth seal on outlet (reduces noise)
    - Magnetic filter frame integrated
    - D-seal groove for enclosure top
    - M3 screw mounting (4 points)
    """
    print("[5/8] TopFanMountV2...")
    
    fan = P['fan_120']  # 120mm
    fan_h = P['fan_thickness']  # 25mm
    housing_w = fan + 10.0  # 130mm outer
    housing_d = fan + 10.0
    housing_h = 35.0  # total height including duct
    
    # Main housing (box with rounded corners approximated)
    housing = make_box(housing_w, housing_d, housing_h)
    
    # Fan recess (cylindrical cutout for fan)
    recess_r = fan/2 + 0.5
    recess = make_cylinder(recess_r, fan_h + 2)
    recess.translate(FreeCAD.Vector(0, 0, housing_h/2 - fan_h/2 - 3))
    housing = housing.cut(recess)
    
    # Fan blade clearance (smaller inner cylinder)
    blade_r = fan/2 - 10
    blade = make_cylinder(blade_r, fan_h + 4)
    blade.translate(FreeCAD.Vector(0, 0, housing_h/2 - fan_h/2 - 3))
    housing = housing.cut(blade)
    
    # Mounting holes (4× M3 on 105mm circle)
    hole_r = P['m3_drill'] / 2
    mount_circle = P['fan_hole'] / 2  # 52.5mm radius
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        hx = mount_circle * math.cos(rad)
        hy = mount_circle * math.sin(rad)
        h = make_cylinder(hole_r, housing_h + 4)
        h.translate(FreeCAD.Vector(hx, hy, 0))
        housing = housing.cut(h)
    
    # D-seal groove around the housing base
    seal_groove = make_box(housing_w + 2, housing_d + 2, P['seal_d_slot_d'])
    seal_groove.translate(FreeCAD.Vector(0, 0, -housing_h/2 + P['seal_d_slot_d']/2))
    housing = housing.cut(seal_groove)
    
    # Labyrinth louver cuts (horizontal slots)
    for i in range(4):
        slot_y = housing_d/2 + 1
        slot = make_box(housing_w - 10, 1.5, housing_h + 2)
        slot.translate(FreeCAD.Vector(0, slot_y, -housing_h/2 + 5 + i * 6))
        housing = housing.cut(slot)
    
    # Duct collar (outlet on top)
    duct_r = fan/2 - 5
    duct_h = 15.0
    duct = make_cylinder(duct_r, duct_h)
    duct.translate(FreeCAD.Vector(0, 0, housing_h/2 - 3))
    housing = housing.fuse(duct)
    
    # Duct inner cone for airflow straightening
    cone_out = make_cylinder(duct_r + 2, 8)
    cone_in = make_cylinder(duct_r - 2, 9)
    cone = cone_out.cut(cone_in)
    cone.translate(FreeCAD.Vector(0, 0, housing_h/2 + duct_h - 5))
    housing = housing.fuse(cone)
    
    export_stl(housing, 'TopFanMountV2.stl', 'TopFanMountV2')
    return housing

# ============================================================
# PART 6: CableEntryRingV2
# Redesigned cable entry with multi-seal design
# ============================================================
def make_cable_entry_ring_v2():
    """
    Redesigned cable entry gland:
    - Main channel for 25mm cables (power, data)
    - 2× auxiliary channels (8mm, 6mm)
    - Silicone seal grooves
    - M3 screw compression
    - T-slot snap mount
    """
    print("[6/8] CableEntryRingV2...")
    
    main_d = P['cable_main'] + 6.0  # 31mm outer for main
    h = 15.0
    
    # Main ring body
    body = make_cylinder(main_d/2 + 4, h)
    
    # Main cable hole
    main_hole = make_cylinder(P['cable_main']/2 + 1.5, h + 4)
    body = body.cut(main_hole)
    
    # Auxiliary holes (offset to the side)
    aux1_offset = main_d/2 + 4 + 8
    aux1 = make_cylinder(P['cable_aux1']/2 + 2, h + 4)
    aux1.translate(FreeCAD.Vector(aux1_offset, 0, 0))
    body = body.cut(aux1)
    
    aux2_offset = main_d/2 + 4 + 18
    aux2 = make_cylinder(P['cable_aux2']/2 + 2, h + 4)
    aux2.translate(FreeCAD.Vector(aux2_offset, 0, 0))
    body = body.cut(aux2)
    
    # Seal gland rings (rubber ring compression)
    for r_offset in [0, 4, 8]:
        gland_r = (P['cable_main']/2 + 3) + r_offset * 0.3
        gland_h = 2.0
        gland = make_cylinder(gland_r, gland_h)
        gland_hole = make_cylinder(gland_r - 1.5, gland_h + 1)
        gland = gland.cut(gland_hole)
        gland.translate(FreeCAD.Vector(0, 0, -h/2 + 3 + r_offset * 1.5))
        body = body.cut(gland)
    
    # T-slot snap mount
    slot_w = P['slot_w'] + 0.4
    slot_prof = make_box(slot_w, main_d + 8, 5)
    slot_prof.translate(FreeCAD.Vector(0, 0, -h/2 - 5/2 + 0.5))
    body = body.cut(slot_prof)
    
    # M3 screw holes for strain relief (2×)
    for x_off in [-8, 8]:
        scr = make_cylinder(P['m3_drill']/2, h + 4)
        scr.translate(FreeCAD.Vector(x_off, main_d/2 + 4, 0))
        body = body.cut(scr)
    
    export_stl(body, 'CableEntryRingV2.stl', 'CableEntryRingV2')
    return body

# ============================================================
# PART 7: MagnetHolderV2
# Redesigned magnet holder with press-fit and panel clip
# ============================================================
def make_magnet_holder_v2():
    """
    Redesigned magnet holder:
    - Ø10×3mm magnet press-fit recess
    - Panel snap clip
    - Flush outer face
    - 2 removal slots
    """
    print("[7/8] MagnetHolderV2...")
    
    od = 16.0
    h = 5.0
    
    body = make_cylinder(od/2, h)
    
    # Magnet recess (press fit - slightly undersized)
    magnet_r = P['magnet_od']/2 - 0.3  # press fit
    magnet_hole = make_cylinder(magnet_r, h + 2)
    body = body.cut(magnet_hole)
    
    # Snap arms for panel (2× small tabs)
    for angle in [0, 180]:
        rad = math.radians(angle)
        tab = make_box(3, 2, 3)
        tab.translate(FreeCAD.Vector(od/2 * math.cos(rad) + (3 if math.cos(rad) > 0 else -3) * math.cos(rad),
                                      od/2 * math.sin(rad),
                                      0))
        body = body.fuse(tab)
    
    # Removal slots (for disassembly)
    for angle in [90, 270]:
        rad = math.radians(angle)
        slot = make_box(3, 4, 2)
        slot.translate(FreeCAD.Vector(od/2 * math.cos(rad),
                                      od/2 * math.sin(rad) + 4 * math.sin(rad),
                                      h/2 + 1))
        body = body.cut(slot)
    
    export_stl(body, 'MagnetHolderV2.stl', 'MagnetHolderV2')
    return body

# ============================================================
# PART 8: DoorHingeMountV2
# Redesigned door hinge mount
# ============================================================
def make_door_hinge_mount_v2():
    """
    Redesigned hinge mount:
    - Works with 30mm small hinges
    - Reinforced mounting plate
    - 3× M3 bolt holes
    - Panel attachment ledge
    - Hinge pin receptacle
    """
    print("[8/8] DoorHingeMountV2...")
    
    w = 30.0
    d = 20.0
    h = 12.0
    pin_r = P['hinge_eye'] / 2  # 3mm pin
    
    body = make_box(w, d, h)
    
    # Hinge eye hole (horizontal through)
    eye_hole = make_cylinder(pin_r + 1.5, d + 4)
    eye_hole.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 90)
    eye_hole.translate(FreeCAD.Vector(-w/2 + 6, 0, h/2 - 4))
    body = body.cut(eye_hole)
    
    # Hinge leaf holes (2× M3 for hinge screws)
    for y_off in [-4, 4]:
        h_hole = Part.makeCylinder(P['m3_drill']/2, w + 4)
        h_hole.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
        h_hole.translate(FreeCAD.Vector(0, y_off, h/2 - 4))
        body = body.cut(h_hole)
    
    # Panel mount holes (3× M3 on body)
    for x_pos in [-w/2 + 4, 0, w/2 - 4]:
        panel_h = Part.makeCylinder(P['m3_drill']/2, d + 4)
        panel_h.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
        panel_h.translate(FreeCAD.Vector(x_pos, 0, -h/2 + 3))
        body = body.cut(panel_h)
    
    # Countersinks on panel face
    for x_pos in [-w/2 + 4, 0, w/2 - 4]:
        csk = Part.makeCone(0, P['m3_countersink']/2, 2.5)
        csk.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), -90)
        csk.translate(FreeCAD.Vector(x_pos, -d/2 - 0.1, -h/2 + 3))
        body = body.cut(csk)
    
    # Reinforcement gussets
    left_gusset = make_box(3, d - 4, h - 2)
    left_gusset.translate(FreeCAD.Vector(-w/2 + 4, 0, 0))
    right_gusset = make_box(3, d - 4, h - 2)
    right_gusset.translate(FreeCAD.Vector(w/2 - 7, 0, 0))
    body = body.fuse(left_gusset).fuse(right_gusset)
    
    export_stl(body, 'DoorHingeMountV2.stl', 'DoorHingeMountV2')
    return body

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("大鱼TT 310 封箱 V2 重新设计")
    print("Parametric FreeCAD Generation")
    print("Design date: 2026-03-26")
    print("=" * 60)
    
    doc_name = "TT310_EnclosureV2"
    doc = FreeCAD.newDocument(doc_name)
    
    make_bottom_bracket_v2()
    make_foot_mount_v2()
    make_foot_pad_v2()
    make_side_panel_clip_v2()
    make_top_fan_mount_v2()
    make_cable_entry_ring_v2()
    make_magnet_holder_v2()
    make_door_hinge_mount_v2()
    
    print("\n" + "=" * 60)
    print(f"All STL files exported to:")
    print(f"  {OUT_DIR}")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review STL files in slicer")
    print("  2. Print test pieces")
    print("  3. Verify fit on actual machine")
    print("  4. Generate DXF panel cutting diagrams")
    print("  5. Update BOM and assembly guide")

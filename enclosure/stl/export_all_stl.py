#!/usr/bin/env python3
"""
US-010: Export all FreeCAD parts to STL for 3D printing
Run: python3 export_all_stl.py
"""
import sys, os
sys.path.insert(0, '/usr/lib/freecad-python3/lib')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import FreeCAD
import Mesh

parts = [
    ("enclosure/freecad/BottomBracketComplete.FCStd",  "Body"),
    ("enclosure/freecad/FootMountComplete.FCStd",     "Body"),
    ("enclosure/freecad/FootPad.FCStd",              "FootPad"),
    ("enclosure/freecad/TopFanMount.FCStd",          "TopFanMountWithHole"),
    ("enclosure/freecad/CornerBracket.FCStd",        "CornerBracket"),
    ("enclosure/freecad/SidePanelClip.FCStd",        "SidePanelClip"),
    ("enclosure/freecad/TopPlateMount.FCStd",       "TopPlateMount"),
    ("enclosure/freecad/DoorHandle.FCStd",           "DoorHandle"),
    ("enclosure/freecad/VentCover.FCStd",           "VentCover"),
    ("enclosure/freecad/CableEntryRing.FCStd",      "CableEntryRing"),
    ("enclosure/freecad/FilterFrame.FCStd",          "FilterFrame"),
    ("enclosure/freecad/HingeMount.FCStd",          "HingeMount"),
    ("enclosure/freecad/MagnetHolder.FCStd",         "MagnetHolder"),
]

outdir = "enclosure/stl"
os.makedirs(outdir, exist_ok=True)

for fcstd_path, obj_name in parts:
    if not os.path.exists(fcstd_path):
        print(f"SKIP: {fcstd_path} not found")
        continue
    doc = FreeCAD.open(fcstd_path)
    obj = doc.getObject(obj_name)
    if not obj:
        # Try first object
        obj = doc.Objects[0] if doc.Objects else None
    if not obj:
        print(f"SKIP: no objects in {fcstd_path}")
        FreeCAD.closeDocument(doc.Name)
        continue
    stl_path = os.path.join(outdir, f"{obj_name}.stl")
    Mesh.export([obj], stl_path)
    print(f"OK: {stl_path}")
    FreeCAD.closeDocument(doc.Name)

print("\nDone. All STL files in enclosure/stl/")

#!/usr/bin/env python3
"""
US-003-02: Create bottom bracket body geometry (40×30×15mm)
Bottom Bracket: 40mm(W) × 30mm(D) × 15mm(H)
"""
import sys, os
sys.path.insert(0, '/usr/lib/freecad-python3/lib')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

import FreeCAD

doc = FreeCAD.newDocument("BottomBracketBody")
body = doc.addObject("Part::Box", "BottomBracketBody")
body.Label = 'BottomBracketBody'
body.Length = 40.0
body.Width = 30.0
body.Height = 15.0

doc.recompute()

# Save
out = os.path.join(os.path.dirname(__file__), '..', 'BottomBracketBody.FCStd')
doc.saveAs(out)

bb = body.Shape.BoundBox
print(f"OK: BottomBracketBody {bb.XLength:.1f}x{bb.YLength:.1f}x{bb.ZLength:.1f}mm saved")

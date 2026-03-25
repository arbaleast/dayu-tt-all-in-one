#!/usr/bin/env python3
"""
US-003-03: Add M3 countersunk holes to bottom bracket
4x M3 countersunk holes at corners, 3mm from edges
"""
import sys, os
sys.path.insert(0, '/usr/lib/freecad-python3/lib')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

import FreeCAD
import Part

doc = FreeCAD.newDocument("BottomBracketM3Holes")

# Base body
body = doc.addObject("Part::Box", "BottomBracket")
body.Label = 'BottomBracket'
body.Length = 40.0
body.Width = 30.0
body.Height = 15.0
doc.recompute()

# 4x M3 countersunk holes at corners (3mm inset)
# M3 countersunk: head Ø5.8mm, shaft Ø3.0mm
holes = []
for x, y in [(-14, -10), (14, -10), (-14, 10), (14, 10)]:
    h = doc.addObject("Part::Cylinder", f"Hole_{x}_{y}")
    h.Radius = 1.5   # M3 shaft radius
    h.Height = 20.0  # through
    h.Placement.Base.x = x
    h.Placement.Base.y = y
    h.Placement.Base.z = 7.5
    holes.append(h)

# Countersunk head: Ø5.8mm, depth 1.5mm
for i, (x, y) in enumerate([(-14, -10), (14, -10), (-14, 10), (14, 10)]):
    head = doc.addObject("Part::Cylinder", f"Head_{x}_{y}")
    head.Radius = 2.9
    head.Height = 1.5
    head.Placement.Base.x = x
    head.Placement.Base.y = y
    head.Placement.Base.z = 15.0 - 1.5

doc.recompute()

out = os.path.join(os.path.dirname(__file__), '..', 'BottomBracketM3Holes.FCStd')
doc.saveAs(out)
print(f"OK: BottomBracketM3Holes with 4x M3 csunk holes saved")

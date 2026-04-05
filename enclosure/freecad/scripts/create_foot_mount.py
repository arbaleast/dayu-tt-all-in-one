#!/usr/bin/env python3
"""US-003-05: Create foot mount body (Ø20×15mm)"""
import sys, os
sys.path.insert(0, '/usr/lib/freecad-python3/lib')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import FreeCAD
doc = FreeCAD.newDocument("FootMount")
cyl = doc.addObject("Part::Cylinder", "FootMount")
cyl.Label = 'FootMount'
cyl.Radius = 10.0
cyl.Height = 15.0
doc.recompute()
out = os.path.join(os.path.dirname(__file__), '..', 'FootMount.FCStd')
doc.saveAs(out)
print(f"OK: FootMount Ø20x15mm saved")

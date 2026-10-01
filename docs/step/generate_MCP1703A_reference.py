"""Recreate the standalone MC package reference with FreeCAD Python.

Source: Microchip MCP1703A DS20005122C, pages 29-30, drawing C04-123 Rev E.
Independent geometry, not a Microchip STEP. Rectangular terminal outlines,
no tie bars, chamfers or pin-1 marking. STEP solid names identify pins.
XY is rotated 90 degrees relative to the drawing: E along X, D along Y.
Pin 1 is at negative X / positive Y when looking down from positive Z.
"""
from pathlib import Path
import FreeCAD as App
import Part

PARAMETERS_MM = dict(body_x=3.0, body_y=2.0, height=0.90, standoff=0.02,
                     metal_thickness=0.20, pitch=0.50, lead_length=0.40,
                     lead_width=0.25, exposed_pad_x=1.625, exposed_pad_y=1.425)
# EP dimensions are midpoints of specified ranges, not published nominals:
# E2 = 1.50..1.75 and D2 = 1.30..1.55. A3 = 0.20 is a reference dimension.


def generate(path):
    p = PARAMETERS_MM
    doc = App.newDocument('MCP1703A_MC_reference')
    terminals = []
    for pin in range(1, 9):
        if pin <= 4:
            x = -p['body_x']/2
            y = (2.5-pin)*p['pitch']
        else:
            x = p['body_x']/2-p['lead_length']
            y = (pin-6.5)*p['pitch']
        shape = Part.makeBox(p['lead_length'], p['lead_width'], p['metal_thickness'],
                             App.Vector(x, y-p['lead_width']/2, 0))
        obj = doc.addObject('Part::Feature', f'Pin_{pin}')
        obj.Shape = shape
        terminals.append(obj)
    ep = doc.addObject('Part::Feature', 'Exposed_Pad_9')
    ep.Shape = Part.makeBox(p['exposed_pad_x'], p['exposed_pad_y'], p['metal_thickness'],
                           App.Vector(-p['exposed_pad_x']/2, -p['exposed_pad_y']/2, 0))
    metal = [obj.Shape for obj in terminals] + [ep.Shape]
    body = doc.addObject('Part::Feature', 'Molded_Body')
    box = Part.makeBox(p['body_x'], p['body_y'], p['height']-p['standoff'],
                       App.Vector(-p['body_x']/2, -p['body_y']/2, p['standoff']))
    body.Shape = box.cut(Part.makeCompound(metal))
    objects = [body] + terminals + [ep]
    doc.recompute()
    assert all(obj.Shape.isValid() for obj in objects)
    Part.export(objects, str(path))
    App.closeDocument(doc.Name)


if __name__ == '__main__':
    generate(Path(__file__).with_name('MCP1703A_MC_datasheet_reference.step'))

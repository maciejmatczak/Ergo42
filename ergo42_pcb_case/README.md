# DON'T MANUFACTURE ANYTHING YET

![PCB case](./pcb_case.png)

## Foreword

I was really missing PCB like case for this keyboard. But as a guy with
electronic/engineering/programming background instead manually one-shot go
through already existing acrylic case design to gerbers process I tried to
introduce some engineering point of view and automations.

## Process description

Case is redesigned in FreeCAD to achieve pure mechanical description. Exported
DXFs are later manually imported in clean KiCad's PCB as edge cuts. After this,
one can use few scripts through prepared [invoke](http://www.pyinvoke.org/)
commands to do following:

- `inv circles2holes`: changes every true circle on edge cuts layer into mounting hole
- `inv plot`: creates gerbers and zippes them
- `inv verify`: simple verifier for drills between board, plate, bottom and cover (uses fab files)

## FreeCAD design notes

Design of the case was remade to achieve nice mechanical like description.
After few times starting over, I used master sketch approach. Master sketch
is mostly built on manual measurments of PCB and already existing acrylic case
design.

From FreeCAD we can freely export DXF of every design can be exported.

## KiCad design notes

DXFs are manually imported in PCB. After that KiCad can be closed at all, rest is done via the scripts.

## Verification design notes

Verifications use drill fab files. Logic is quite simple: we do know sets of
drills between the designs should match, so we do cross check those. List of holes
is normalized to left bottom most hole and diffed between.

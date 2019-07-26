import os
from pathlib import Path
import sys

import pcbnew


pcb_path = os.path.abspath(sys.argv[1])
mh_pretty = os.path.abspath(sys.argv[2])
mh_name = sys.argv[3]

if not Path(pcb_path).exists():
    print(f'PCB {pcb_path} not found, exiting')
    sys.exit(1)

if not Path(mh_pretty).exists():
    print(f'Pretty path {mh_pretty} not found, exiting')
    sys.exit(1)

board = pcbnew.LoadBoard(pcb_path)
io = pcbnew.PCB_IO()

# the only modules there should be already existing mounting holes - we
# perfectly fine to delete it
for m in board.GetModules():
    board.Delete(m)

# every circle (on every layer) is going to be used as coord source for
# mounting hole
for drawing in board.GetDrawings():
    type = drawing.GetShapeStr()
    if type == 'Circle':
        center = drawing.GetCenter()

        mod = io.FootprintLoad(mh_pretty, mh_name)
        if mod is None:
            print(f'Footprint {mh_name} not found')
            sys.exit(1)

        mod.SetPosition(center)
        mod.Reference().SetVisible(False)
        board.Add(mod)

        # moving circles from edge cuts - still needed as coord reference
        # for easily redoing mounting hole placement
        drawing.SetLayer(board.GetLayerID("Eco1.User"))

board.Save(board.GetFileName())

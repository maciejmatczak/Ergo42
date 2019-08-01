''' Python script for auto plotting proper gerbers.

Based (pretty much copied) from Andrey Shmakov:
https://github.com/akshmakov/pcbops_template/blob/master/kicad_cicd/plotter.py

Also great talk from KiCon 2019: 
PCBOps : Applying CI/CD To PCB Design Projects
https://www.youtube.com/watch?v=cQ-iFtBBwFc
'''

import sys
import os

import pcbnew
from pcbnew import EXCELLON_WRITER, wxPoint

file_name = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])

try:
    os.makedirs(output_dir)
except OSError:
    pass


board = pcbnew.LoadBoard(file_name)
pctl = pcbnew.PLOT_CONTROLLER(board)
popt = pctl.GetPlotOptions()
popt.SetOutputDirectory(output_dir)
popt.SetPlotFrameRef(False)
popt.SetLineWidth(pcbnew.FromMM(0.1))

popt.SetAutoScale(False)
popt.SetScale(1)
popt.SetMirror(False)

popt.SetUseGerberAttributes(True)
popt.SetUseGerberProtelExtensions(True)

popt.SetExcludeEdgeLayer(True)
popt.SetUseAuxOrigin(False)
pctl.SetColorMode(True)

popt.SetSubtractMaskFromSilk(False)
popt.SetPlotReference(True)
popt.SetPlotValue(True)

layers = [
    ("F.Cu", pcbnew.F_Cu, "Top layer"),
    ("B.Cu", pcbnew.B_Cu, "Bottom layer"),
    # ("F.Paste", pcbnew.F_Paste, "Paste top"),
    # ("B.Paste", pcbnew.B_Paste, "Paste bottom"),
    ("F.SilkS", pcbnew.F_SilkS, "Silk top"),
    ("B.SilkS", pcbnew.B_SilkS, "Silk top"),
    ("F.Mask", pcbnew.F_Mask, "Mask top"),
    ("B.Mask", pcbnew.B_Mask, "Mask bottom"),
    ("Edge.Cuts", pcbnew.Edge_Cuts, "Edges"),
]

for layer_info in layers:
    pctl.SetLayer(layer_info[1])
    pctl.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_GERBER, layer_info[2])
    pctl.PlotLayer()
    pctl.ClosePlot()

drill_writer = EXCELLON_WRITER(board)
drill_writer.SetOptions(
    aMirror=False,
    aMinimalHeader=False,
    aOffset=wxPoint(0, 0),
    aMerge_PTH_NPTH=True
)

metric = True
drill_writer.SetFormat(metric)
drill_writer.CreateDrillandMapFilesSet(
    aPlotDirectory=output_dir,
    aGenDrill=True,
    aGenMap=False
)

pctl.OpenPlotfile("Overview", pcbnew.PLOT_FORMAT_PDF, "overview")
for layer_info in layers:
    pctl.SetLayer(layer_info[1])
    pctl.PlotLayer()
pctl.ClosePlot()

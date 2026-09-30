#!/bin/bash
# v0.7 pipeline: placement -> DSN -> Freerouting -> SES -> post-route -> DRC -> exports (if clean)
cd "$(dirname "$0")"
K="/c/Users/LAPTOP/AppData/Local/Programs/KiCad/10.0/bin"
J="/c/Users/LAPTOP/tools/jre25/jdk-25.0.4.1+1-jre/bin/java.exe"
FR="/c/Users/LAPTOP/tools/freerouting/freerouting-2.4.1.jar"
B="$(cygpath -w "$PWD/ppg_pcb_v08.kicad_pcb")"; S="$(cygpath -w "$PWD/ppg_pcb_v08.kicad_sch")"
DD="$(cygpath -w "$PWD/../docs")"; G="$(cygpath -w "$PWD/../gerber")/"

"$K/python.exe" build_pcb_v08.py "$B" 2>&1 | grep -E "pads|Error|error"
"$K/kicad-cli.exe" pcb drc --severity-all --format json -o drc0.json "$B" >/dev/null 2>&1
python drc_summary.py drc0.json placement
mkdir -p /tmp/fr8 && cp ppg_pcb_v08.dsn /tmp/fr8/
( cd /tmp/fr8 && rm -f ppg_pcb_v08.ses && timeout 500 "$J" -jar "$FR" -de ppg_pcb_v08.dsn -do ppg_pcb_v08.ses -mp 80 -l en -mt 4 2>&1 | grep -E "Auto-routing stage completed|Net '" | tail -3 )
cp /tmp/fr8/ppg_pcb_v08.ses .
"$K/python.exe" build_pcb_v08.py "$B" --ses "$(cygpath -w "$PWD/ppg_pcb_v08.ses")" 2>&1 | tail -1
"$K/kicad-cli.exe" pcb drc --severity-all --format json -o drc.json "$B" >/dev/null 2>&1
"$K/python.exe" postroute_v08.py "$B" drc.json 2>&1 | grep -v "memory leak"
"$K/kicad-cli.exe" pcb drc --severity-all --format json -o drc.json "$B" >/dev/null 2>&1
python drc_summary.py drc.json final
if [ "$(cat drc_ok.flag)" != "1" ]; then echo "DRC not clean - stopping before export"; exit 0; fi

"$K/python.exe" netcheck_v08.py 2>&1 | grep -v "memory leak"
rm -rf ../gerber/*
"$K/kicad-cli.exe" pcb export gerbers --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts,F.Fab,B.Fab" --subtract-soldermask --no-x2 --use-drill-file-origin -o "$G" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format pdf -o "$G" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb export pos --format csv --units mm --side both --use-drill-file-origin -o "$DD\\ppg_pcb_v08_positions.csv" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb export pdf --layers "F.Cu,B.Cu,In1.Cu,In2.Cu,Edge.Cuts,F.Fab,B.Fab" --mode-multipage -o "$DD\\ppg_pcb_v08_layers.pdf" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb render --side top --background opaque --quality high -w 1400 -h 1400 -o "$DD\\render_front.png" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb render --side bottom --background opaque --quality high -w 1400 -h 1400 -o "$DD\\render_back.png" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb export svg --layers "F.Cu,F.Fab,Edge.Cuts" --page-size-mode 2 -o "$DD\\layout_front.svg" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb export svg --layers "B.Cu,B.Fab,Edge.Cuts" --page-size-mode 2 --mirror -o "$DD\\layout_back.svg" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" pcb export step --subst-models -o "$DD\\ppg_pcb_v08.step" "$B" >/dev/null 2>&1
"$K/kicad-cli.exe" sch export pdf -o "$DD\\ppg_pcb_v08_schematic.pdf" "$S" >/dev/null 2>&1
python bom_v08.py
rm -f drc0.json erc.json netlist.xml drc_ok.flag
ls ../docs

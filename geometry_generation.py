"""
Code part of FYP: "Aerodynamic shape optimization of wings with compliant winglets"

Jaime Galiana Herrera
Imperial College London
Feb 2024

Code designed for the automatic generation of wing geometry utilizing FLEXOP aircraft geometry and OpenVSP.
It allows for exploring different cant and sweep angle configurations. The total wing span is fixed, 
thus, the different winglet configurations affect the main wing span and this is taken into account in the code.

"""

import os
import subprocess
from subprocess import PIPE
import numpy as np
import sys
import argparse

def chord_distribution(x, span_total, chord_root, chord_tip):
    return round((chord_tip - chord_root)/span_total * x + chord_root, 4)

def wingspan_distribution(span_total, span_blend, span_winglet, cant_blend, cant_winglet):
    cant_blend = np.radians(cant_blend)
    cant_winglet = np.radians(cant_winglet)
    projected_span_blend = span_blend*np.cos(cant_blend)
    projected_span_winglet = span_winglet*np.cos(cant_winglet)
    if -np.radians(90) <= cant_winglet <= np.radians(90):
        return round(span_total - projected_span_blend - projected_span_winglet, 4)
    else:
        return round(span_total - projected_span_blend, 4)

def winglet_chord_distribution(x, span_total, chord_root, chord_tip):
    return round((chord_tip - chord_root)/span_total * x + chord_root, 4)

def blended_span_distribution(cant):
    return round(0.01/9 * abs(cant) + 0.1, 4)

def main(cant, sweep):
    # Wing geometry of the original wing without winglet
    span_total = 3.536
    span_blend = blended_span_distribution(cant)
    span_winglet = 0.3536
    wing_chord_root = 0.4713
    wing_chord_tip = 0.2357
    wing_sweep = 20

    ## Calculate the main wing geometry (first section)
    # Update main wing span (first section), taking into account the projected winglet span
    new_wing_span = wingspan_distribution(span_total, span_blend, span_winglet, cant*0.5, cant)
    new_wing_chord_tip = chord_distribution(new_wing_span, span_total, wing_chord_root, wing_chord_tip)

    winglet_taper_ratio = 0.2
    new_blended_chord_tip = chord_distribution( span_blend, span_blend + span_winglet, new_wing_chord_tip, new_wing_chord_tip * winglet_taper_ratio )

    if not os.path.exists('./winggen.vspscript'):
        print("No winggen.vspscript file found")
        sys.exit()

    
    with open("./winggen.vspscript", "r") as file:
        replaced_content = ""
        for line in file:
                # Section 1 - main wing: Change tip chord and span
            if "'Tip_Chord', 'XSec_1'" in line.strip():
                new_line = "SetParmVal(  wid, 'Tip_Chord', 'XSec_1', {0} );".format(str(new_wing_chord_tip))
            elif "'Span', 'XSec_1'" in line.strip():
                new_line = "SetParmVal(  wid, 'Span', 'XSec_1', {0} );".format(str(new_wing_span))

                # Section 2- blended section: Change root chord, tip chord, sweep, cant/dihedral
            elif "'Span', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(  wid, 'Span', 'XSec_2', {0} );".format(str(span_blend))
            elif "'Root_Chord', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(  wid, 'Root_Chord', 'XSec_2', {0} );".format(str(new_wing_chord_tip))
            elif "'Tip_Chord', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(  wid, 'Tip_Chord', 'XSec_2', {0} );".format(str(new_blended_chord_tip))
            elif "'Sweep', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(  wid, 'Sweep', 'XSec_2', {0} );".format(str(round((wing_sweep + sweep * 0.5), 4)))
            elif "'Dihedral', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(  wid, 'Dihedral', 'XSec_2', {0} );".format(str(round((cant * 0.5), 4)))

                # Sction 3 - winglet: Change root chord, sweep, cant/dihedral
            elif "'Root_Chord', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(  wid, 'Root_Chord', 'XSec_3', {0} );".format(str(new_blended_chord_tip))
            elif "'Tip_Chord', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(  wid, 'Tip_Chord', 'XSec_3', {0} );".format(str(new_wing_chord_tip * winglet_taper_ratio ))
            elif "'Sweep', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(  wid, 'Sweep', 'XSec_3', {0} );".format(str(round((wing_sweep + sweep), 4)))
            elif "'Dihedral', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(  wid, 'Dihedral', 'XSec_3', {0} );".format(str(round((cant), 4)))

            else:
                new_line = line.strip()
            replaced_content += new_line + "\n"
    
    with open("./winggen.vspscript", "w") as write_file:
        write_file.write(replaced_content)

    cmd_str = "/rds/general/user/jg2219/home/OpenVSP-compiled/OpenVSP-3.37.0-Linux/vspscript -script ./winggen.vspscript"
    subprocess.run(cmd_str, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-c', '--cant', type=float, help='Cant value')
    parser.add_argument('-s', '--sweep', type=float, help='Sweep value')
    args = parser.parse_args()

    if args.cant is None or args.sweep is None:
        parser.error("Please provide both cant and sweep values using -c/--cant and -s/--sweep")

    main(args.cant, args.sweep)
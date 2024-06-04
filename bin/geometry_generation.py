"""
    FYP: Automated aerodynamic shape optimisation of winglets with SU2 on Imperial HPC cluster

    Author: Jaime Galiana Herrera
    Date: 2024-06-03
    Description: Generates geometric models for CFD analysis. Distances in meters, angles in degrees.
"""

import os
import subprocess
from subprocess import PIPE
import numpy as np
import sys
import argparse

def chord_distribution(x, span_total, chord_root, chord_tip):
    """
    Calculate chord length at position x.
    
    Parameters:
        x (float): Position along the wingspan (m).
        span_total (float): Total wingspan (m).
        chord_root (float): Chord length at the root (m).
        chord_tip (float): Chord length at the tip (m).

    Returns:
        float: Chord length at position x (m).
    """
    return round((chord_tip - chord_root)/span_total * x + chord_root, 4)

def wingspan_distribution(span_total, span_blend, span_winglet, cant_blend, cant_winglet):
    """
    Calculate effective wingspan considering blended and winglet sections.
    
    Parameters:
        span_total (float): Total wingspan (m).
        span_blend (float): Span of the blended section (m).
        span_winglet (float): Span of the winglet section (m).
        cant_blend (float): Cant angle of the blended section (degrees).
        cant_winglet (float): Cant angle of the winglet section (degrees).

    Returns:
        float: Effective wingspan (m).
    """
    cant_blend = np.radians(cant_blend)
    cant_winglet = np.radians(cant_winglet)
    projected_span_blend = span_blend*np.cos(cant_blend)
    projected_span_winglet = span_winglet*np.cos(cant_winglet)
    if -np.radians(90) <= cant_winglet <= np.radians(90):
        return round(span_total - projected_span_blend - projected_span_winglet, 4)
    else:
        return round(span_total - projected_span_blend, 4)

def winglet_chord_distribution(x, span_total, chord_root, chord_tip):
    """
    Calculate chord length at position x for winglet.
    
    Parameters:
        x (float): Position along the winglet span (m).
        span_total (float): Total span including winglet (m).
        chord_root (float): Chord length at the root (m).
        chord_tip (float): Chord length at the tip (m).

    Returns:
        float: Chord length at position x (m).
    """
    return round((chord_tip - chord_root)/span_total * x + chord_root, 4)

def blended_span_distribution(cant):
    """
    Calculate span for blended section.
    
    Parameters:
        cant (float): Cant angle (degrees).

    Returns:
        float: Span of the blended section (m).
    """
    return round(0.01/9 * abs(cant) + 0.1, 4)

def main(cant, sweep):
    """
    Generate wing geometry including blended winglet.

    Parameters:
        cant (float): Cant angle for the winglet (degrees).
        sweep (float): Sweep angle for the winglet (degrees).

    Returns:
        .step: wing.stp
    """
    # Wing parameters
    span_total = 3.536  # meters
    span_blend = blended_span_distribution(cant)  # meters
    span_winglet = 0.3536  # meters
    wing_chord_root = 0.4713  # meters
    wing_chord_tip = 0.2357  # meters
    wing_sweep = 20  # degrees

    # Calculate geometry
    new_wing_span = wingspan_distribution(span_total, span_blend, span_winglet, cant * 0.5, cant)  # meters
    new_wing_chord_tip = chord_distribution(new_wing_span, span_total, wing_chord_root, wing_chord_tip)  # meters

    winglet_taper_ratio = 0.2
    new_blended_chord_tip = chord_distribution(span_blend, span_blend + span_winglet, new_wing_chord_tip, new_wing_chord_tip * winglet_taper_ratio)  # meters

    if not os.path.exists('./winggen.vspscript'):
        print("No winggen.vspscript file found")
        sys.exit()

    # Update script with new parameters
    with open("./winggen.vspscript", "r") as file:
        replaced_content = ""
        for line in file:
            if "'Tip_Chord', 'XSec_1'" in line.strip():
                new_line = "SetParmVal(wid, 'Tip_Chord', 'XSec_1', {0});".format(str(new_wing_chord_tip))
            elif "'Span', 'XSec_1'" in line.strip():
                new_line = "SetParmVal(wid, 'Span', 'XSec_1', {0});".format(str(new_wing_span))
            elif "'Span', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(wid, 'Span', 'XSec_2', {0});".format(str(span_blend))
            elif "'Root_Chord', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(wid, 'Root_Chord', 'XSec_2', {0});".format(str(new_wing_chord_tip))
            elif "'Tip_Chord', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(wid, 'Tip_Chord', 'XSec_2', {0});".format(str(new_blended_chord_tip))
            elif "'Sweep', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(wid, 'Sweep', 'XSec_2', {0});".format(str(round((wing_sweep + sweep * 0.5), 4)))
            elif "'Dihedral', 'XSec_2'" in line.strip():
                new_line = "SetParmVal(wid, 'Dihedral', 'XSec_2', {0});".format(str(round((cant * 0.5), 4)))
            elif "'Root_Chord', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(wid, 'Root_Chord', 'XSec_3', {0});".format(str(new_blended_chord_tip))
            elif "'Tip_Chord', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(wid, 'Tip_Chord', 'XSec_3', {0});".format(str(new_wing_chord_tip * winglet_taper_ratio))
            elif "'Sweep', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(wid, 'Sweep', 'XSec_3', {0});".format(str(round((wing_sweep + sweep), 4)))
            elif "'Dihedral', 'XSec_3'" in line.strip():
                new_line = "SetParmVal(wid, 'Dihedral', 'XSec_3', {0});".format(str(round((cant), 4)))
            else:
                new_line = line.strip()
            replaced_content += new_line + "\n"

    with open("./winggen.vspscript", "w") as write_file:
        write_file.write(replaced_content)

    # Run OpenVSP script
    cmd_str = "/path/to/OpenVSP-3.37.0-Linux/vspscript -script ./winggen.vspscript"
    subprocess.run(cmd_str, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate wing geometry with specified cant and sweep.')
    parser.add_argument('-c', '--cant', type=float, help='Cant angle (degrees)')
    parser.add_argument('-s', '--sweep', type=float, help='Sweep angle (degrees)')
    args = parser.parse_args()

    if args.cant is None or args.sweep is None:
        parser.error("Provide both cant and sweep values using -c/--cant and -s/--sweep")

    main(args.cant, args.sweep)
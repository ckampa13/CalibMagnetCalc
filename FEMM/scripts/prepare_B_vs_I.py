import sys
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
from plotting import config_plots
import ezdxf

config_plots()

# femm directory
femmdir = os.path.abspath(os.path.join(os.path.dirname(sys.path[0]), '.'))+'/' # directory above script is "FEMM/"
# femmdir = sys.path[0] # '/home/ckampa/Coding/CalibMagnetCalc/FEMM/'
print(femmdir)

# Units = mm
# Yoke Dimensions
Y_height = 864/2 # 864 is full height
Y_width = 667/2 # for distance to top in +z, +r quadrant
Y_thickness = 98
# Pole dimensions
P_radius = 250/2 # diameter is specified
P_length = 379
# Coil dimensions (Coil spec sheet)
C_radius0 = 153
C_radius1 = 318 # 467
C_length = 140

def calculate_nodes(gap=75, Y_height=Y_height, Y_width=Y_width, Y_thickness=Y_thickness,
                    P_radius=P_radius, P_length=P_length, C_radius0=C_radius0, C_radius1=C_radius1, C_length=C_length):
    # pole
    pole_nodes = [[0, gap/2], [0, gap/2+P_length], [P_radius, gap/2+P_length], [P_radius, gap/2]]
    pole_nodes_negative = [[0, -gap/2], [0, -(gap/2+P_length)], [P_radius, -(gap/2+P_length)], [P_radius, -gap/2]]
    # coil
    # NOTE: first 2 nodes are shared by yoke
    coil_nodes = [[C_radius0, Y_width-Y_thickness-C_length], [C_radius0, Y_width-Y_thickness], [C_radius1, Y_width-Y_thickness], [C_radius1, Y_width-Y_thickness-C_length]]
    coil_nodes_negative = [[C_radius0, -(Y_width-Y_thickness-C_length)], [C_radius0, -(Y_width-Y_thickness)], [C_radius1, -(Y_width-Y_thickness)], [C_radius1, -(Y_width-Y_thickness-C_length)]]
    # yoke
    yoke_nodes = [[P_radius, (Y_width-Y_thickness-C_length)], [P_radius, (Y_width)], [Y_height, (Y_width)],
                  [Y_height, -(Y_width)], [P_radius, -(Y_width)], [P_radius, -(Y_width-Y_thickness-C_length)],
                  [C_radius0, -(Y_width-Y_thickness-C_length)], [C_radius0, -(Y_width-Y_thickness)], [Y_height-Y_thickness, -(Y_width-Y_thickness)],
                  [Y_height-Y_thickness, (Y_width-Y_thickness)], [C_radius0, (Y_width-Y_thickness)], [C_radius0, (Y_width-Y_thickness-C_length)]]
    return pole_nodes, pole_nodes_negative, coil_nodes, coil_nodes_negative, yoke_nodes

def write_dxf(filename, pole_nodes, pole_nodes_negative, coil_nodes, coil_nodes_negative, yoke_nodes):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    for node_set in [pole_nodes, pole_nodes_negative, coil_nodes, coil_nodes_negative, yoke_nodes]:
        N_nodes = np.array(node_set).shape[0]
        # add a line between consecutive nodes (CAUTION: ordering important in calculations above!)
        for i in range(N_nodes-1):
            msp.add_line(node_set[i], node_set[i+1])
        # add between final node and first node
        msp.add_line(node_set[-1], node_set[0])

    doc.saveas(filename)
    print(f"Saved Geometry File As: {filename}")

def generate_lua(templatefile, outputfile, args):
    # read in template file
    with open(templatefile, 'r') as f:
        lines = f.readlines()
    # search for lines to replace
    lines_new = []
    for line in lines:
        if "-- TEMPLATE --" in line:
            lines_new.append(f"-- RUN FILE --\n")
        elif "gap =" in line:
            lines_new.append(f"gap = {args.gap} -- A\n")
        elif "min_i =" in line:
            lines_new.append(f"min_i = {args.current_i} -- A\n")
        elif "max_i =" in line:
            lines_new.append(f"max_i = {args.current_f} -- A\n")
        elif "increment =" in line:
            lines_new.append(f"increment = {args.current_d} -- A\n")
        else:
            lines_new.append(line)
    # write to outputfile
    with open(outputfile, 'w+') as f:
        for l in lines_new:
            f.write(l)
    print(f"Used Lua file: {templatefile}")
    print(f"Wrote Lua file: {outputfile}")

def plot_geom(fnamebase, gap, pole_nodes, pole_nodes_negative, coil_nodes, coil_nodes_negative, yoke_nodes):
    fig, ax = plt.subplots(figsize=(6,8))
    ax.fill(*np.array(coil_nodes).T, color='green', label='Solenoid Coils')
    ax.fill(*np.array(coil_nodes_negative).T, color='green')
    ax.fill(*np.array(pole_nodes).T, color='gray', label='Poles')
    ax.fill(*np.array(pole_nodes_negative).T, color='gray')
    ax.fill(*np.array(yoke_nodes).T, color='yellow', label='Yoke')
    ax.set_xlabel('r [mm]')
    ax.set_ylabel('z [mm]')
    ax.set_title(f'FEMM Nodes: Gap = {gap} mm')
    ax.legend()
    ax.xaxis.set_major_locator(MultipleLocator(100))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(20))
    ax.yaxis.set_major_locator(MultipleLocator(100))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_minor_locator(MultipleLocator(20))
    plt.gca().set_aspect('equal', adjustable='box')
    fig.savefig(fnamebase+'.pdf')
    fig.savefig(fnamebase+'.png')
    print(f"Saved plots: {fnamebase}[.pdf, .png]")
    return fig, ax


if __name__=='__main__':
    # parse agruments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gap', help='Pole gap [mm] (Range: 0-150)')
    parser.add_argument('-i', '--current_i', help='Current start of range [A]')
    parser.add_argument('-f', '--current_f', help='Current end of range [A]')
    parser.add_argument('-d', '--current_d', help='Current increment (delta_Current) [A]')
    args = parser.parse_args()
    # set defaults
    if args.current_i is None:
        args.current_i = 0
    else:
        args.current_i = float(args.current_i)
    if args.current_f is None:
        args.current_f = 200
    else:
        args.current_f = float(args.current_f)
    if args.current_d is None:
        args.current_d = 20
    else:
        args.current_d = float(args.current_d)
    if args.gap is None:
        args.gap = 75
    else:
        args.gap = int(args.gap)
    # check value is in valid range
    if (args.gap < 0) or (args.gap > 150):
        raise ValueError(f'Invalid gap value: {args.gap} is not in the range [0, 150].')
    # calculate ordered nodes
    pole_nodes, pole_nodes_negative, coil_nodes, coil_nodes_negative, yoke_nodes = calculate_nodes(gap=args.gap)
    # output "line" elements in a DXF file
    write_dxf(femmdir+f'geom/GMW_{args.gap}mm.dxf', pole_nodes, pole_nodes_negative, coil_nodes, coil_nodes_negative, yoke_nodes)
    # create lua script from template
    generate_lua(femmdir+'scripts/templates/B_vs_I_r0z0_TEMPLATE.lua', femmdir+'scripts/run.lua', args)
    # make a plot to visually check geometry
    fig, ax = plot_geom(femmdir+f'scripts/plots/GMW_{args.gap}mm_mpl', args.gap, pole_nodes, pole_nodes_negative, coil_nodes, coil_nodes_negative, yoke_nodes)
    plt.show()

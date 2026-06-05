import streamlit as st # GUI library
import numpy as np 
import matplotlib.pyplot as plt
import trimesh
import subprocess
import ctypes
import os

# Create app title
st.title("Force Calculator from cutter-workpiece engagement")

# User uploaded files
st.subheader("User uploaded files")

bulk_media = st.file_uploader("Upload bulk media", 
                              type=["stl"] # Only accept stl file
)

tool_path = st.file_uploader("Upload toolpath",
                            type=["nc","gcode"] 
)

# User inputed values
st.subheader("User inputed values")
tool_radius = st.number_input("Tool radius R [m]", 
                              value = 5.0
)

helix_angle_degrees = st.number_input("Helix angle gamma [deg]",
                                      value = 30
)

# Convert Helix angle to radians

helix_angle_radians = helix_angle_degrees * np.pi / 180

flute_length = st.number_input("Flute length [m]",
                               value = 0.5)

handle_length = st.number_input("Handle length [m]",
                                value = 0.5)


number_of_flutes = st.number_input("Number of flutes",
                                   min_value = 1,
                                   value = 2,
                                   step=1 # Specfies integer
)
lead_angle = st.number_input("Lead angle [deg]",
                             value = 0)
tilt_angle = st.number_input("Tilt angle [deg]",
                             value=0)

# Cutter Constants
st.subheader("Cutter Constants")
K_rc = st.number_input("K_rc",
                       value = 1)
K_re = st.number_input("K_re",
                       value = 1)
K_psic = st.number_input("K_psic",
                         value = 1)
K_psie = st.number_input("K_psie",
                         value = 1)
K_tc = st.number_input("K_tc",
                       value = 1)
K_te = st.number_input("K_te",
                       value = 1)
st.subheader("Discretization")
dz = st.number_input("Axial Spacing along tool dz [m]",
                     value = 0.05
)
dtheta_deg = st.number_input("Angle spacing dtheta [deg]",
                             value = 1
)

# Run Edgar's code below
if st.button("Done"):
    x = 1

# Pass number of flutes N_f
# helix angle gamma
# tool radius R into appropriate variables
N_f = int(number_of_flutes)
gamma = helix_angle_degrees
R = tool_radius

lead_angle_rad = lead_angle * np.pi/180
tilt_angle_rad = tilt_angle * np.pi/180
lead = lead_angle_rad
tilt = tilt_angle_rad

# Convert angular spacing from degrees to radians

dtheta_rad = dtheta_deg * np.pi / 180

file_path = "Tool_parameters.txt"

# Parse user inputted g code file

tool_path_points = []

def parse_gcode(tool_path):

    lines = tool_path.getvalue().decode("utf-8").splitlines() # Convert g code into readable lines

    # Store cutter position                  
    current_x = 0.0
    current_y = 0.0
    current_z = 0.0

    for line in lines: # Loop through every line in the g code file
    
        if line.startswith("G0") or line.startswith("G1"): # Proper g code lines start with this

            # Split line into pieces
            # "G1 X5 Y2 Z0" into ["G1", "X5", "Y2", "Z0"]
            line = line.replace(","," ")
            words = line.split()

            for word in words:

                # word[1:] means take everything except the first character
                if word.startswith("X"):
                    current_x = float(word[1:]) 

                elif word.startswith("Y"):
                    current_y = float(word[1:])

                elif word.startswith("Z"):
                    current_z = float(word[1:])
            
            tool_path_points.append(
                [current_x, current_y, current_z]
            )

    return tool_path_points

with open(file_path, "w") as f:
    f.write(str(tool_radius) + "\n")
    f.write(str(helix_angle_degrees) + "\n")
    f.write(str(flute_length) + "\n")
    f.write(str(handle_length) + "\n")
    f.write(str(number_of_flutes) + "\n")
    f.write(str(lead_angle) + "\n")
    f.write(str(tilt_angle) + "\n")
    f.write(str(dz) + "\n")
    f.write(str(dtheta_deg) + "\n")

st.success(f"Saved update to {file_path}")

# Functions for finding angles for transformation of forces for a given point
# INPUT ANGLES IN RADIANS
def psi_z(z,R,gamma):
    # Give height z, tool radius R, and helix angle gamma
    return z/(R*np.tan(gamma))

def theta_nzN_f(n,z,N_f,R,gamma):
    # Give flute index n, height z, number of flutes N_f, tool radius R, and helix angle gamma
    return 2*np.pi*(n-1)/N_f - psi_z(z,R,gamma)

# Functions for calculating transformation matrices

def A(psi,theta):
    # Input psi_z and theta_nzN_f functions above
    matrix = np.array([
                      [-np.sin(psi)*np.sin(theta), -np.cos(psi)*np.sin(theta), -np.cos(theta)],
                      [np.sin(psi)*np.cos(theta), np.cos(psi)*np.cos(theta), -np.sin(theta)],
                      [np.cos(psi), -np.sin(psi), 0]
                      ])
    return matrix

def B(gamma):
    matrix = np.array([
                        [np.cos(gamma), -np.sin(gamma),0],
                        [np.sin(gamma), np.cos(gamma), 0],
                        [0, 0, 1]
    ])
    return matrix

# T matrix. For flat end-mill most of the time lead=tilt=0
# Just assume we are in line with the global z axis

def T(lead, tilt):
    matrix = np.array([
        [np.cos(lead), np.sin(tilt)*np.sin(lead), -np.cos(tilt)*np.sin(lead)],
        [0, np.cos(tilt), np.sin(tilt)],
        [np.sin(lead), -np.sin(tilt)*np.cos(lead), np.cos(tilt)*np.cos(lead)]
    ])
    return matrix

# Define de_casteljau function
def de_casteljau_curve(points, weights, t):
    points = np.array(points, dtype=float)
    weights = np.array(weights, dtype=float)

    # Convert to weighted control points

    weighted_points = points * weights[:,None]  # Changes [1,2,1] to 
                                                # [[1],
                                                #  [2],
                                                #  [1]]

    for r in range(1, len(points)):
        weighted_points[:-r] = (
            (1 - t) * weight_points[:-r]
            + t * weighted_points[1:len(points) - r + 1]
        )

        weights[:-r] = (
            (1 - t) * weights[:-r]
            + t * weights[1 : len(weights) - r + 1]
        )
    
    return weighted_points[0] / weights [0]

def run_force_calculation(tool_path_points_ref,cylinder_points, flute_array):
    # Load bulk media
    if bulk_media is not None:
        bulk = trimesh.load_mesh(
        bulk_media,
        file_type="stl"
        )
    else: 
        st.error("Please upload an STL file first")
        return [],[],[],[]

    st.write("Running force calculation")

    # Find differential Area element

    dA = tool_radius * dtheta_rad * dz

    st.write("Tool differential area element dA:",dA)

    # Initialize force array
    F_X = []
    F_Y = []
    F_Z = []

    # Initialize CWE array
    CWE_array = []

    # Create cutter mesh for boolean operation

    cutter_mesh = trimesh.creation.cylinder(
        radius=tool_radius,
        height=flute_length,
        sections = int(round(2*np.pi / dtheta_rad)) # Sections are angular 
    )

    # Move cutter so that bottom dead center is at (0,0,0)
    cutter_mesh.apply_translation([0,0,flute_length/2])

    for tool_position in tool_path_points_ref:
        tool_position = np.array(tool_position) 

        # Translate cylinder points by first making a copy
        cylinder_points_copy = cylinder_points.copy()

        # Bottom dead center of cylinder is (0,0,0). Translate by adding global tool position
        cylinder_points_copy_global = cylinder_points_copy + tool_position

        # Find intersecting points and then calculate total CWE_area
        engaged_points_boolean_mask = bulk.contains(cylinder_points_copy_global)
        CWE_area = engaged_points_boolean_mask.sum()*dA

        # Append to CWE array
        CWE_array.append(CWE_area)
        
        # Calculate forces F_r, F_psi, and F_t for each point and then transform into F_X, F_Y, and F_Z
        flute_counter = 0

        # Current F_X, F_Y, and F_Z forces
        F_X_current = 0
        F_Y_current = 0
        F_Z_current = 0

        for flute_points in flute_array:
            flute_counter += 1
            # Move local helix point into global coordinates
            global_flute_points = flute_points + tool_position

            # Check intersection of helix points with stock
            engaged_mask = bulk.contains(global_flute_points)

            # Output engaged points in local coordinates
            engaged_flute_points_local = flute_points[engaged_mask]
            num_engaged_flute_points = engaged_flute_points_local.shape[0]

            # Avoid dividing by 0 if there are no engaged flute points
            if num_engaged_flute_points == 0:
                continue

            # Define new dA by distributing over flutes and then distributing over points
            new_dA = (CWE_area/N_f)/num_engaged_flute_points

            for local_flute_point in engaged_flute_points_local:
                dF_r = K_rc*new_dA + K_re*dz
                dF_psi = K_psic*new_dA + K_psie*dz
                dF_t = K_tc*new_dA + K_te*dz

                # Create force array
                force_array = np.array([
                    [dF_r],
                    [dF_psi],
                    [dF_t]
                ])

                # Get the z coordinate of the local flute point
                z = local_flute_point[2]
                psi = psi_z(z,R,gamma)
                theta = theta_nzN_f(flute_counter,z,N_f,R,gamma)

                # Calculate forces in global coordinates
                dF_XYZ_array = T(lead,tilt) @ B(gamma) @ A(psi, theta) @ force_array

                # Update forces
                F_X_current += dF_XYZ_array[0,0] # Make sure we result in a scalar
                F_Y_current += dF_XYZ_array[1,0]
                F_Z_current += dF_XYZ_array[2,0] 
    
        # Update forces at current point in tool path

        F_X.append(F_X_current)
        F_Y.append(F_Y_current)
        F_Z.append(F_Z_current)
    
        # Update bulk media after current tool position
        cutter_current = cutter_mesh.copy()
        cutter_current.apply_translation(tool_position)

        # Boolean operation if cutter intersects stock
        if CWE_area > 0:
            try:
                bulk_cut = trimesh.boolean.difference(
                    [bulk,cutter_current],
                    engine="manifold"
                )

                # Update bulk with successful cut
                if bulk_cut is not None:
                    bulk = bulk_cut

            except Exception as e:
                st.warning(f"Boolean cut failed at tool position {tool_position}: {e}")

    return F_X, F_Y, F_Z, CWE_array

# Define button to run force calculation function above


if st.button("Run Force Calculation"):

    if tool_path is not None:

        # We will generate a circle using rational quadratic Bezier
        # Then evaluate via De Casteljau
        # and extrude in the z direction

        # Define number of arc points 
        # from dtheta_rad
        num_arc_points = int(2 * np.pi / dtheta_rad)
        num_quarter_points = num_arc_points // 4

        # Define control points
        P_list = np.array([
            [1,0],
            [1,1],
            [0,1]
        ])

        # Define weights

        weights = np.array([
            1,
            1 / np.sqrt(2),
            1
        ])

        # Evaluate quarter circle points

        quarter_points = []

        for i in range(num_arc_points + 1): 
            t = i / num_quarter_points # t in [0,1]
            quarter_points.append(de_casteljau_curve(P_list, weights, t))

        # Scale by radius
        quarter_points = R * quarter_points

        # Get points of entire circle by rotations
        circle_points = []

        for q in range(4): # range = [0,1,2,3]
            # rotation angle [rad]
            angle = q * np.pi/2

            # rotation matrix
            rotation_matrix = np.array([
                [np.cos(angle),np.sin(angle)],
                [-np.sin(angle), np.cos(angle)]
            ])

            if q == 0:
                intermediate_points = quarter_points
            else:
                intermediate_points = quarter_points[1:] # skip first duplicate boundary point
            
            rotated_points = (rotation_matrix @ intermediate_points.T).T

            circle_points.append(rotated_points)
    
        circle_points = np.vstack(circle_points) # Concatenates vectors row-wise

        # Remove final duplicate point

        circle_points = circle_points[:-1]    # a[1:]   everything except first element
                                            # a[:-1]  everything except last element
                                            # a[:]    entire array
                                            # a[1:-1] everything except first and last

        # Extrude in z

        z_values = np.arange(0,flute_length + dz, dz)

        # Intialize cylinder points

        cylinder_points = []
        
        for z in z_values:
            for p in circle_points:
                cylinder_points.append([p[0], p[1], z])
        
        cylinder_points = np.array(cylinder_points)

        # Build flute_array below

        tool_path_points = parse_gcode(tool_path)

        Fx_list, Fy_list, Fz_list, CWE_array = run_force_calculation(tool_path_points,cylinder_points)

        # Size of tool_path
        tool_path_size = len(tool_path_points)

        tool_path_array_plot = np.arange(1, tool_path_size + 1)

        # Plot graph of forces 

        fig, ax = plt.subplots()
            
        ax.plot(
            tool_path_array_plot,
            Fx_list,
            label="Fx"
        )

        ax.plot(
            tool_path_array_plot,
            Fy_list,
            label="Fy"
        )

        ax.plot(
            tool_path_array_plot,
            Fz_list,
            label="Fz"
        )

        ax.set_title("Cutting Forces")
        ax.set_xlabel("Toolpath point")
        ax.set_ylabel("Force")
        ax.grid(True)
        ax.legend()

        st.pyplot(fig)

        # Plot graph of CWE

        fig, ax = plt.subplots()

        ax.plot(
            tool_path_array_plot,
            CWE_array,
            label="CWE area"
        )

        ax.set_title("Cutter Workpiece Engagement Area")
        ax.set_xlabel("Toolpath point")
        ax.set_ylabel("Area")
        ax.grid(True)
        ax.legend()

        st.pyplot(fig)

    else:
        st.error("No G-code toolpath file uploaded. Please upload now.")
        
# Button for plotting

if st.button("Show Sample Plot"):

    sample_array = np.ones(200)

    fig, ax = plt.subplots()

    ax.plot(sample_array,sample_array,color="blue")
    ax.set_title("Sample Plot")
    ax.set_xlabel("x axis")
    ax.set_ylabel("y axis")
    ax.grid(True)

    st.pyplot(fig)
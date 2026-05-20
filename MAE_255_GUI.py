import streamlit as st # GUI library
import numpy as np 
import pyvista as pv # Handles 3D meshes and plotting
from stpyvista import stpyvista

# Create app title
st.title("Force Calculator from cutter-workpiece engagement")

# User uploaded files
st.subheader("User uploaded files")

bulk_media = st.file_uploader("Upload bulk media", 
                              type=["step", "stp"] # Want exact CAD geometries, so only "step" and "stp" files
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

st.subheader("Discretization")
dz = st.number_input("Axial Spacing along tool dz [m]",
                     value = 0.05
)
dtheta_deg = st.number_input("Angle spacing dtheta [deg]",
                             value = 1
)

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

st.success(f"Saved update to {file_path}")

def run_force_calculation():
    st.write("Running force calculation")

    # Find differential Area element

    dA = 0.01

    st.write("Tool differential area element:",dA)

    # Find forces 


# Define button to run force calculation function above

if st.button("Run Force Calculation and include slider"):

    run_force_calculation()

    if tool_path is not None:
    
        tool_path_points = parse_gcode(tool_path)

        st.subheader("Toolpath Animation Slider")

        frame = st.slider(
            "Toolpath Frame",
            min_value = 0,
            max_value = len(tool_path_points) - 1,
            value = 0,
            step = 1
        )
    
        current_tool_position = tool_path_points[frame]

        st.write("Current tool position:")
        st.write(current_tool_position)

        points = np.array(tool_path_points)

        plotter = pv.Plotter(window_size=[800,600])

        plotter.add_lines(points,width=3)

        cutter_marker = pv.Cylinder(
            center=current_tool_position,
            direction=(0,0,1),
            radius=tool_radius,
            height=flute_length + handle_length,
            resolution=60
        )
        plotter.add_mesh(cutter_marker)

        plotter.add_axes()
        plotter.view_isometric()

        stpyvista(plotter, backend="html")
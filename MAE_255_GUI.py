import streamlit as st # GUI library
import numpy as np 

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

number_of_flutes = st.number_input("Number of flutes",
                                   min_value = 1
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
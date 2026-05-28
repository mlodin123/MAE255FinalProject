import trimesh
import numpy as np

step_path = r"C:\Users\mirwa\Downloads\Taylor_Lab\Rear Pan Support Rod End Attachment Bracket.step"
stl_path = r"C:\Users\mirwa\Downloads\Taylor_Lab\Rear Pan Support Rod End Attachment Bracket.stl"

# Load stl file
bulk = trimesh.load(stl_path)

# Specify radius and height of cutter
radius = 5
height = 20

cutter = trimesh.creation.cylinder(
    radius = radius,
    height = height,
    sections = 128 # sections number of wedges wrapped around the axis to approximate a cylinder
                   # dtheta = 2pi/(sections)
)
# The cylinder axis is aligned along global z axis
# z in [-H/2,H/2]

# Translate cylinder upward
cutter.apply_translation([0,0,height/2])
# z in [0,H]

# Discretize points along the outer surface of the cylinder
n_theta = 360 # Around cutter circumference
n_z = 200 # Along cutter height

# Theta discretization
theta_vals = np.linspace(0,2*np.pi,n_theta,endpoint=False) # endpoint=False so that we don't include the final value
# z discretization
z_vals = np.linspace(0,height,n_z)

# Generate points on cylinder

cylinder_points =[]
for z in z_vals:
    for theta in theta_vals:
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)

        cylinder_points.append([x,y,z])

cylinder_points = np.array(cylinder_points)

# Above Edgar will write code for generating Bezier surface of cylinder and curve and then generate point cloud

# Cut stock with tool for given tool path
tool_path = []
result = bulk # Loaded stl file

# Calculate CWE area
dtheta = 2*np.pi/n_theta
dz = height/(n_z - 1) # subtract 1 because we contain top and bottom

dA = radius * dtheta * dz

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

# T matrix to add lead and tilt angle later
# Just assume we are in line with the global z axis

def T(lead, tilt):
    matrix = np.array([
        [np.cos(lead), np.sin(tilt)*np.sin(lead), -np.cos(tilt)*np.sin(lead)],
        [0, np.cos(tilt), np.sin(tilt)],
        [np.sin(lead), -np.sin(tilt)*np.cos(lead), np.cos(tilt)*np.cos(lead)]
    ])
    return matrix

# Initialize force array
F_X = []
F_Y = []
F_Z = []

# Initialize CWE array
CWE_array = []

# Specify cutter constants
K_rc = 1
K_re = 1
K_psic = 1
K_psie = 1
K_tc = 1
K_te = 1

lead = 0
tilt = 0
gamma = np.pi/2
N_f = 2
R = 0.1

for tool_position in tool_path:
    tool_position = np.array(tool_position) 

    # Translate cylinder points by first making a copy
    cylinder_points_copy = cylinder_points.copy()
    cylinder_points_copy_global = cylinder_points_copy + tool_position # Assume that the cutter is pointing downward

    # Find intersecting points and then calculate total CWE_area
    engaged_points_boolean_mask = bulk.contains(cylinder_points_copy_global)
    CWE_area = engaged_points_boolean_mask.sum()*dA

    # Append to CWE array
    CWE_array.append(CWE_area)

    #engaged_local_points = cylinder_points_copy[engaged_points_boolean_mask]
    
    # Calculate forces F_r, F_psi, and F_t for each point and then transform into F_X, F_Y, and F_Z
    flute_counter = 0
    flute_array = []

    # Current F_X, F_Y, and F_Z forces
    F_X_current = 0
    F_Y_current = 0
    F_Z_current = 0

    for flute_points in flute_array:
        flute_counter += 1
        # Move helix point into global coordinates
        global_flute_points = flute_points + tool_position

        # Check intersection of helix points with stock
        engaged_mask = bulk.contains(global_flute_points)

        # Output engaged points in local coordinates
        engaged_flute_points_local = flute_points[engaged_mask]

        for local_flute_point in engaged_flute_points_local:
            dF_r = K_rc*dA + K_re*dz
            dF_psi = K_psic*dA + K_psie*dz
            dF_t = K_tc*dA + K_te*dz

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

    # Output machined stock at each interval
    # Find translated cutter
    translated_cutter = cutter.copy() # copy cutter
    translated_cutter.apply_translation(tool_position)
    result = bulk.difference(translated_cutter, engine="manifold") # result = bulk - cutter
    
    # Update bulk
    bulk = result

# Output total machined stock
output_export_path = "bulk_cut.stl"
result.export(output_export_path)
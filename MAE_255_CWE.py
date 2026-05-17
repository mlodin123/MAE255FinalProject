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

# Cut stock with tool for given tool path
tool_path = []
result = bulk
for tool_position in tool_path:
    tool_position = np.array(tool_position)
    cylinder_points_global = cylinder_points + tool_position

    engaged_points_boolean_mask = bulk.contains(cylinder_points_global)
    engaged_points = cylinder_points_global[engaged_points_boolean_mask]

    # Calculate CWE area
    dtheta = 2*np.pi/n_theta
    dz = height/(n_z - 1) # subtract 1 because we contain top and bottom

    dA = radius * dtheta * dz

    CWE_area = engaged_points_boolean_mask.sum()*dA

    # Output machined stock at each interval
    result = bulk.difference(cutter, engine="manifold") # result = bulk - cutter

# Output total machined stock
result.export("bulk_cut.stl")



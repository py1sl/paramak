import openmc
import numpy as np
import math
import paramak

openmc.config['cross_sections'] = '/nuclear_data/cross_sections.xml' # change this to the dir of your cross_sections.xml

my_reactor = paramak.tokamak_from_plasma(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30), # layer_1
        (paramak.LayerType.SOLID, 50), # layer_2
        (paramak.LayerType.SOLID, 10), # layer_3
        (paramak.LayerType.SOLID, 120), # layer_4
        (paramak.LayerType.SOLID, 20), # layer_5
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300), # plasma
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20), # layer_3
        (paramak.LayerType.SOLID, 120), # layer_4
        (paramak.LayerType.SOLID, 10), # layer_5
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,
)
my_reactor.save(f"tokamak_minimal.step")
print(f"Saved as tokamak_minimal.step")
my_reactor=my_reactor.remove(name='plasma')

# this prints all the names of the parts in the reactor
print(my_reactor.names())

from cad_to_dagmc import CadToDagmc
my_model = CadToDagmc()
material_tags = ["layer_1", "layer_2", "layer_3", "layer_4", "layer_5"]

# 6 material tags as inner and outer layers are one solid there are only 6 solids in model
my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)

from pathlib import Path
script_path = Path(__file__).resolve()
script_folder = script_path.parent
h5m_filename =  script_folder/"dagmc.h5m"
# my_model.export_dagmc_h5m_file(filename=h5m_filename, min_mesh_size=10.0, max_mesh_size=20.0)

# simplified material definitions have been used to keen this example minimal
mat_layer_1 = openmc.Material(name='layer_1')
mat_layer_1.add_element('Cu', 1, "ao")
mat_layer_1.set_density("g/cm3", 7)

mat_layer_2 = openmc.Material(name='layer_2')
mat_layer_2.add_nuclide('W186', 1, "ao")
mat_layer_2.set_density("g/cm3", 0.01)

mat_layer_3 = openmc.Material(name='layer_3')
mat_layer_3.add_nuclide('Fe56', 1, "ao")
mat_layer_3.set_density("g/cm3", 7)

mat_layer_4 = openmc.Material(name='layer_4')
mat_layer_4.add_element('Li', 1, "ao")
mat_layer_4.set_density("g/cm3", 0.5)

mat_layer_5 = openmc.Material(name='layer_5')
mat_layer_5.add_nuclide('Fe56', 1, "ao")
mat_layer_5.set_density("g/cm3", 7)

mat_concrete = openmc.Material(name='concrete')
mat_concrete.add_nuclide('Fe56', 1, "ao")
mat_concrete.set_density("g/cm3", 7)


materials = openmc.Materials([mat_layer_1, mat_layer_2, mat_layer_3, mat_layer_4, mat_layer_5, mat_concrete])

wedge_angles = (0, 180)

dag_univ = openmc.DAGMCUniverse(filename=h5m_filename)

bioshield_to_reactor_gap = 500
bioshield_radial_thickness = 200
z_padding = 400

bbox = dag_univ.bounding_box

dagmc_radius = max(abs(bbox[0][0]), abs(bbox[0][1]), abs(bbox[1][0]), abs(bbox[1][1]))

bioshield_inner_surface = openmc.ZCylinder(r=dagmc_radius+bioshield_to_reactor_gap, surface_id=1000)

wedge_angle_surf_1 = openmc.Plane(
    a=math.sin(math.radians(wedge_angles[0])),
    b=-math.cos(math.radians(wedge_angles[0])),
    c=0.0,
    d=0.0,
    boundary_type='reflective',
    surface_id=1001
)

wedge_angle_surf_2 = openmc.Plane(
    a=math.sin(math.radians(wedge_angles[1])),
    b=-math.cos(math.radians(wedge_angles[1])),
    c=0.0,
    d=0.0,
    boundary_type='reflective',
    surface_id=1002
)

lower_z = openmc.ZPlane(0, surface_id=1003)
upper_z = openmc.ZPlane(abs(bbox[0][2])+bbox[1][2], surface_id=1004)
# lower_z = openmc.ZPlane(bbox[0][2], boundary_type='vacuum', surface_id=1003)
# upper_z = openmc.ZPlane(bbox[1][2], boundary_type='vacuum', surface_id=1004)


wedge_region = (
        -bioshield_inner_surface
        & +lower_z
        & -upper_z
        & (-wedge_angle_surf_1 | +wedge_angle_surf_2)
    )


bounding_cell = openmc.Cell(
    fill=dag_univ,
    cell_id=1000,
    region=wedge_region
)
# moving the geometry so that the bottom of is at z=0
# to do this we need to move the geometry up as it is centered around z=0
# we also need to move it up so the the start of the earth layer is at z=0
dagmc_geometry_offset = abs(bbox[0][2])
bounding_cell.translation = (0,0,dagmc_geometry_offset)


floor_lower_surface = openmc.ZPlane(z0=0, boundary_type='vacuum', surface_id=1005)
bioshield_outer_surface = openmc.ZCylinder(r=dagmc_radius+bioshield_to_reactor_gap, boundary_type='vacuum', surface_id=1006)

bioshield_region = -bioshield_outer_surface & +bioshield_inner_surface & +lower_z & -upper_z & (-wedge_angle_surf_1 | +wedge_angle_surf_2)
bioshield_cell = openmc.Cell(region=bioshield_region, fill=mat_concrete, cell_id=1001)

floor_region = -lower_z & +floor_lower_surface & -bioshield_outer_surface & (-wedge_angle_surf_1 | +wedge_angle_surf_2)
floor_cell = openmc.Cell(region=floor_region, fill=mat_concrete, cell_id=1002)

geometry = openmc.Geometry([bounding_cell, floor_cell, bioshield_cell])

# import matplotlib.pyplot as plt
# geometry.plot()
# plt.show

# initializes a new source object
my_source = openmc.IndependentSource()

# initialises a new source object
my_source = openmc.IndependentSource()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([my_reactor.major_radius], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=np.pi)

# this makes the ring source using the three distributions and a radius
my_source.space = openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0))

# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()

# sets the energy distribution to a Muir distribution neutrons
my_source.energy = openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)


# specifies the simulation computational intensity
settings = openmc.Settings()
settings.batches = 10
settings.particles = 10000
settings.run_mode = "fixed source"
settings.source = my_source

# adds a tally to record the heat deposited in a mesh overlaid over entire geometry

mesh = openmc.RegularMesh().from_domain(geometry)
mesh.dimension=[100, 100, 100]
mesh_tally = openmc.Tally(name="heating")
mesh_tally.filters=[openmc.MeshFilter(mesh)]
mesh_tally.scores = ["heating"]
tallies = openmc.Tallies([mesh_tally])

# # builds the openmc model
my_model = openmc.Model(materials=materials, geometry=geometry, settings=settings, tallies=tallies)

# # starts the simulation
output_file = my_model.run()

# # loads up the output file from the simulation
statepoint = openmc.StatePoint(output_file)

my_heating_mesh_tally = statepoint.get_tally(name="heating")

mesh.write_data_to_vtk(
    datasets={'mean': my_heating_mesh_tally.mean.flatten()},
    filename='structured_mesh_tally_results.vtk',
)

print('VTK file saved to structured_mesh_tally_results.vtk')
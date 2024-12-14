import openmc

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

# this prints all the names of the parts in the reactor
for part in my_reactor:
    print(part[1])

from cad_to_dagmc import CadToDagmc
my_model = CadToDagmc()
material_tags = ["layer_1", "layer_2", "layer_3", "layer_4", "layer_5", "plasma"]

# 6 material tags as inner and outer layers are one solid there are only 6 solids in model
my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)

h5m_filename = "dagmc.h5m"
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

mat_plasma = openmc.Material(name='plasma')
mat_plasma.add_nuclide('Fe56', 1, "ao")
mat_plasma.set_density("g/cm3", 7)


materials = openmc.Materials([mat_layer_1, mat_layer_2, mat_layer_3, mat_layer_4, mat_layer_5, mat_plasma])



dag_univ = openmc.DAGMCUniverse(filename=h5m_filename)
bound_dag_univ = dag_univ.bounded_universe()
geometry = openmc.Geometry(root=bound_dag_univ)

# initializes a new source object
my_source = openmc.IndependentSource()

# initialises a new source object
my_source = openmc.IndependentSource()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([10], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=2* 3.14159265359)

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

mesh = openmc.RegularMesh().from_domain(bound_dag_univ)
mesh.dimension=[100, 100, 100]
mesh_tally = openmc.Tally(name="flux")
mesh_tally.filters=[openmc.MeshFilter(mesh)]
mesh_tally.scores = ["flux"]
tallies = openmc.Tallies([mesh_tally])

# # builds the openmc model
my_model = openmc.Model(materials=materials, geometry=geometry, settings=settings, tallies=tallies)

# # starts the simulation
output_file = my_model.run()

# # loads up the output file from the simulation
statepoint = openmc.StatePoint(output_file)

my_flux_mesh_tally = statepoint.get_tally(name="flux")

mesh.write_data_to_vtk(
    datasets={'mean': my_flux_mesh_tally.mean.flatten()},
    filename='mesh_tally_results.vtk',
)
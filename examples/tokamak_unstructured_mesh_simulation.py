from example_util_functions import transport_particles_on_h5m_geometry

import paramak
import openmc


openmc.config["cross_sections"] = '/nuclear_data/cross_sections.xml'

my_reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP, 10),  # inner bore
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 50), 
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 120),  # breeder
        (paramak.LayerType.SOLID, 10), # first wall
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),  # plasma
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10), # first wall
        (paramak.LayerType.SOLID, 120), # breeder
        (paramak.LayerType.SOLID, 10),
    ],
    vertical_build=[
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 100),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 700),  # plasma
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 100),
        (paramak.LayerType.SOLID, 15),
    ],
    triangularity=0.55,
    rotation_angle=180,
)

my_reactor.save(f"tokamak_minimal.step")
print(f"Saved as tokamak_minimal.step")
my_reactor=my_reactor.remove(name="plasma")  # removing as we don't need the plasma for this neutronics simulation

from cad_to_dagmc import CadToDagmc
my_model = CadToDagmc()
material_tags = ["mat1"] * 5  # as inner and outer layers are one solid there are only 6 solids in model
my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)
my_model.export_dagmc_h5m_file(min_mesh_size=10.0, max_mesh_size=20.0, filename="dagmc.h5m")
my_model.export_unstructured_mesh_file(min_mesh_size=10.0, max_mesh_size=20.0, filename="unstructured_mesh.vtk")

h5m_filename = "dagmc.h5m"


mat1 = openmc.Material(name='mat1')
mat1.add_nuclide('Fe56', 1, "ao")
mat1.set_density("g/cm3", 0.01)

materials = openmc.Materials([mat1])


dag_univ = openmc.DAGMCUniverse(filename=h5m_filename)
bound_dag_univ = dag_univ.bounded_universe()
geometry = openmc.Geometry(root=bound_dag_univ)

# initializes a new source object
my_source = openmc.IndependentSource()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([my_reactor.major_radius], [1])

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
settings = openmc.Settings(batches = 10, particles = 10000,run_mode = "fixed source")
settings.source = my_source

mesh = openmc.UnstructuredMesh(filename='unstructured_mesh.vtk', library='moab',mesh_id = 1)

# adds a tally to record the heat deposited in entire geometry
mesh_tally = openmc.Tally(name="flux")
mesh_tally.filters = [openmc.MeshFilter(mesh)]
mesh_tally.scores = ["flux"]

# groups the two tallies
tallies = openmc.Tallies([mesh_tally])

# builds the openmc model
my_model = openmc.Model(materials=materials, geometry=geometry, settings=settings, tallies=tallies)

# starts the simulation
output_file = my_model.run()

# loads up the output file from the simulation
statepoint = openmc.StatePoint(output_file)

mesh_tally_result = statepoint.get_tally(name="flux")

umesh_from_sp = statepoint.meshes[1]


centroids = umesh_from_sp.centroids # not needed in the next release of openmc
mesh_vols = umesh_from_sp.volumes # not needed in the next release of openmc

umesh_from_sp.write_data_to_vtk(
    datasets={'mean': mesh_tally_result.mean.flatten()},
    filename='mesh_tally_results.vtk',
)

print('VTK file saved to mesh_tally_results.vtk')

def transport_particles_on_h5m_geometry(
    h5m_filename: str,
    material_tags: list,
    vtk_filename: str = None,
    nuclides: list = None,
    cross_sections_xml: str = None,
):
    """A function for testing the geometry file with particle transport in
    DAGMC OpenMC. Requires openmc and either the cross_sections_xml to be
    specified. Returns the flux on each volume

    Arg:
        h5m_filename: The name of the DAGMC h5m file to test
        material_tags: The
        nuclides:
        cross_sections_xml:

    """

    import openmc
    from openmc.data import NATURAL_ABUNDANCE

    if nuclides is None:
        nuclides = list(NATURAL_ABUNDANCE.keys())

    materials = openmc.Materials()
    for i, material_tag in enumerate(set(material_tags)):
        # simplified material definitions have been used to keen this example minimal
        mat_dag_material_tag = openmc.Material(name=material_tag)
        mat_dag_material_tag.add_nuclide(nuclides[i], 1, "ao")
        mat_dag_material_tag.set_density("g/cm3", 0.01)

        materials.append(mat_dag_material_tag)

    if cross_sections_xml:
        openmc.config["cross_sections"] = cross_sections_xml

    else:
        with open("cross_sections.xml", "w") as file:
            file.write(
                """
            <?xml version='1.0' encoding='UTF-8'?>
            <cross_sections>
            <library materials="H1" path="ENDFB-7.1-NNDC_H1.h5" type="neutron"/>
            <library materials="H2" path="ENDFB-7.1-NNDC_H2.h5" type="neutron"/>
            </cross_sections>
            """
            )

        openmc.config["cross_sections"] = "cross_sections.xml"

    dag_univ = openmc.DAGMCUniverse(filename=h5m_filename)
    bound_dag_univ = dag_univ.bounded_universe()
    geometry = openmc.Geometry(root=bound_dag_univ)

    # initializes a new source object
    my_source = openmc.IndependentSource()

    center_of_geometry = (
        (dag_univ.bounding_box[0][0] + dag_univ.bounding_box[1][0]) / 2,
        (dag_univ.bounding_box[0][1] + dag_univ.bounding_box[1][1]) / 2,
        (dag_univ.bounding_box[0][2] + dag_univ.bounding_box[1][2]) / 2,
    )
    # sets the location of the source which is not on a vertex
    center_of_geometry_nudged = (
        center_of_geometry[0] + 0.1,
        center_of_geometry[1] + 0.1,
        center_of_geometry[2] + 0.1,
    )

    my_source.space = openmc.stats.Point(center_of_geometry_nudged)
    # sets the direction to isotropic
    my_source.angle = openmc.stats.Isotropic()
    # sets the energy distribution to 100% 14MeV neutrons
    my_source.energy = openmc.stats.Discrete([14e6], [1])

    # specifies the simulation computational intensity
    settings = openmc.Settings()
    settings.batches = 10
    settings.particles = 10000
    settings.inactive = 0
    settings.run_mode = "fixed source"
    settings.source = my_source

    if vtk_filename:
        mesh = openmc.UnstructuredMesh(filename=vtk_filename, library='moab')
    else:
        mesh = openmc.RegularMesh().from_domain(bound_dag_univ)
    mesh.id = 1

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
    centroids = umesh_from_sp.centroids
    mesh_vols = umesh_from_sp.volumes

    umesh_from_sp.write_data_to_vtk(
        datasets={'mean': mesh_tally_result.mean.flatten()},
        filename='mesh_tally_results.vtk',
    )

    return mesh_tally_result.mean.flatten()


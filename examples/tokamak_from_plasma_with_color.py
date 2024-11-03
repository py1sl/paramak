from example_util_functions import transport_particles_on_h5m_geometry

import paramak

my_reactor = paramak.tokamak_from_plasma(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 120),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 120),
        (paramak.LayerType.SOLID, 10),
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,
    colors={
        "layer_1": (0.4, 0.9, 0.4),
        "layer_2": (0.6, 0.8, 0.6),
        "plasma": (1., 0.7, 0.8, 0.6),
        "layer_3": (0.1, 0.1, 0.9),
        "layer_4": (0.4, 0.4, 0.8),
        "layer_5": (0.5, 0.5, 0.8),
    }
)
my_reactor.export(f"tokamak_with_colors.step")
print(f"Saved as tokamak_with_colors.step")


# show colors with inbuild vtk viewer
# from cadquery.vis import show
# show(my_reactor)

# cadquery also supports svg export
# currently needs converting to compound first as svg export not supported by assembly objects
# lots of options https://cadquery.readthedocs.io/en/latest/importexport.html#exporting-svg
# my_reactor.toCompound().export("tokamak_from_plasma_with_colors.svg")

# show colors with png file export
# first install plugin with
# pip install git+https://github.com/jmwright/cadquery-png-plugin
import cadquery_png_plugin.plugin
# lots of options
# https://github.com/jmwright/cadquery-png-plugin/blob/d2dd6e8a51b7e165ee80240a701c5b434dfe0733/cadquery_png_plugin/plugin.py#L276-L298
my_reactor.exportPNG(
    options={
        "width":1280,
        "height":1024,
        "zoom":1.4,
    },
    file_path='tokamak_from_plasma_with_colors.png'
)

# from cad_to_dagmc import CadToDagmc
# my_model = CadToDagmc()
# material_tags = ["mat1"] * 6  # as inner and outer layers are one solid there are only 6 solids in model
# my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)
# my_model.export_dagmc_h5m_file(min_mesh_size=3.0, max_mesh_size=20.0)

# h5m_filename = "dagmc.h5m"
# flux = transport_particles_on_h5m_geometry(
#     h5m_filename=h5m_filename,
#     material_tags=material_tags,
#     nuclides=["H1"] * len(material_tags),
#     cross_sections_xml="tests/cross_sections.xml",
# )
# assert flux > 0.0

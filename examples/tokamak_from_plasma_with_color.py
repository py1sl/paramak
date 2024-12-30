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
my_reactor.save(f"tokamak_with_colors.step")
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

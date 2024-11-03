import paramak
import cadquery_png_plugin.plugin

# Original radial build values
original_radial_build = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.GAP, 50),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.SOLID, 60),
    (paramak.LayerType.SOLID, 10),
]
original_elongation = 2

# Function to create a reactor with modified radial build
def create_reactor(radial_build, elongation):
    return paramak.spherical_tokamak_from_plasma(
        radial_build=radial_build,
        elongation=elongation,
        triangularity=0.55,
        rotation_angle=180,
        colors={
            "layer_1": (0.4, 0.9, 0.4),
            "layer_2": (0.6, 0.8, 0.6),
            "plasma": (1., 0.7, 0.8, 0.6),
            "layer_3": (0.1, 0.1, 0.9),
            "layer_4": (0.4, 0.4, 0.8),
            "layer_5": (0.5, 0.5, 0.8),
        },
    )

# Function to export reactor to PNG
def export_reactor_to_png(reactor, file_path):
    reactor.exportPNG(
        options={
            "width": 1280,
            "height": 1024,
            "zoom": 1.4,
        },
        file_path=file_path
    )

# Generate reactors with varying radial build values
frame = 0
for i in range(len(original_radial_build)):
    layer_type, original_value = original_radial_build[i]
    for factor in [1.0, 1.5, 2.0, 1.5, 1.0]:
        modified_radial_build = original_radial_build.copy()
        modified_radial_build[i] = (layer_type, original_value * factor)
        reactor = create_reactor(modified_radial_build, original_elongation)
        export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
        frame += 1

for factor in [1.0, 1.5, 2.0, 1.5, 1.0]:
    modified_elongation = original_elongation * factor
    reactor = create_reactor(original_radial_build, modified_elongation)
    export_reactor_to_png(reactor, f'spherical_tokamak_frame_{frame:03d}.png')
    frame += 1
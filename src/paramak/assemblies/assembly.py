# Creates an assembly class that inherits from cadquery's assembly class
# and adds a few conveniences methods remove() and names()

import warnings
import cadquery as cq


class Assembly(cq.Assembly):
    """Nested assembly of Workplane and Shape objects defining their relative positions."""

    def __init__(self, elongation=None, triangularity=None, major_radius=None, minor_radius=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elongation = elongation
        self.triangularity = triangularity
        self.major_radius = major_radius
        self.minor_radius = minor_radius

    def remove(self, name: str):
        new_assembly = Assembly(
            elongation=self.elongation,
            triangularity=self.triangularity,
            major_radius=self.major_radius,
            minor_radius=self.minor_radius
        )
        part_found = False
        for part in self:
            if part[1].endswith(f'/{name}'):
                part_found = True
                # print('removing' , part)
            else:
                # print('adding' , part)
                new_assembly.add(part[0], name=part[1], color=part[3], loc=part[2])
        if not part_found:
            warnings.warn(f'Part with name {name} not found')
        return new_assembly

    def names(self):
        names = []
        for part in self:
            names.append(part[1].split('/')[-1])
        return names

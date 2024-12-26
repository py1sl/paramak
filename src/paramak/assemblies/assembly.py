# Creates an assembly class that inherits from cadquery's assembly class
# and adds a few conveniences methods remove() and names()

import warnings
import cadquery as cq


class Assembly(cq.Assembly):
    """Nested assembly of Workplane and Shape objects defining their relative positions."""

    elongation=None
    triangularity=None
    major_radius=None
    minor_radius=None

    def remove(self, name: str):
        new_assembly = Assembly()
        part_found = False
        for part in self:
            if part[1].endswith(f'/{name}'):
                part_found = True
            else:
                new_assembly.add(part[0], name=part[1], color=part[3], loc=part[2])
        if not part_found:
            warnings.warn(f'Part with name {name} not found')

        new_assembly.elongation = self.elongation
        new_assembly.triangularity = self.triangularity
        new_assembly.major_radius = self.major_radius
        new_assembly.minor_radius = self.minor_radius
        return new_assembly

    def names(self):
        names = []
        for part in self:
            names.append(part[1].split('/')[-1])
        return names

    def bounding_box(self):
        # Iterate through the remaining parts and update the bounding box coordinates
        for i, part in enumerate(self):
            if i == 0:
                first_part_bbox = part[0].BoundingBox()
                bbox_min = cq.Vector(first_part_bbox.xmin, first_part_bbox.ymin, first_part_bbox.zmin)
                bbox_max = cq.Vector(first_part_bbox.xmax, first_part_bbox.ymax, first_part_bbox.zmax)
            else:
                part_bbox = part[0].BoundingBox()
                bbox_min.x = min(bbox_min.x, part_bbox.xmin)
                bbox_min.y = min(bbox_min.y, part_bbox.ymin)
                bbox_min.z = min(bbox_min.z, part_bbox.zmin)
                bbox_max.x = max(bbox_max.x, part_bbox.xmax)
                bbox_max.y = max(bbox_max.y, part_bbox.ymax)
                bbox_max.z = max(bbox_max.z, part_bbox.zmax)

        return (bbox_min.x, bbox_min.y, bbox_min.z), (bbox_max.x, bbox_max.y, bbox_max.z)

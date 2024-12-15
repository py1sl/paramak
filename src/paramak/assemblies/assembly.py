# Creates an assembly class that inherits from cadquery's assembly class
# and adds a few conveniences methods remove() and names()

import warnings
import cadquery as cq


class Assembly(cq.Assembly):
    """Nested assembly of Workplane and Shape objects defining their relative positions."""

    def remove(self, name:str):
        new_assembly = Assembly()
        part_found=False
        for part in self:
            if part[1].endswith(f'/{name}'):
                part_found = True
                # print('removing' , part)
            else:
                # print('adding' , part)
                new_assembly.add(part[0], name=part[1], color=part[3], loc=part[2])
        if part_found == False:
            warnings.warn(f'Part with name {name} not found')
        return new_assembly


    def names(self):
        names = []
        for part in self:
            names.append(part[1].split('/')[-1])
        return names




# testing
# sphere1 = cq.Workplane().moveTo(2, 2).sphere(1)
# box1 = cq.Workplane().box(1, 1, 1)
# assembly = Assembly()
# assembly.add(box1, name="box1", color=cq.Color(0.5, 0.5, 0.5))
# assembly.add(sphere1, name="sphere")


# assembly2 = assembly.remove('sphere')
# assembly3 = assembly.remove('box1')
# assembly4 = assembly.remove('bosdfsdf')
#!/usr/bin/env python3

import soy
import re
import os.path

class Model(soy.bodies.Mesh) :
    def __init__(self, filename) :
        data = open(filename)
        lines = data.readlines()
        data.close()
        
        vertices = []
        normals = []
        uvs = [0, 0]
        
        material = soy.materials.Material()
        
        materials = {}
        
        splitter = re.compile(r'(\S+)')
        
        for line in lines :
            ind = line.find('#')
            if ind != -1 :
                line = line[0:ind]
                
            line = line.strip()
            
            if len(line) == 0 :
                continue
                
            fields = splitter.findall(line)
            
            if len(fields) == 0 :
                continue
            
            if fields[0] == 'v' :
                if len(fields) != 4 :
                    continue
                
                try :
                    x = float(fields[1])
                    y = float(fields[2])
                    z = float(fields[3])
                    vertices += [x, y, z]
                except ValueError :
                    continue
                
            elif fields[0] == 'vn' :
                if len(fields) != 4 :
                    continue
                
                try :
                    x = float(fields[1])
                    y = float(fields[2])
                    z = float(fields[3])
                    normals += [x, y, z]
                except ValueError :
                    continue
                
            elif fields[0] == 'vt' :
                if len(fields) != 3 :
                    continue
                
                try :
                    x = float(fields[1])
                    y = 1 - float(fields[2])
                    uvs += [x, y]
                except ValueError :
                    continue
                
            elif fields[0] == 'f' :
                if len(fields) < 4 :
                    continue
                
                i1 = i2 = i3 = n1 = n2 = n3 = u1 = u2 = u3 = 0
                
                error = False
                
                for i in range(1, len(fields)) :
                    values = fields[i].split('/')
                    
                    try :
                        i3 = int(values[0])
                    except ValueError :
                        error = True
                        break
                    
                    n3 = 0
                    u3 = 0
                    
                    if len(values) >= 3 :
                        try :
                            n3 = int(values[2])
                        except ValueError :
                            n3 = 0
                    
                    if len(values) >= 2 :
                        try :
                            u3 = int(values[1])
                        except ValueError :
                            u3 = 0
                    
                    if i == 1 :
                        i1 = i3
                        n1 = n3
                        u1 = u3
                        continue
                        
                    if i > 2 :
                        v1 = soy.atoms.Vector(vertices[(i1 - 1)*3:i1*3])
                        v2 = soy.atoms.Vector(vertices[(i2 - 1)*3:i2*3])
                        v3 = soy.atoms.Vector(vertices[(i3 - 1)*3:i3*3])
                        nn1 = nn2 = nn3 = []
                        
                        if n1 == 0 or n2 == 0 or n3 == 0 :
                            nv2 = v2 - v1
                            nv3 = v3 - v1
                            normal = v2.cross(v3)
                            normal.normalize()
                            nn1 = nn2 = nn3 = normal
                            
                        if n1 != 0 :
                            nn1 = soy.atoms.Vector(normals[(n1-1)*3:n1*3])
                        if n2 != 0 :
                            nn2 = soy.atoms.Vector(normals[(n2-1)*3:n2*3])
                        if n3 != 0 :
                            nn3 = soy.atoms.Vector(normals[(n3-1)*3:n3*3])

                        uv1 = soy.atoms.Position(uvs[u1*2:(u1+1)*2])
                        uv2 = soy.atoms.Position(uvs[u2*2:(u2+1)*2])
                        uv3 = soy.atoms.Position(uvs[u3*2:(u3+1)*2])
                        
                        v1 = soy.atoms.Vertex(soy.atoms.Position(v1), nn1, uv1, soy.atoms.Vector((1,0,0)))
                        v2 = soy.atoms.Vertex(soy.atoms.Position(v2), nn2, uv2, soy.atoms.Vector((1,0,0)))
                        v3 = soy.atoms.Vertex(soy.atoms.Position(v3), nn3, uv3, soy.atoms.Vector((1,0,0)))

                        face = soy.atoms.Face(v1, v2, v3, material)
                        self.append(face)
                        
                    i2 = i3
                    n2 = n3
                    u2 = u3
                if error :
                    continue
            elif fields[0] == 'mtllib' :
                if len(fields) != 2 :
                    continue
                base = os.path.split(filename)
                materials.update(self._loadMtl(os.path.join(base[0], fields[1])))
            elif fields[0] == 'usemtl' :
                if len(fields) != 2 :
                    continue
                
                try :
                    material = materials[fields[1]]
                except KeyError :
                    continue

    def _loadMtl(self, filename) :
        data = open(filename)
        lines = data.readlines()
        data.close()
        
        materials = {}
        
        splitter = re.compile(r'(\S+)')
        
        name = None
        bumpmap = soy.textures.Texture()
        colormap = soy.textures.Texture()
        glowmap = soy.textures.Texture()
        ambient = None
        diffuse = None
        specular = None
        shininess = None
        
        for line in lines :
            ind = line.find('#')
            if ind != -1 :
                line = line[0:ind]
                
            line = line.strip()
            
            if len(line) == 0 :
                continue
                
            fields = splitter.findall(line)
            
            if len(fields) == 0 :
                continue
            
            if fields[0] == 'newmtl' :
                if len(fields) != 2 :
                    continue
                if name != None:
                    materials[name] = soy.materials.Textured(name = name, bumpmap = bumpmap, colormap = colormap, glowmap = glowmap)
                    if ambient is not None :
                        materials[name].ambient = ambient
                    if diffuse is not None :
                        materials[name].diffuse = diffuse
                    if specular is not None :
                        materials[name].specular = specular
                    if shininess is not None :
                        materials[name].shininess = shininess
                name = fields[1]
                bumpmap = soy.textures.Texture()
                colormap = soy.textures.Texture()
                glowmap = soy.textures.Texture()
                ambient = None
                diffuse = None
                specular = None
                shininess = None
            elif fields[0] == 'map_Kd' :
                if len(fields) != 2 :
                    continue
                if not os.path.isabs(fields[1]) :
                    base = os.path.split(filename)
                    fields[1] = os.path.join(base[0], fields[1])
                colormap = soy.textures.Texture(fields[1])
            elif fields[0].lower() == 'map_bump' or fields[0].lower() == 'bump' :
                if len(fields) != 2 :
                    continue
                if not os.path.isabs(fields[1]) :
                    base = os.path.split(filename)
                    fields[1] = os.path.join(base[0], fields[1])
                bumpmap = soy.textures.Bumpmap(fields[1])
            elif fields[0] == 'map_Ka' :
                if len(fields) != 2 :
                    continue
                if not os.path.isabs(fields[1]) :
                    base = os.path.split(filename)
                    fields[1] = os.path.join(base[0], fields[1])
                glowmap = soy.textures.Texture(fields[1])
            elif fields[0] == 'Ka' :
                if len(fields) != 4 :
                    continue
                try :
                    ambient = soy.atoms.Color((int(float(fields[1]) * 255), int(float(fields[2]) * 255), int(float(fields[3]) * 255), 255))
                except ValueError :
                    continue
            elif fields[0] == 'Kd' :
                if len(fields) != 4 :
                    continue
                try :
                    diffuse = soy.atoms.Color((int(float(fields[1]) * 255), int(float(fields[2]) * 255), int(float(fields[3]) * 255), 255))
                except ValueError :
                    continue
            elif fields[0] == 'Ks' :
                if len(fields) != 4 :
                    continue
                try :
                    specular = soy.atoms.Color((int(float(fields[1]) * 255), int(float(fields[2]) * 255), int(float(fields[3]) * 255), 255))
                except ValueError :
                    continue
            elif fields[0] == 'Ns' :
                if len(fields) != 2 :
                    continue
                try :
                    shininess = float(fields[1])
                except ValueError :
                    continue
                
        if name != None:
            if colormap is not None :
                if bumpmap is not None:
                    if glowmap is not None:
                        materials[name] = soy.materials.Textured(name = name, colormap = colormap, bumpmap = bumpmap, glowmap = glowmap)
                    else :
                        materials[name] = soy.materials.Textured(name = name, colormap = colormap, bumpmap = bumpmap)
                else :
                    if glowmap is not None:
                        materials[name] = soy.materials.Textured(name = name, colormap = colormap, glowmap = glowmap)
                    else :
                        materials[name] = soy.materials.Textured(name = name, colormap = colormap)
            else :
                if bumpmap is not None:
                    if glowmap is not None:
                        materials[name] = soy.materials.Textured(name = name, bumpmap = bumpmap, glowmap = glowmap)
                    else :
                        materials[name] = soy.materials.Textured(name = name, bumpmap = bumpmap)
                else :
                    if glowmap is not None:
                        materials[name] = soy.materials.Textured(name = name, glowmap = glowmap)
                    else :
                        materials[name] = soy.materials.Colored()
            if ambient is not None :
                materials[name].ambient = ambient
            if diffuse is not None :
                materials[name].diffuse = diffuse
            if specular is not None :
                materials[name].specular = specular
            if shininess is not None :
                materials[name].shininess = shininess
        
        return materials

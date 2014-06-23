#!/usr/bin/env python3

import sdl2
import soy
import sys
import time
import math
import os.path
from model import Model

class Planet :
    def __init__(self, name, texture, size, position, scene) :
        self.name = name
        self.texture = soy.textures.Texture(texture)
        self.sphere = soy.bodies.Sphere()
        self.sphere.material = soy.materials.Textured(colormap=self.texture)
        self.sphere.radius = size
        self.sphere.position = position
        scene[name] = self.sphere

class Player :
    def __init__(self, scene) :
        self.cam = soy.bodies.Camera((0,0,10))
        scene['cam'] = self.cam
        self.rot = self.cam.rotation
        self.shots = []
        self.last_shot = time.time()
        self.controller = sdl2.SDL_GameControllerOpen(0)
        
    def update(self, dt, scene) :
        speed = 50
        strafe = 20
        
        axis1 = sdl2.SDL_GameControllerGetAxis(self.controller, 0) / 32768
        axis2 = sdl2.SDL_GameControllerGetAxis(self.controller, 1) / 32768
        axis3 = sdl2.SDL_GameControllerGetAxis(self.controller, 2) / 32768
        axis4 = sdl2.SDL_GameControllerGetAxis(self.controller, 3) / 32768
        
        self.rot *= soy.atoms.Rotation((0, 1, 0), -axis3 * dt)
        self.rot *= soy.atoms.Rotation((1, 0, 0), -axis4 * dt)

        mov = soy.atoms.Position(self.rot.rotate(soy.atoms.Vector((0, 0, 1)) * dt * speed * axis2))
        mov += soy.atoms.Position(self.rot.rotate(soy.atoms.Vector((1, 0, 0)) * dt * strafe * axis1))

        self.cam.position += mov
        self.cam.rotation = self.rot
        
        current = time.time()

        sdl2.SDL_GameControllerUpdate()
        
        if self.last_shot + 0.1 < current and sdl2.SDL_GameControllerGetButton(self.controller, 8) :
            shot = soy.bodies.Billboard(self.cam.position,
                                        size=soy.atoms.Size((.5,.5)),material=soy.materials.Colored('gold'))
            shot.rotation = self.rot
            shot.addRelForce(0, 0, -1000)
            scene['shot%d' % len(self.shots)] = shot
            self.shots.append(shot)
            self.last_shot = current


sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)
sdl2.SDL_GameControllerEventState(sdl2.SDL_IGNORE)
sdl2.SDL_GameControllerAddMapping(b'030000006d04000018c2000010010000,Logitech Logitech RumblePad 2 USB,platform:Linux,x:b0,a:b1,b:b2,y:b3,back:b8,start:b9,dpleft:h0.8,dpdown:h0.4,dpright:h0.2,dpup:h0.1,leftshoulder:b4,lefttrigger:b6,rightshoulder:b5,righttrigger:b7,leftstick:b10,rightstick:b11,leftx:a0,lefty:a1,rightx:a2,righty:a3,')

if not sdl2.SDL_IsGameController(0) :
    print('No game controller found!')
    sys.exit(1)

client = soy.Client()
room = soy.scenes.Room(1000)
player = Player(room)
client.window.append(soy.widgets.Projector(player.cam))

hudtexture = soy.textures.Texture('hud/hud.svg')
hud = soy.widgets.Canvas(hudtexture)
client.window.append(hud)

room['light'] = soy.bodies.Light((-2, 3, 5))


box = Model('models/main_ship.obj')
box.position = soy.atoms.Position((0, 0, 0))
room['box'] = box



earth = Planet('earth', 'textures/earthmap1k.jpg', 3, soy.atoms.Position((20, 0, 0)), room)
earth.sphere.addTorque(3000,3000,500)

#venus = Planet('venus', 'textures/venusmap.png', 2, soy.atoms.Position((0, 0, -50)), room)
#mercury = Planet('mercury', 'textures/mercurymap.png', 1, soy.atoms.Position((0, 0, -100)), room)
#mars = Planet('mars', 'textures/mars_1k_color.png', 2, soy.atoms.Position((0, 0, 50)), room)
#jupiter = Planet('jupiter', 'textures/jupitermap.png', 10, soy.atoms.Position((0, 0, 100)), room)
#saturn = Planet('saturn', 'textures/saturnmap.png', 9, soy.atoms.Position((0, 0, 150)), room)
#uranus = Planet('uranus', 'textures/uranusmap.png', 7, soy.atoms.Position((0, 0, 200)), room)
#neptune = Planet('neptune', 'textures/neptunemap.png', 7, soy.atoms.Position((0, 0, 250)), room)

last = time.time()

#__import__("code").interact(local=locals())

if __name__ == '__main__' :
    while client.window :

        current = time.time()
        dt = current - last
        last = current
        
        player.update(dt, room)

        #for i in range(32) :
        #    print(sdl2.SDL_GameControllerGetButton(controller, i), end='')
        #print('')

        time.sleep(.01)


sdl2.SDL_GameControllerClose(player.controller)
sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)

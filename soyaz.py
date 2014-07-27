#!/usr/bin/env python3

import sdl2
import soy
import sys
import time
import math
import os.path
from model import Model

class HUD(soy.widgets.Container) :
    def __init__(self) :
        self._crosshair = soy.widgets.Canvas(soy.textures.Texture('hud/crosshair.svg'))
        self._crosshair.keep_aspect = True
        self._crosshair.scaleX = 0.1
        self._crosshair.scaleY = 0.1
        self._target = soy.widgets.Canvas(soy.textures.Texture('hud/hud_target.svg'))
        self._target.keep_aspect = True
        self._target.scaleX = 0.2
        self._target.scaleY = 0.2
        self._target.align = 1
        self._target.y = -0.7
        self._target_picture_empty = soy.textures.Texture()
        self._target_picture_asteroid = soy.textures.Texture("hud/target_type_asteroid.svg")
        self._target_picture_planet = soy.textures.Texture("hud/target_type_planet.svg")
        self._target_picture_ship = soy.textures.Texture("hud/target_type_ship.svg")
        self._target_picture = soy.widgets.Canvas(self._target_picture_empty)
        self._target_picture.keep_aspect = True
        self._target_picture.scaleX = 0.075
        self._target_picture.scaleY = 0.075
        self._target_picture.align = 1
        self._target_picture.y = -0.79
        self._target_picture.x = -0.325
        self._target_text_tex = soy.textures.SVGTexture()
        with open("hud/hud_target_text.svg", "r") as file:
            self._target_text_svg = file.read()
        self._target_text = soy.widgets.Canvas(self._target_text_tex)
        self._target_text.keep_aspect = True
        self._target_text.scaleX = 0.2
        self._target_text.scaleY = 0.2
        self._target_text.align = 1
        self._target_text.y = -0.7
        self._stats = soy.widgets.Canvas(soy.textures.Texture('hud/shieldhull.svg'))
        self._stats.keep_aspect = True
        self._stats.scaleX = 0.2
        self._stats.scaleY = 0.2
        self._stats.align = -1
        self._stats.y = -0.7
        self._target_arrow = soy.widgets.Canvas(soy.textures.Texture('hud/target_arrow.svg'))
        self._target_arrow.keep_aspect = True
        self._target_arrow.scaleX = 0.1
        self._target_arrow.scaleY = 0.1
        self._target_arrow.rotation = 45 / 180 * math.pi
        self._target_circle = soy.widgets.Canvas(soy.textures.Texture('hud/target_circle.svg'))
        self._target_circle.keep_aspect = True
        self._target_circle.scaleX = 0.1
        self._target_circle.scaleY = 0.1
        with open("hud/shieldhull_full.svg", "r") as file:
            self._stats_bar_svg = file.read()
        self._stats_bar_tex = soy.textures.SVGTexture()
        self._stats_bar = soy.widgets.Canvas(self._stats_bar_tex)
        self._stats_bar.keep_aspect = True
        self._stats_bar.scaleX = 0.2
        self._stats_bar.scaleY = 0.2
        self._stats_bar.align = -1
        self._stats_bar.y = -0.7
        
        self.append(self._crosshair)
        self.append(self._target)
        self.append(self._target_picture)
        self.append(self._target_text)
        self.append(self._stats)
        self.append(self._stats_bar)
        self.append(self._target_arrow)
        self.append(self._target_circle)
        
    def target(self, player, objects) :
        target_name = ""
        if player.target == -1 :
            self._target_circle.scaleX = 0
            self._target_circle.scaleY = 0
            self._target_arrow.scaleX = 0
            self._target_arrow.scaleY = 0
            self._target_picture.texture = self._target_picture_empty
        else :
            t = objects[player.target]
            target_name = t.name
            
            if isinstance(t, Asteroid) :
                self._target_picture.texture = self._target_picture_asteroid
            elif isinstance(t, Planet) :
                self._target_picture.texture = self._target_picture_planet
            elif isinstance(t, Ship) :
                self._target_picture.texture = self._target_picture_ship
            else :
                self._target_picture.texture = self._target_picture_empty
            
            direction = soy.atoms.Vector(t.body.position - player.cam.position)
            rot = player.rot.conjugate()
            direction = rot.rotate(direction)
            
            aspect = self.size[0] / self.size[1]
            onscreen = False
            
            if direction[2] < 0 :
                res = player.cam.project(soy.atoms.Vector(direction), aspect)
                if math.fabs(res[0]) < 1 and math.fabs(res[1]) < 1 :
                    self._target_circle.scaleX = 0.1
                    self._target_circle.scaleY = 0.1
                    self._target_arrow.scaleX = 0
                    self._target_arrow.scaleY = 0
                    self._target_circle.x = res[0] * aspect
                    self._target_circle.y = res[1]
                    scale = -11 / direction[2]
                    self._target_circle.scaleX = scale
                    self._target_circle.scaleY = scale
                    onscreen = True

            if onscreen == False :
                angle = math.atan2(direction[1], direction[0])
                
                self._target_arrow.rotation = angle - math.pi / 2
                
                x = math.cos(angle)
                y = math.sin(angle)
                
                yjump = 1 / math.sqrt(aspect * aspect + 1)
                
                if math.fabs(y) < yjump :
                    # left or right screen edge
                    self._target_arrow.x = math.copysign(0.9 * aspect, x)
                    self._target_arrow.y = y * self._target_arrow.x / x
                else :
                    self._target_arrow.y = math.copysign(.9, y)
                    self._target_arrow.x = x * self._target_arrow.y / y
                self._target_circle.scaleX = 0
                self._target_circle.scaleY = 0
                self._target_arrow.scaleX = 0.1
                self._target_arrow.scaleY = 0.1
        self._target_text_tex.source = self._target_text_svg.format(target_name)
        self._stats_bar_tex.source = self._stats_bar_svg.format(975.05469 * player.health / player.max_health, 975.05469 * player.shield / player.max_shield)


class SpaceObject :
    def __init__(self, body, name, position, size, scene, health, shield) :
        self.body = body
        self.name = name
        self.size = size
        self.health = health
        self.shield = shield
        body.position = position
        scene[name] = body
    def collides(self, other) :
        distance = self.body.position - other.body.position
        return distance.x * distance.x + distance.y * distance.y + distance.z * distance.z < (self.size + other.size) * (self.size + other.size)

class Planet(SpaceObject) :
    def __init__(self, name, texture, size, position, scene) :
        super().__init__(soy.bodies.Sphere(), name, position, size, scene, 1000000, 0)
        self.texture = soy.textures.Texture(texture)
        self.body.material = soy.materials.Textured(colormap=self.texture)
        self.body.radius = size

class Ship(SpaceObject) :
    def __init__(self, name, model, size, position, scene) :
        super().__init__(Model(model), name, position, size, scene, 100, 100)

class Asteroid(SpaceObject) :
    def __init__(self, name, model, size, position, scene) :
        super().__init__(Model(model), name, position, size, scene, 30, 0)

class Shot(SpaceObject) :
    def __init__(self, position, number, birth, rotation, scene) :
        body = soy.bodies.Billboard(position, size=soy.atoms.Size((.5,.5)),material=soy.materials.Colored('gold'))
        name = 'shot{0}'.format(number)
        super().__init__(body, name, position, 0, scene, 0, 0)
        self.body.rotation = rotation
        self.body.addRelForce(0, 0, -1000)
        self.number = number
        self.birth = birth
        self.damage = 10

class Player(SpaceObject) :
    def __init__(self, scene) :
        position = soy.atoms.Position((0,0,10))
        self.cam = soy.bodies.Camera(position)
        super().__init__(self.cam, 'cam', position, 3, scene, 100, 100)
        self.rot = self.cam.rotation
        self.shots = []
        self.last_shot = time.time()
        self.controller = sdl2.SDL_GameControllerOpen(0)
        self.target_prev = False
        self.target_next = False
        self.target = -1
        self.fired = 0
        self.max_health = 100
        self.max_shield = 100
        
    def update(self, dt, scene, objects) :
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
            shot = Shot(self.cam.position, self.fired, current, self.rot, scene)
            self.fired += 1
            self.shots.append(shot)
            self.last_shot = current
        
        if len(objects) > 0 :
            if sdl2.SDL_GameControllerGetButton(self.controller, 9) != self.target_prev :
                self.target_prev = not self.target_prev
                if self.target_prev:
                    if self.target == -1 :
                        self.target = 0
                    else :
                        self.target = (self.target + len(objects) - 1) % len(objects)

            if sdl2.SDL_GameControllerGetButton(self.controller, 10) != self.target_next :
                self.target_next = not self.target_next
                if self.target_next:
                    if self.target == -1 :
                        self.target = 0
                    else :
                        self.target = (self.target + 1) % len(objects)
        else :
            self.target = -1
            
        for shot in self.shots :
            hit = False
            
            for obj in objects :
                if obj.collides(shot) :
                    hit = True
                    if obj.shield > 0 :
                        obj.shield -= shot.damage
                        if obj.shield < 0 :
                            obj.shield = 0
                    else :
                        obj.health -= shot.damage
                        if obj.health <= 0 :
                            del scene[obj.name]
                            objects.remove(obj)
                            if self.target == len(objects) :
                                self.target = -1
            
            if current - shot.birth > 10 or hit :
                self.shots.remove(shot)
                del scene['shot%d' % shot.number]

        for obj in objects :
            if obj.collides(self) :
                if self.shield > 0 :
                    self.shield -= 10 * dt
                    if self.shield < 0 :
                        self.shield = 0
                else :
                    self.health -= 10 * dt
                
                if self.health <= 0 :
                    quit()

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

hud = HUD()
client.window.append(hud)

room['light'] = soy.bodies.Light((-2, 3, 5))

objects = []

ship = Ship('Enemy Ship', 'models/main_ship.obj', 3, soy.atoms.Position((0, 0, 0)), room)
earth = Planet('Earth', 'textures/earthmap1k.jpg', 3, soy.atoms.Position((20, 0, 0)), room)
asteroid = Asteroid('Asteroid', 'models/asteroid.obj', 1, soy.atoms.Position((-20, 0, 0)), room)

earth.body.addTorque(3000,3000,500)

objects.append(ship)
objects.append(earth)
objects.append(asteroid)

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
        
        player.update(dt, room, objects)
        
        hud.target(player, objects)

        time.sleep(.01)


sdl2.SDL_GameControllerClose(player.controller)
sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)

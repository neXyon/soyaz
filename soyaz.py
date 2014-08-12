#!/usr/bin/env python3

import sdl2
import soy
import sys
import time
import math
import os.path
import random
import copy
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
        self._score_text_tex = soy.textures.SVGTexture()
        self._score_text = soy.widgets.Canvas(self._score_text_tex)
        self._score_text.keep_aspect = True
        self._score_text.scaleX = 0.2
        self._score_text.scaleY = 0.2
        self._score_text.align = 1
        self._score_text.y = 0.9
        self._time_text_tex = soy.textures.SVGTexture()
        self._time_text = soy.widgets.Canvas(self._time_text_tex)
        self._time_text.keep_aspect = True
        self._time_text.scaleX = 0.2
        self._time_text.scaleY = 0.2
        self._time_text.align = -1
        self._time_text.y = 0.9
        with open("hud/stats_text.svg", "r") as file:
            self._stats_text_svg = file.read()
        self._distance_text_tex = soy.textures.SVGTexture()
        self._distance_text = soy.widgets.Canvas(self._distance_text_tex)
        self._distance_text.keep_aspect = True
        self._distance_text.scaleX = 0.1
        self._distance_text.scaleY = 0.1
        self._distance_text.align = 0
        self._distance_text.x = -0.1
        self._distance_text.y = -0.08
        with open("hud/distance.svg", "r") as file:
            self._distance_text_svg = file.read()
        
        self.append(self._crosshair)
        self.append(self._distance_text)
        self.append(self._target)
        self.append(self._target_picture)
        self.append(self._target_text)
        self.append(self._stats)
        self.append(self._stats_bar)
        self.append(self._target_arrow)
        self.append(self._target_circle)
        self.append(self._score_text)
        self.append(self._time_text)
        
    def update(self, player, objects, time) :
        target_name = ""
        if player.target == None :
            self._target_circle.scaleX = 0
            self._target_circle.scaleY = 0
            self._target_arrow.scaleX = 0
            self._target_arrow.scaleY = 0
            self._target_picture.texture = self._target_picture_empty
            self._distance_text_tex.source = self._stats_text_svg.format('')
        else :
            target_name = player.target.name
            
            if isinstance(player.target, Asteroid) :
                self._target_picture.texture = self._target_picture_asteroid
            elif isinstance(player.target, Planet) :
                self._target_picture.texture = self._target_picture_planet
            elif isinstance(player.target, Ship) :
                self._target_picture.texture = self._target_picture_ship
            else :
                self._target_picture.texture = self._target_picture_empty
            
            direction = soy.atoms.Vector(player.target.body.position - player.cam.position)
            distance = direction.magnitude()
            rot = player.rot.conjugate()
            direction = rot.rotate(direction)
            
            aspect = self.size[0] / self.size[1]
            onscreen = False
            
            self._distance_text_tex.source = self._stats_text_svg.format('{0:.1f}'.format(distance))

            if direction[2] < 0 :
                res = player.cam.project(soy.atoms.Vector(direction), aspect)
                if math.fabs(res[0]) < 1 and math.fabs(res[1]) < 1 :
                    self._target_circle.scaleX = 0.1
                    self._target_circle.scaleY = 0.1
                    self._target_arrow.scaleX = 0
                    self._target_arrow.scaleY = 0
                    self._target_circle.x = res[0] * aspect
                    self._target_circle.y = res[1]
                    scale = -4 * player.target.size / direction[2]
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
        self._score_text_tex.source = self._stats_text_svg.format('{0}'.format(player.score))
        
        time = player.maxtime - time
        
        minutes = math.floor(time / 60)
        seconds = math.floor(math.fmod(time, 60))
        
        self._time_text_tex.source = self._stats_text_svg.format('{0}:{1:02d}'.format(minutes, seconds))
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
    model = None
    
    def __init__(self, name, model, size, position, scene) :
        if Asteroid.model is None :
            Asteroid.model = Model(model)
        
        super().__init__(copy.deepcopy(Asteroid.model), name, position, size, scene, 30, 0)

class Shot(SpaceObject) :
    def __init__(self, position, number, birth, rotation, scene) :
        body = soy.bodies.Billboard(position, size=soy.atoms.Size((.5,.5)),material=soy.materials.Textured(colormap = soy.textures.Texture('textures/shot.png')))
        name = 'shot{0}'.format(number)
        super().__init__(body, name, position, 0, scene, 0, 0)
        self.body.rotation = rotation
        self.body.addRelForce(0, 0, -5000)
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
        self.target_clicked = False
        self.target = None
        self.fired = 0
        self.max_health = 100
        self.max_shield = 100
        self.score = 0
        self.maxtime = 300
        
    def select_target(self, objects) :
        if len(objects) == 0 :
            self.target = None
            return

        best = 1e10
        prev = self.target
        
        for i, t in enumerate(objects) :
            if t == prev :
                continue
            
            direction = soy.atoms.Vector(t.body.position - self.cam.position)
            rot = self.rot.conjugate()
            direction = soy.atoms.Vector(rot.rotate(direction))
            length = direction.magnitude()
            angle = direction.z / length + 1
            weighted = angle + (length / 200)
            if weighted < best :
                self.target = t
                best = weighted
        
    def update(self, runtime, dt, scene, objects, free_asteroids) :
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
        
        if self.last_shot + 0.1 < current and sdl2.SDL_GameControllerGetButton(self.controller, 10) :
            shot = Shot(self.cam.position, self.fired, current, self.rot, scene)
            self.fired += 1
            self.shots.append(shot)
            self.last_shot = current
        
        if sdl2.SDL_GameControllerGetButton(self.controller, 9) != self.target_clicked :
            self.target_clicked = not self.target_clicked
            if self.target_clicked :
                self.select_target(objects)
            
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
                            self.score += 1
                            free_asteroids.append(obj.name)
                            del scene[obj.name]
                            objects.remove(obj)
                            if self.target == obj :
                                self.select_target(objects)
            
            if current - shot.birth > 10 or hit :
                self.shots.remove(shot)
                del scene['shot%d' % shot.number]

        for obj in objects :
            if obj.collides(self) :
                if self.shield > 0 :
                    self.shield -= 10
                    if self.shield < 0 :
                        self.shield = 0
                else :
                    self.health -= 10
                    
                if self.health <= 0 :
                    quit()

                free_asteroids.append(obj.name)
                del scene[obj.name]
                objects.remove(obj)
        
        if runtime > self.maxtime :
            quit()

sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)
sdl2.SDL_GameControllerEventState(sdl2.SDL_IGNORE)
sdl2.SDL_GameControllerAddMapping(b'030000006d04000018c2000010010000,Logitech Logitech RumblePad 2 USB,platform:Linux,x:b0,a:b1,b:b2,y:b3,back:b8,start:b9,dpleft:h0.8,dpdown:h0.4,dpright:h0.2,dpup:h0.1,leftshoulder:b4,lefttrigger:b6,rightshoulder:b5,righttrigger:b7,leftstick:b10,rightstick:b11,leftx:a0,lefty:a1,rightx:a2,righty:a3,')

if not sdl2.SDL_IsGameController(0) :
    print('No game controller found!')
    sys.exit(1)

scale = 500

client = soy.Client()
scene = soy.scenes.Space(2 ** 24, scale)
player = Player(scene)
client.window.append(soy.widgets.Projector(player.cam))

hud = HUD()
client.window.append(hud)

background = soy.textures.Cubemap()
background.front = soy.textures.Texture('textures/front.png')
background.back = soy.textures.Texture('textures/back.png')
background.up = soy.textures.Texture('textures/top.png')
background.down = soy.textures.Texture('textures/bottom.png')
background.left = soy.textures.Texture('textures/left.png')
background.right = soy.textures.Texture('textures/right.png')
scene.skybox = background

objects = []

#ship = Ship('Enemy Ship', 'models/main_ship.obj', 3.5, soy.atoms.Position((0, 0, 0)), scene)
earth = Planet('Earth', 'textures/earthmap1k.jpg', 50000, soy.atoms.Position((0, 0, -60000)), scene)
scene.setDistance('Earth', 100000)

earth.body.addTorque(3000,3000,500)

#objects.append(ship)
#objects.append(earth)

def createAsteroid(name) :
    pos = []
    rot = []
    for j in range(3) :
        pos.append((random.random() * 3 - 1) * scale)
        rot.append((random.random() * 2 - 1) * 10)
    asteroid = Asteroid(name, 'models/asteroid.obj', 1.5, soy.atoms.Position(pos), scene)
    asteroid.body.addTorque(rot[0], rot[1], rot[2])
    objects.append(asteroid)
    scene.setKeep(name, False)
    scene.setDistance(name, scale * 2)

for i in range(100) :
    createAsteroid('Asteroid {0}'.format(i))

free_asteroids = []

#venus = Planet('venus', 'textures/venusmap.png', 2, soy.atoms.Position((0, 0, -50)), scene)
#mercury = Planet('mercury', 'textures/mercurymap.png', 1, soy.atoms.Position((0, 0, -100)), scene)
#mars = Planet('mars', 'textures/mars_1k_color.png', 2, soy.atoms.Position((0, 0, 50)), scene)
#jupiter = Planet('jupiter', 'textures/jupitermap.png', 10, soy.atoms.Position((0, 0, 100)), scene)
#saturn = Planet('saturn', 'textures/saturnmap.png', 9, soy.atoms.Position((0, 0, 150)), scene)
#uranus = Planet('uranus', 'textures/uranusmap.png', 7, soy.atoms.Position((0, 0, 200)), scene)
#neptune = Planet('neptune', 'textures/neptunemap.png', 7, soy.atoms.Position((0, 0, 250)), scene)

start = time.time()
last = start

#__import__("code").interact(local=locals())

if __name__ == '__main__' :
    while client.window :

        current = time.time()
        dt = current - last
        last = current
        
        player.update(current - start, dt, scene, objects, free_asteroids)
        
        hud.update(player, objects, current - start)
        
        rem = scene.pollRemoved()
        for name in rem :
            for i, t in enumerate(objects) :
                if t.name == name :
                    del objects[i]
        free_asteroids.extend(rem)
            
        transitions = scene.pollCells()
        if len(transitions) > 0 :
            for name in free_asteroids :
                createAsteroid(name)
            free_asteroids.clear()
            

        time.sleep(.01)


sdl2.SDL_GameControllerClose(player.controller)
sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)

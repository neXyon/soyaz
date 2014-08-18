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
        self._speed_text_tex = soy.textures.SVGTexture()
        self._speed_text = soy.widgets.Canvas(self._speed_text_tex)
        self._speed_text.keep_aspect = True
        self._speed_text.scaleX = 0.1
        self._speed_text.scaleY = 0.1
        self._speed_text.align = 0
        self._speed_text.x = 0.1
        self._speed_text.y = -0.08
        with open("hud/highscore.svg", "r") as file:
            self._highscore_svg = file.read()
        self._highscore_tex = soy.textures.SVGTexture()
        self._highscore = soy.widgets.Canvas(self._highscore_tex)
        self._highscore.keep_aspect = True
        self._highscore.scaleX = 0.5
        self._highscore.scaleY = 0.5
        self._highscore.align = 1
        self._highscore.x = -0.02
        
        self.append(self._crosshair)
        self.append(self._distance_text)
        self.append(self._speed_text)
        self.append(self._target)
        self.append(self._target_picture)
        self.append(self._target_text)
        self.append(self._stats)
        self.append(self._stats_bar)
        self.append(self._target_arrow)
        self.append(self._target_circle)
        self.append(self._score_text)
        self.append(self._time_text)
        self.append(self._highscore)
        
    def updateHighScore(self, game) :
        if game.menu :
            self._highscore.scaleY = 0.5
            
            hs = []
            i = 1
            
            for score in game.highscores :
                hs.append('{0}. {1}'.format(i, score))
                i += 1
            
            self._highscore_tex.source = self._highscore_svg.format('\n'.join(hs))
        else :
            self._highscore.scaleY = 0
        
    def update(self, game) :
        target_name = ""
        if game.player.target == None :
            self._target_circle.scaleX = 0
            self._target_circle.scaleY = 0
            self._target_arrow.scaleX = 0
            self._target_arrow.scaleY = 0
            self._target_picture.texture = self._target_picture_empty
            self._distance_text_tex.source = self._stats_text_svg.format('')
        else :
            target_name = game.player.target.name
            
            if isinstance(game.player.target, Asteroid) :
                self._target_picture.texture = self._target_picture_asteroid
            elif isinstance(game.player.target, Planet) :
                self._target_picture.texture = self._target_picture_planet
            elif isinstance(game.player.target, Ship) or isinstance(game.player.target, JumpGate) :
                self._target_picture.texture = self._target_picture_ship
            else :
                self._target_picture.texture = self._target_picture_empty
            
            direction = soy.atoms.Vector(game.player.target.body.position - game.player.cam.position)
            distance = direction.magnitude()
            rot = game.player.rot.conjugate()
            direction = rot.rotate(direction)
            
            aspect = self.size[0] / self.size[1]
            onscreen = False
            
            self._distance_text_tex.source = self._stats_text_svg.format('{0:.1f}'.format(distance))

            if direction[2] < 0 :
                res = game.player.cam.project(soy.atoms.Vector(direction), aspect)
                if math.fabs(res[0]) < 1 and math.fabs(res[1]) < 1 :
                    self._target_circle.scaleX = 0.1
                    self._target_circle.scaleY = 0.1
                    self._target_arrow.scaleX = 0
                    self._target_arrow.scaleY = 0
                    self._target_circle.x = res[0] * aspect
                    self._target_circle.y = res[1]
                    scale = -4 * game.player.target.size / direction[2]
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
        self._score_text_tex.source = self._stats_text_svg.format('{0}'.format(game.player.score))
        self._speed_text_tex.source = self._stats_text_svg.format('{0:.1f}'.format(abs(game.player.speed.current)))
        
        minutes = math.floor(game.player.time / 60)
        seconds = math.floor(math.fmod(game.player.time, 60))
        
        self._time_text_tex.source = self._stats_text_svg.format('{0}:{1:02d}'.format(minutes, seconds))
        self._stats_bar_tex.source = self._stats_bar_svg.format(975.05469 * game.player.health / game.player.max_health, 975.05469 * game.player.shield / game.player.max_shield)


class SpaceObject :
    def __init__(self, body, name, position, size, scene, health, shield, keep, target = False) :
        self.body = body
        self.name = name
        self.size = size
        self.health = health
        self.shield = shield
        self.target = target
        self.keep = keep
        #body.position = position
        scene[name] = body
        body.position = position
        
    def collides(self, scene, other) :
        distance = soy.atoms.Vector(scene.getPosition(self.name)) - soy.atoms.Vector(scene.getPosition(other.name))
        return distance.x * distance.x + distance.y * distance.y + distance.z * distance.z < (self.size + other.size) * (self.size + other.size)

class Planet(SpaceObject) :
    def __init__(self, name, texture, size, position, scene) :
        super().__init__(soy.bodies.Sphere(), name, position, size, scene, 1000000, 0, True, True)
        self.texture = soy.textures.Texture(texture)
        self.body.material = soy.materials.Textured(colormap=self.texture)
        self.body.radius = size

    def collidePlayer(self, game) :
        print('Thanks for playing, bye!')
        game.quit = True

class Ship(SpaceObject) :
    def __init__(self, name, model, size, position, scene) :
        super().__init__(Model(model), name, position, size, scene, 100, 100, True, False)

class Asteroid(SpaceObject) :
    model = None
    
    def __init__(self, name, model, position, scene) :
        if Asteroid.model is None :
            Asteroid.model = Model(model)
        
        super().__init__(copy.deepcopy(Asteroid.model), name, position, 1.5, scene, 30, 0, False, True)

    def collidePlayer(self, game) :
        if game.player.shield > 0 :
            game.player.shield -= 10
            if game.player.shield < 0 :
                game.player.shield = 0
        else :
            game.player.health -= 10
        
        game.remove(self)

class TimeUp(SpaceObject) :
    model = None
    
    def __init__(self, name, model, position, scene) :
        if TimeUp.model is None :
            TimeUp.model = Model(model)
        
        super().__init__(copy.deepcopy(TimeUp.model), name, position, 1, scene, 0, 0, False)
        
    def collidePlayer(self, game) :
        game.player.time += 10
        game.player.score += 17
        game.remove(self)

class SpeedUp(SpaceObject) :
    model = None
    
    def __init__(self, name, model, position, scene) :
        if SpeedUp.model is None :
            SpeedUp.model = Model(model)
        
        super().__init__(copy.deepcopy(SpeedUp.model), name, position, 1, scene, 0, 0, False)

    def collidePlayer(self, game) :
        game.player.boost()
        game.player.score += 27
        game.remove(self)

class HealthUp(SpaceObject) :
    model = None
    
    def __init__(self, name, model, position, scene) :
        if HealthUp.model is None :
            HealthUp.model = Model(model)
        
        super().__init__(copy.deepcopy(HealthUp.model), name, position, 1, scene, 0, 0, False)

    def collidePlayer(self, game) :
        if game.player.health == game.player.max_health :
            game.player.shield += 10
            if game.player.shield > game.player.max_shield :
                game.player.shield = game.player.max_shield
        else :
            game.player.health += 10
            if game.player.health > game.player.max_health :
                game.player.health = game.player.max_health
        game.player.score += 123
        game.remove(self)

class Bomb(SpaceObject) :
    model = None
    
    def __init__(self, name, model, position, scene) :
        if Bomb.model is None :
            Bomb.model = Model(model)
        
        super().__init__(copy.deepcopy(Bomb.model), name, position, 1, scene, 0, 0, False)

    def collidePlayer(self, game) :
        if game.player.shield > 0 :
            game.player.shield -= 30
            if game.player.shield <= 0 :
                game.player.shield = 0
        else :
            game.player.health -= 30
        game.player.score -= 11
        game.remove(self)

class Shot(SpaceObject) :
    def __init__(self, position, number, birth, rotation, scene) :
        body = soy.bodies.Billboard(position, size=soy.atoms.Size((.5,.5)),material=soy.materials.Textured(colormap = soy.textures.Texture('textures/shot.png')))
        name = 'shot{0}'.format(number)
        super().__init__(body, name, position, 0, scene, 0, 0, False)
        self.body.rotation = rotation
        self.body.addRelForce(0, 0, -5000)
        self.number = number
        self.birth = birth
        self.damage = 10

class JumpGate(SpaceObject) :
    model = None

    def __init__(self, name, model, position, scene) :
        if JumpGate.model is None :
            JumpGate.model = Model(model)

        super().__init__(copy.deepcopy(JumpGate.model), name, position, 2, scene, 1000000, 0, True, True)

    def collidePlayer(self, game) :
        if game.menu :
            game.start()
        else :
            game.stop(True)

class Speed :
    def __init__(self, max, accel, decel) :
        self.max = max
        self.original = max
        self.duration = 0
        self.accel = accel
        self.decel = decel
        self.current = 0
    
    def update(self, to, dt) :
        to *= self.max
        
        mag = abs(to)
        magc = abs(self.current)
        diff = to - self.current
        magd = abs(diff)
        
        acc = self.accel * dt
        
        if magc > mag or to * self.current < 0 :
            acc = self.decel * dt
        
        if magd < acc :
            acc = diff
        else :
            acc = math.copysign(acc, diff)
        
        self.current += acc
        
        self.duration -= dt
        if self.duration <= 0 :
            self.max = self.original
        
        return self.current * dt
    
    def boost(self, duration, speed) :
        self.max = speed
        self.duration = duration

class Player(SpaceObject) :
    def __init__(self, scene) :
        position = soy.atoms.Position((0,0,0))
        self.cam = soy.bodies.Camera(position)
        super().__init__(self.cam, 'cam', position, 3, scene, 100, 100, True)
        self.rot = self.cam.rotation
        self.last_shot = time.time()
        self.controller = sdl2.SDL_GameControllerOpen(0)
        self.target_clicked = False
        self.target = None
        self.fired = 0
        self.max_health = 100
        self.max_shield = 100
        self.score = 0
        self.start_time = 60#120
        self.time = self.start_time
        self.speed = Speed(50, 10, 20)
        self.strafe = Speed(20, 5, 10)
        self.rotate1 = Speed(1, 4, 4)
        self.rotate2 = Speed(1, 4, 4)
        
    def boost(self) :
        self.speed.boost(5, 80)
        self.strafe.boost(5, 30)
        
    def select_target(self, objects) :
        if len(objects) == 0 :
            self.target = None
            return

        best = 1e10
        prev = self.target
        
        for i, t in enumerate(objects) :
            if t == prev or not t.target :
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
        
    def update(self, dt, game) :
        axis1 = sdl2.SDL_GameControllerGetAxis(self.controller, 0) / 32768
        axis2 = sdl2.SDL_GameControllerGetAxis(self.controller, 1) / 32768
        axis3 = sdl2.SDL_GameControllerGetAxis(self.controller, 2) / 32768
        axis4 = sdl2.SDL_GameControllerGetAxis(self.controller, 3) / 32768
        
        self.rot *= soy.atoms.Rotation((0, 1, 0), -self.rotate1.update(axis3, dt))
        self.rot *= soy.atoms.Rotation((1, 0, 0), -self.rotate2.update(axis4, dt))

        mov = soy.atoms.Position(self.rot.rotate(soy.atoms.Vector((0, 0, 1)) * self.speed.update(axis2, dt)))
        mov += soy.atoms.Position(self.rot.rotate(soy.atoms.Vector((1, 0, 0)) * self.strafe.update(axis1, dt)))

        self.cam.position += mov
        self.cam.rotation = self.rot
        
        current = time.time()

        sdl2.SDL_GameControllerUpdate()
        
        if self.last_shot + 0.1 < current and sdl2.SDL_GameControllerGetButton(self.controller, 10) :
            shot = Shot(self.cam.position, self.fired, current, self.rot, game.scene)
            self.fired += 1
            game.shots.append(shot)
            self.last_shot = current
        
        if sdl2.SDL_GameControllerGetButton(self.controller, 9) != self.target_clicked :
            self.target_clicked = not self.target_clicked
            if self.target_clicked :
                self.select_target(game.objects)
            
        if not game.menu :
            self.time -= dt
        
class Game :
    def __init__(self) :
        self.client = soy.Client()
        self.scale = 500
        
        self.objects = []
        self.free_asteroids = []
        self.shots = []
        self.pup = 0
        self.quit = False
        self.menu = True
        
        self.readHighScore()

        self.scene = soy.scenes.Space(2 ** 24, self.scale)
        self.player = Player(self.scene)

        self.client.window.append(soy.widgets.Projector(self.player.cam))

        self.hud = HUD()
        self.hud.updateHighScore(self)
        self.client.window.append(self.hud)

        background = soy.textures.Cubemap()
        background.front = soy.textures.Texture('textures/front.png')
        background.back = soy.textures.Texture('textures/back.png')
        background.up = soy.textures.Texture('textures/top.png')
        background.down = soy.textures.Texture('textures/bottom.png')
        background.left = soy.textures.Texture('textures/left.png')
        background.right = soy.textures.Texture('textures/right.png')
        self.scene.skybox = background

        #self.ship = Ship('Enemy Ship', 'models/main_ship.obj', 3.5, soy.atoms.Position((0, 0, 0)), self.scene)
        self.earth = Planet('Earth', 'textures/earthmap1k.jpg', 50000, soy.atoms.Position((0, 0, -50100)), self.scene)
        self.scene.setDistance('Earth', 100000)
        self.earth.body.addTorque(3000,3000,500)

        self.jumpgate1 = JumpGate('Earth Jump Gate', 'models/jumpgate.obj', soy.atoms.Position((0, 0, 100)), self.scene)
        self.jumpgate1.body.addTorque(30,30,30)

        self.jumpgate2 = JumpGate('Asteroid Field Jump Gate', 'models/jumpgate.obj', soy.atoms.Position((0, 0, 50100)), self.scene)
        self.jumpgate2.body.addTorque(30,30,30)

        #self.objects.append(self.ship)
        self.objects.append(self.jumpgate1)
        self.objects.append(self.jumpgate2)
        self.objects.append(self.earth)

        #venus = Planet('venus', 'textures/venusmap.png', 2, soy.atoms.Position((0, 0, -50)), scene)
        #mercury = Planet('mercury', 'textures/mercurymap.png', 1, soy.atoms.Position((0, 0, -100)), scene)
        #mars = Planet('mars', 'textures/mars_1k_color.png', 2, soy.atoms.Position((0, 0, 50)), scene)
        #jupiter = Planet('jupiter', 'textures/jupitermap.png', 10, soy.atoms.Position((0, 0, 100)), scene)
        #saturn = Planet('saturn', 'textures/saturnmap.png', 9, soy.atoms.Position((0, 0, 150)), scene)
        #uranus = Planet('uranus', 'textures/uranusmap.png', 7, soy.atoms.Position((0, 0, 200)), scene)
        #neptune = Planet('neptune', 'textures/neptunemap.png', 7, soy.atoms.Position((0, 0, 250)), scene)

    def readHighScore(self) :
        filename = os.path.expanduser('~/soyaz.score')
        
        try :
            data = open(filename)
            lines = data.readlines()
            data.close()
            
            hs = []
            
            for line in lines :
                hs.append(int(line))
            
            hs.sort(reverse = True)
            
            self.highscores = hs
        except :
            self.highscores = []

    def saveHighScores(self) :
        filename = os.path.expanduser('~/soyaz.score')

        self.highscores.sort(reverse = True)
        self.highscores = self.highscores[0:10]

        lines = []
        for hs in self.highscores :
            lines.append(str(hs) + '\n')

        try :
            data = open(filename, 'w')
            data.writelines(lines)
            data.close()
        except :
            pass

    def start(self) :
        if self.menu :
            self.menu = False
            #self.client.window.append(self.hud)
            self.hud.updateHighScore(self)
            goto = soy.atoms.Vector(self.scene.getPosition(self.jumpgate2.name))
            #goto = goto - soy.atoms.Vector(self.scene.getPosition(self.player.name))
            self.scene.setPosition(self.player.name, goto[0], goto[1], goto[2] - 100)
            time.sleep(0.1)
            if len(self.free_asteroids) == 0 :
                for i in range(100) :
                    self.createAsteroid('Asteroid {0}'.format(i))
            else :
                self.resetAsteroids()
            #self.player.select_target(self.objects)
            self.player.target = self.jumpgate2
        
    def stop(self, scores = False) :
        if not self.menu :
            self.menu = True
            
            if scores :
                self.player.score += 111
                
            # save high score!
            
            self.highscores.append(self.player.score)
            self.saveHighScores()
            print('Game over, score: {0}'.format(self.player.score))
            self.hud.updateHighScore(self)
            
            #self.client.window.remove(self.hud)
            keeping = 0
            while len(self.objects) > keeping :
                if self.objects[keeping].keep :
                    keeping += 1
                else :
                    self.remove(self.objects[keeping])
            self.player.health = self.player.max_health
            self.player.shield = self.player.max_shield
            self.player.time = self.player.start_time
            self.player.score = 0
            goto = soy.atoms.Vector(self.scene.getPosition(self.jumpgate1.name))
            #goto = goto - soy.atoms.Vector(self.scene.getPosition(self.player.name))
            self.scene.setPosition(self.player.name, goto[0], goto[1], goto[2] - 100)

    def createAsteroid(self, name) :
        pos = []
        rot = []
        for j in range(3) :
            pos.append((random.random() * 3 - 1) * self.scale)
            rot.append((random.random() * 2 - 1) * 10)
        asteroid = Asteroid(name, 'models/asteroid.obj', soy.atoms.Position(pos), self.scene)
        asteroid.body.addTorque(rot[0], rot[1], rot[2])
        self.objects.append(asteroid)
        self.scene.setKeep(name, False)
        self.scene.setDistance(name, self.scale * 2)
        
    def resetAsteroid(self, asteroid) :
        pos = []
        rot = []
        for j in range(3) :
            pos.append((random.random() * 3 - 1) * self.scale)
            rot.append((random.random() * 2 - 1) * 10)
        asteroid.body.addTorque(rot[0], rot[1], rot[2])
        asteroid.body.position = soy.atoms.Position(pos)
        self.objects.append(asteroid)
        self.scene[asteroid.name] = asteroid.body
        self.scene.setKeep(asteroid.name, False)
        self.scene.setDistance(asteroid.name, self.scale * 2)
    
    def resetAsteroids(self) :
        for obj in self.free_asteroids :
            self.resetAsteroid(obj)
        self.free_asteroids.clear()
        
    def createPowerUp(self, position) :
        name = 'Power Up {0}'.format(self.pup)
        pup = None
        
        prob = random.random()
        
        if prob < 0.25 :
            pup = TimeUp(name, 'models/time.obj', position, self.scene)
        elif prob < 0.5 :
            pup = SpeedUp(name, 'models/speed.obj', position, self.scene)
        elif prob < 0.75 :
            pup = HealthUp(name, 'models/health.obj', position, self.scene)
        elif prob < 1.0 :
            pup = Bomb(name, 'models/bomb.obj', position, self.scene)
        else :
            return
        
        self.pup += 1
        self.objects.append(pup)
        self.scene.setKeep(name, False)
        self.scene.setDistance(name, self.scale * 2)
        
    def remove(self, obj) :
        if obj.name.startswith('Asteroid') :
            self.free_asteroids.append(obj)

        del self.scene[obj.name]
        self.objects.remove(obj)

        if self.player.target == obj :
            self.player.select_target(self.objects)
        
    def run(self) :
        start = time.time()
        last = start

        #__import__("code").interact(local=locals())

        while self.client.window and not self.quit :

            current = time.time()
            dt = current - last
            last = current
            
            # skip lags
            if dt > 0.5 :
                dt = 0
            
            self.player.update(dt, game)
            
            for shot in self.shots :
                hit = False
                
                for obj in self.objects :
                    if obj.target and obj.collides(self.scene, shot) :
                        hit = True
                        if obj.shield > 0 :
                            obj.shield -= shot.damage
                            if obj.shield < 0 :
                                obj.shield = 0
                        else :
                            obj.health -= shot.damage
                            if obj.health <= 0 :
                                self.createPowerUp(obj.body.position)
                                self.player.score += 10
                                self.remove(obj)
                
                if current - shot.birth > 10 or hit :
                    self.shots.remove(shot)
                    del self.scene['shot%d' % shot.number]

            for obj in self.objects :
                if obj.collides(self.scene, self.player) :
                    obj.collidePlayer(self)
        
            if self.player.health <= 0 or self.player.time <= 0 :
                self.stop()
                
            self.hud.update(self)
            
            rem = self.scene.pollRemoved()
            for name in rem :
                for i, t in enumerate(self.objects) :
                    if t.name == name :
                        del self.objects[i]
                        if name.startswith('Asteroid') :
                            self.free_asteroids.append(t)
                
            transitions = self.scene.pollCells()
            if len(transitions) > 0 and not self.menu :
                self.resetAsteroids()

            time.sleep(.01)

if __name__ == '__main__' :
    sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)
    sdl2.SDL_GameControllerEventState(sdl2.SDL_IGNORE)
    sdl2.SDL_GameControllerAddMapping(b'030000006d04000018c2000010010000,Logitech Logitech RumblePad 2 USB,platform:Linux,x:b0,a:b1,b:b2,y:b3,back:b8,start:b9,dpleft:h0.8,dpdown:h0.4,dpright:h0.2,dpup:h0.1,leftshoulder:b4,lefttrigger:b6,rightshoulder:b5,righttrigger:b7,leftstick:b10,rightstick:b11,leftx:a0,lefty:a1,rightx:a2,righty:a3,')

    if not sdl2.SDL_IsGameController(0) :
        print('No game controller found!')
        sys.exit(1)

    game = Game()

    game.run()

    sdl2.SDL_GameControllerClose(game.player.controller)
    sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_GAMECONTROLLER)

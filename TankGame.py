#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#==============================================================================
# Title: Tank Game
# Author: Ryan J. Slater
# Date: 4/18/2018
#==============================================================================

import pygame
import math
import time
import sys
import os.path
import platform
import updateTerrain
import random as rand
import numpy as np
import pygame.locals as pl

operatingSystem = platform.system()
pygame.font.init()

#import generateRandomFunction as grf



#==============================================================================
# Generic GUI Stuff
#==============================================================================

class colors():
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    RED = (200,0,0)
    GREEN = (0,200,0)
    BLUE = (0, 0, 200)
    ORANGE = (255, 100, 0)
    PURPLE = (102, 0, 51)
    PINK = (255, 0, 102)
    BROWN = (139, 69, 19)
    BRIGHTRED = (255,0,0)
    BRIGHTGREEN = (0,255,0)
    BRIGHTBLUE = (0, 0, 255)
    SKY = (135, 206, 250)
    GRASS = (70, 127, 0)
    CONTROLBOARDBACKGROUND = (100, 100, 100)

    def getRGBColor(color):
        if color == 'red':
            return (200,0,0)
        elif color == 'blue':
            return (0, 0, 200)
        elif color == 'yellow':
            return (200, 200, 0)
        elif color == 'green':
            return (0, 100, 0)
        elif color == 'orange':
            return (255, 100, 0)
        elif color == 'purple':
            return (102, 0, 51)
        elif color == 'pink':
            return (255, 0, 102)
        elif color == 'brown':
            return (139, 69, 19)

    def getColorFromPlayerNum(num):
        if num == 0:
            return 'red'
        elif num == 1:
            return 'blue'
        elif num == 2:
            return 'green'
        elif num == 3:
            return 'yellow'
        elif num == 4:
            return 'purple'
        elif num == 5:
            return 'orange'
        elif num == 6:
            return 'pink'
        elif num == 7:
            return 'brown'

    def getRandomGrassColor():
        return (70+rand.randint(-30, 30), 100+rand.randint(-30, 30), 0)

    def getPowerBarColor(color, value):
        factor = value/200
        if color == 'red':
            return (255, 200-value, 200-value)
        elif color == 'blue':
            return (200-value, 200-value, 255)
        elif color == 'yellow':
            return (200, 200, 200-value)
        elif color == 'green':
            return (200-value, 255-int(factor*155), 200-value)
        elif color == 'purple':
            return (255-int(factor*153), 200-value, 255-int(factor*204))
        elif color == 'orange':
            return (255, 255-int(factor*155), 200-value)
        elif color == 'pink':
            return (255, 200-value, 255-int(factor*153))
        elif color == 'brown':
            return (255-int(factor*116), 255-int(factor*186), 255-int(factor*236))

    def getExplosionColor(value, maxValue):
        return (255, int(255-255*(value/maxValue)), 0)


def text_objects(text, font, color=colors.BLACK):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def button(msg, x, y, w, h, ic, ac, action=None, textSize = 30):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        text = pygame.font.SysFont('couriernew', textSize)
        textSurf, textRect = text_objects(msg, text)
        textRect.center = ((x+(w/2)), (y+(h/2)))
        gameDisplay.blit(textSurf, textRect)
        if click[0] == 1 and action != None:
            if action == play:
                play(displayWidth, displayHeight)
            else:
                action()
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))
        text = pygame.font.SysFont('couriernew', textSize)
        textSurf, textRect = text_objects(msg, text)
        textRect.center = ((x+(w/2)), (y+(h/2)))
        gameDisplay.blit(textSurf, textRect)

class TextInput:
    """
    This class lets the user input a piece of text, e.g. a name or a message.
    This class let's the user input a short, one-lines piece of text at a blinking cursor
    that can be moved using the arrow-keys. Delete, home and end work as well.
    """
    def __init__(self, font_family = "",
                        font_size = 35,
                        antialias=True,
                        text_color=(0, 0, 0),
                        cursor_color=(0, 0, 1),
                        repeat_keys_initial_ms=400,
                        repeat_keys_interval_ms=35):
        """
        Args:
            font_family: Name or path of the font that should be used. Default is pygame-font
            font_size: Size of the font in pixels
            antialias: (bool) Determines if antialias is used on fonts or not
            text_color: Color of the text
            repeat_keys_initial_ms: ms until the keydowns get repeated when a key is not released
            repeat_keys_interval_ms: ms between to keydown-repeats if key is not released
        """

        # Text related vars:
        self.antialias = antialias
        self.text_color = text_color
        self.font_size = font_size
        self.input_string = "" # Inputted text
        if not os.path.isfile(font_family): font_family = pygame.font.match_font(font_family)
        self.font_object = pygame.font.SysFont('couriernew', font_size)

        # Text-surface will be created during the first update call:
        self.surface = pygame.Surface((1, 1))
        self.surface.set_alpha(0)

        # Vars to make keydowns repeat after user pressed a key for some time:
        self.keyrepeat_counters = {} # {event.key: (counter_int, event.unicode)} (look for "***")
        self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
        self.keyrepeat_interval_ms = repeat_keys_interval_ms

        # Things cursor:
        self.cursor_surface = pygame.Surface((int(self.font_size/20+1), self.font_size))
        self.cursor_surface.fill(cursor_color)
        self.cursor_position = 0 # Inside text
        self.cursor_visible = True # Switches every self.cursor_switch_ms ms
        self.cursor_switch_ms = 500 # /|\
        self.cursor_ms_counter = 0

        self.clock = pygame.time.Clock()

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.cursor_visible = True # So the user sees where he writes

                # If none exist, create counter for that key:
                if not event.key in self.keyrepeat_counters:
                    self.keyrepeat_counters[event.key] = [0, event.unicode]

                if event.key == pl.K_BACKSPACE:
                    self.input_string = self.input_string[:max(self.cursor_position - 1, 0)] + \
                                        self.input_string[self.cursor_position:]

                    # Subtract one from cursor_pos, but do not go below zero:
                    self.cursor_position = max(self.cursor_position - 1, 0)
                elif event.key == pl.K_DELETE:
                    self.input_string = self.input_string[:self.cursor_position] + \
                                        self.input_string[self.cursor_position + 1:]

                elif event.key == pl.K_RETURN:
                    return True

                elif event.key == pl.K_RIGHT:
                    # Add one to cursor_pos, but do not exceed len(input_string)
                    self.cursor_position = min(self.cursor_position + 1, len(self.input_string))

                elif event.key == pl.K_LEFT:
                    # Subtract one from cursor_pos, but do not go below zero:
                    self.cursor_position = max(self.cursor_position - 1, 0)

                elif event.key == pl.K_END:
                    self.cursor_position = len(self.input_string)

                elif event.key == pl.K_HOME:
                    self.cursor_position = 0

                else:
                    # If no special key is pressed, add unicode of key to input_string
                    self.input_string = self.input_string[:self.cursor_position] + \
                                        event.unicode + \
                                        self.input_string[self.cursor_position:]
                    self.cursor_position += len(event.unicode) # Some are empty, e.g. K_UP

            elif event.type == pl.KEYUP:
                # *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
                if event.key in self.keyrepeat_counters:
                    del self.keyrepeat_counters[event.key]

        # Update key counters:
        for key in self.keyrepeat_counters :
            self.keyrepeat_counters[key][0] += self.clock.get_time() # Update clock
            # Generate new key events if enough time has passed:
            if self.keyrepeat_counters[key][0] >= self.keyrepeat_intial_interval_ms:
                self.keyrepeat_counters[key][0] = self.keyrepeat_intial_interval_ms - \
                                                    self.keyrepeat_interval_ms

                event_key, event_unicode = key, self.keyrepeat_counters[key][1]
                pygame.event.post(pygame.event.Event(pl.KEYDOWN, key=event_key, unicode=event_unicode))

        # Rerender text surface:
        self.surface = self.font_object.render(self.input_string, self.antialias, self.text_color)

        # Update self.cursor_visible
        self.cursor_ms_counter += self.clock.get_time()
        if self.cursor_ms_counter >= self.cursor_switch_ms:
            self.cursor_ms_counter %= self.cursor_switch_ms
            self.cursor_visible = not self.cursor_visible

        if self.cursor_visible:
            cursor_y_pos = self.font_object.size(self.input_string[:self.cursor_position])[0]
            # Without this, the cursor is invisible when self.cursor_position > 0:
            if self.cursor_position > 0:
                cursor_y_pos -= self.cursor_surface.get_width()
            self.surface.blit(self.cursor_surface, (cursor_y_pos, 0))

        self.clock.tick()
        return False

    def get_surface(self):
        return self.surface

    def get_text(self):
        return self.input_string

    def get_cursor_position(self):
        return self.cursor_position

    def set_text_color(self, color):
        self.text_color = color

    def set_cursor_color(self, color):
        self.cursor_surface.fill(color)

    def clear_text(self):
        self.input_string=""

def unpause():
    global pause
    global players
    print('Unpausing game')
    pause = False
    loadingScreen()
    drawTerrain()
    drawTanks(players)
    print('Done')

def paused():
    text = pygame.font.SysFont('couriernew', titleTextSize)
    TextSurf, TextRect = text_objects('Paused', text)
    TextRect.center = ((displayWidth/2), (displayHeight/4))
    print('Game paused')
    while True:
        if not pause:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitGame()
        gameDisplay.fill(colors.WHITE)
        bg = pygame.image.load('pausedMenuBackground.jpg')
        gameDisplay.blit(bg, (0, 0))
        gameDisplay.blit(TextSurf, TextRect)
        button('MAIN MENU', int((displayWidth/2)+(5/640)*displayWidth), int((3/4)*displayHeight), int((13/64)*displayWidth), int((5/48)*displayHeight), colors.RED, colors.BRIGHTRED, play)
        button('CONTINUE', int(displayWidth/2-(125/640)*displayWidth), int((3/4)*displayHeight), int((12/64)*displayWidth), int((5/48)*displayHeight), colors.GREEN, colors.BRIGHTGREEN, unpause)
        pygame.display.update()
        clock.tick(60)

def quitGame():
    pygame.quit()


















#==============================================================================
# Player and Weapon Classes
#==============================================================================

class player:
    def __init__(self, name, color, idnum):
        self.idnum = idnum
        self.name = name
        self.color = color
        self.RGBColor = colors.getRGBColor(self.color)
        self.tankLoc = (0, 0)
        self.movementPerTurn = 200
        self.movementLeft = self.movementPerTurn
        self.statuses = []
        if operatingSystem == 'Windows':
            self.tankImage = pygame.image.load('tanks\\' + self.color + 'tank.png')
        else:
            self.tankImage = pygame.image.load('tanks/' + self.color + 'tank.png')
        self.weapons = [weapon('standard', 0), weapon('highexplosive', 2)]

        # Weapon ideas:

        # EASY:
        # --Standard: r=10, moderate damage, moderate dropoff--
        # --HE: r = 20, high damage, fast dropoff--
        # Tunneler: standard shot but less damage, same physics, doesn't stop if hit terrain
        # Flamethrower: low damage, but add burn effect, low range, random duration (1-5 turns?)
        # shot with no wind effect. tmpWind = wind, wind = 0, calc as normal, reset wind = tmpWind
        # EMP: if hit, add EMP status effect, emp = 0, if effect: emp = rand.ranint(-2, 2), add emp*t to xDisplacementCalculation, duration rand(1, 3) turns
        # Freeze: if hit, add freeze status effect, movement for next turn of hit tank = 0, duration rand(1, 3) turns
        # Terrain-builder: standard shot, low damage, builds terrain, tank rises
        # Heal shot: standard, but deals negative damage

        # MEDIUM:
        # Lightning shot: on hit, check if dist to all other tanks < 200, if so do less damage to that tank, repeat. recursive?
        # Pokeball: hit tank is captured. turn-=1 so player can shoot pokeball again. Wherever it lands is where captured tank ends up
        # Sniper: gravity = 0 temporarily, doesn't shoot through much terrain, 25 dmg

        # HARD:
        # Spreadshot: 10-20 shells, r = 1 or 2?, low damage, no dropoff
        # Airstrike: 25 damage, select area, massive initial cooldown (not ready for a while)
        # Tri-shot: 1/3 of standard, shoots in sequence, slight RNG on shells 2 and 3
        # Machine gun: 30ish? shells, RNG on each shot, low damage, no dropoff, r= 1 or 2



        self.currentWeapon = self.weapons[0]
        self.barrelAngle = 0 # Straight up
        self.power = 50
        self.tankHealth = 100

    def updateTankLoc(self, loc):
        self.tankLoc = loc

    def shoot(self):
        print('\n' + self.name + ' shooting')
        self.currentWeapon.shoot(self.power, math.radians(-1*(self.barrelAngle-90)), self.tankLoc)
        self.currentWeapon.resetCooldown()

    def moveBarrel(self, amount):
        self.barrelAngle += amount
        if self.barrelAngle < -110:
            self.barrelAngle = -110
        elif self.barrelAngle > 110:
            self.barrelAngle = 110

    def updateSelectedWeaponArrowKeys(self, direction):
        currentSelection = 0
        for i in range(len(self.weapons)):
            if self.weapons[i] == self.currentWeapon:
                currentSelection = i
                break
        currentSelection += direction
        if currentSelection < 0:
            self.currentWeapon = self.weapons[len(self.weapons)-1]
        elif currentSelection >= len(self.weapons):
            self.currentWeapon = self.weapons[0]
        else:
            self.currentWeapon = self.weapons[currentSelection]

    def updateCurrentSelectedWeapon(self, number):
        if number > 0 and number <= len(self.weapons) and self.weapons[number-1].isReady():
            self.currentWeapon = self.weapons[number-1]

    def changePower(self, amount):
        self.power += amount
        if self.power > 100:
            self.power = 100
        elif self.power < 10:
            self.power = 10

    def updateHealth(self, amount):
        print('Changing tank health ' + str(self.tankHealth) + ' + ' + str(amount) + ' = ' + str(self.tankHealth+amount))
        self.tankHealth += amount
        if self.tankHealth > 100:
            self.tankHealth = 100
        elif self.tankHealth <= 0:
            self.tankHealth = 0
            self.die()

    def die(self):
        global players
        global turn

        for col in range(1080):
            for row in range(mapHeight):
                if terrain[row][col] == self.idnum:
                    terrain[row][col] = 0
        for i in range(len(players)):
            if players[i].idnum == self.idnum:
                players.pop(i)
                break
        explosion = pygame.image.load('explosion.png')
        gameDisplay.blit(explosion, (self.tankLoc[0]-25, self.tankLoc[1]-23))
        pygame.display.update()
        time.sleep(1)
        print('Length players: ' + str(len(players)))
        for i in players:
            print('Player id ' + str(i.idnum))
        print('Turn: ' + str(turn))
        if turn >= len(players):
            turn = -1
        print('Updated turn: ' + str(turn))
        drawTerrain()
        drawTanks(players)

class weapon:
    def __init__(self, name, cooldownTime):
        self.name = name
        self.cooldownTime = cooldownTime
        self.timeUntilAvailable = cooldownTime
        self.shell = Shell(self.name)
        weaponsDir = 'weapons/'
        if operatingSystem == 'Windows':
            weaponsDir = 'weapons\\'
        self.image = pygame.image.load(weaponsDir + self.name + 'weapon.png')

    def shoot(self, power, angle, initialLocation):
        hit = self.shell.shoot(power, angle, (initialLocation[0]+25, initialLocation[1]+7))
        return hit

    def cool(self):
        self.timeUntilAvailable -= 1
        if self.timeUntilAvailable < 0:
            self.timeUntilAvailable = 0

    def resetCooldown(self):
        self.timeUntilAvailable = self.cooldownTime + 1

    def isReady(self):
        if self.timeUntilAvailable == 0:
            return True
        return False

class Shell:
    def __init__(self, ammoType):
        self.ammoType = ammoType
        self.xLocation = 0
        self.yLocation = 0
        self.tankDamageRadius, self.terrainExplosionRadius = self.defineExplosionParameters()

    def defineExplosionParameters(self):
        if self.ammoType == 'standard':
            return (10, 10)
        elif self.ammoType == 'highexplosive':
            return (30, 30)
        return (0, 0)

    def getDamage(self, distance):
        if self.ammoType == 'standard':
            return 10
        elif self.ammoType == 'highexplosive':
            return (-1/45)*distance**2 + 20

    def shoot(self, power, angle, initialLoc):
        hit = False
        self.xLocation = initialLoc[0]
        self.yLocation = initialLoc[1]
        p = power
        a = angle
        t = 0
        xCalcDelta = 0
        yCalcDelta = 0
        x = []
        xNoWind = []
        y = []
        if self.ammoType in ['standard', 'highexplosive']: # or any other weapons with these physics
            g = gravity
            while True:
                xCalcDelta = int(p*t*math.cos(a)+wind*t)
                yCalcDelta = int(p*t*math.sin(a)-0.5*g*t*t)
                x.append(xCalcDelta)
                y.append(yCalcDelta)
                xNoWind.append(xCalcDelta-wind*t)
                t += 1/50
                if self.xLocation+xCalcDelta < 0 or self.xLocation+xCalcDelta > 1080 or self.yLocation-yCalcDelta > 670:
                    break

            for i in y:
                i = 670-i

        # Remove points that overlap shooting tank
        while True:
            if terrain[self.yLocation-y[0]-1][self.xLocation+x[0]-1] != 0:
                x.pop(0)
                y.pop(0)
                xNoWind.pop(0)
            else:
                break

        displayInterval = 2
        i = displayInterval
        currentLoc = (self.xLocation+x[0]-1, self.yLocation-y[0]-1)
        while self.xLocation+x[i] > 0 and self.xLocation+x[i] < 1080 and self.yLocation-y[i] < 670:
            if i > len(x)-1 or i > len(y)-1:
                break
            if terrain[self.yLocation-y[i]-1][self.xLocation+x[i]-1] != 0 and self.yLocation-y[i] > 0:
                hit = True
                break
            pygame.draw.rect(gameDisplay, colors.BLACK, (self.xLocation+x[i]-1, self.yLocation-y[i]-1, 3, 3))
            pygame.draw.rect(gameDisplay, colors.SKY, (self.xLocation+x[i-displayInterval]-1, self.yLocation-y[i-displayInterval]-1, 3, 3))
            pygame.draw.rect(gameDisplay, colors.BLACK, (self.xLocation+x[i]-1, self.yLocation-y[i]-1, 3, 3))
            currentLoc = (self.xLocation+x[i]-1, self.yLocation-y[i]-1)
            pygame.display.update()
            clock.tick(30)
            i += displayInterval
            if i > len(x)-1 or i > len(y)-1:
                break

        if hit:
            print('Hit at (' + str(currentLoc[0]) + ', ' + str(currentLoc[1]) + ')')
            pygame.draw.rect(gameDisplay, colors.SKY, (currentLoc[0], currentLoc[1], 3, 3))
            self.explode(currentLoc)
            print('Gravity update')
            gravityUpdate()
            print('Redrawing terrain')
            drawTanks(players)
            drawTerrain(currentLoc[0]-self.terrainExplosionRadius-55, currentLoc[0]+self.terrainExplosionRadius+55)
            drawTanks(players)
        else:
            pygame.draw.rect(gameDisplay, colors.SKY, (currentLoc[0], currentLoc[1], 3, 3))
        return hit

    def explode(self, location):
        for i in range(self.terrainExplosionRadius, 0, -1):
            pygame.draw.circle(gameDisplay, colors.getExplosionColor(i, self.terrainExplosionRadius), location, i)
        for col in range(location[0]-self.terrainExplosionRadius-2, location[0]+self.terrainExplosionRadius+2):
            for row in range(location[1]-self.terrainExplosionRadius-2, location[1]+self.terrainExplosionRadius+2):
                if col >= 0 and col < 1080 and row >= 0 and row < mapHeight:
                    if math.sqrt( (col-location[0])**2 + (row-location[1])**2 ) <= self.terrainExplosionRadius and terrain[row][col] == -1:
                        terrain[row][col] = 0
        pygame.display.update()
        time.sleep(0.25)
        pygame.draw.circle(gameDisplay, colors.SKY, location, self.terrainExplosionRadius)
        drawControlBoard(players[turn])
        pygame.display.update()
        drawTanks(players)

        # Damage tanks
        hitTankIds = []
        tanksHit = []
        damage = []
        for col in range(location[0]-self.tankDamageRadius-2, location[0]+self.tankDamageRadius+2):
            for row in range(location[1]-self.tankDamageRadius-2, location[1]+self.tankDamageRadius+2):
                if col >= 0 and col < 1080 and row >= 0 and row < mapHeight:
                    if terrain[row][col] > 0 and terrain[row][col] not in hitTankIds:
                        for i in players:
                            if i.idnum == terrain[row][col]:
                                hitTankIds.append(terrain[row][col])
                                tanksHit.append(i)
                                distance = math.sqrt( (col-(i.tankLoc[0]+25))**2 + (row-i.tankLoc[1]+17)**2 ) - 0.5*self.tankDamageRadius
                                if distance < 0:
                                    distance = 0
                                print('Hit at distance: ' + str(distance))
                                damage.append(self.getDamage(distance))

        for i in range(len(tanksHit)):
            tanksHit[i].updateHealth(-1*damage[i])
        drawTanks(players)
        time.sleep(1)

# TODO:
class Status:
    pass




















#==============================================================================
# Terrain Handling
#==============================================================================

def gravityUpdate():
    def setTank(player, x):
        maxy = mapHeight
        for col in range(x+9, x+43):
            for row in range(maxy):
                if terrain[row][col] == -1:
                    maxy = row
                    break
        tankLoc = (x, maxy-34)
        player.updateTankLoc((tankLoc[0]+25, tankLoc[1]+17))

        # Add to terrain array
        for col in range(x, x+50):
            for row in range(maxy-34, maxy):
                if row >= 0  and row < 670 and col >= 0 and col < 1080:
                    if terrain[row][col] == 0:
                        terrain[row][col] = player.idnum

        return tankLoc

    # Update Terrain
    global terrain

    print('Updating terrain')
    terrain = updateTerrain.update(terrain)
    for col in range(displayWidth):
        terrain[mapHeight-1][col] = -1
        terrain[mapHeight-2][col] = -1

    # Update Tanks
    print('Updating tanks')
    for player in players:
        player.tankLoc = setTank(player, player.tankLoc[0])

def drawTanks(tanks):
    def drawTank(player):
        gameDisplay.blit(player.tankImage, player.tankLoc)

        # Display player name above tank
        text = pygame.font.SysFont('couriernew', 12)
        TextSurf, TextRect = text_objects(player.name, text, player.RGBColor)
        TextRect.center = (player.tankLoc[0]+25, player.tankLoc[1] - 20)
        gameDisplay.blit(TextSurf, TextRect)

        # Display player health under nameplate
        pygame.draw.rect(gameDisplay, colors.CONTROLBOARDBACKGROUND, (player.tankLoc[0], player.tankLoc[1]-10, 50, 8))
        pygame.draw.rect(gameDisplay, player.RGBColor, (player.tankLoc[0], player.tankLoc[1]-10, int(player.tankHealth/2), 8))

        return player.tankLoc
    for i in tanks:
        drawTank(i)

def setTanks(tanks):
    def setTank(player, boundaries):
        x = rand.randint(boundaries[0], boundaries[1])
        maxy = mapHeight
        for col in range(x+9, x+43):
            for row in range(maxy):
                if terrain[row][col] == -1:
                    maxy = row
                    break
        tankLoc = (x, maxy-34)
        gameDisplay.blit(player.tankImage, tankLoc)
        player.updateTankLoc((tankLoc[0]+25, tankLoc[1]+17))

        # Add to terrain array
        for col in range(x, x+50):
            for row in range(maxy-34, maxy):
                if row >= 0  and row < 670 and col >= 0 and col < 1080:
                    if terrain[row][col] == 0:
                        terrain[row][col] = player.idnum

        # Display player name above tank
        text = pygame.font.SysFont('couriernew', 12)
        TextSurf, TextRect = text_objects(player.name, text, player.RGBColor)
        TextRect.center = (tankLoc[0]+25, tankLoc[1] - 20)
        gameDisplay.blit(TextSurf, TextRect)

        # Display player health under nameplate
        pygame.draw.rect(gameDisplay, colors.CONTROLBOARDBACKGROUND, (tankLoc[0], tankLoc[1]-10, 50, 8))
        pygame.draw.rect(gameDisplay, player.RGBColor, (tankLoc[0], tankLoc[1]-10, int(player.tankHealth/2), 8))

        return tankLoc

    # homeZoneWidth allows roughly even distribution of tanks. No tank will be placed on top of another
    homeZoneWidth = int(displayWidth/len(tanks))
    zoneNumber = 0
    for player in tanks:
        player.tankLoc = setTank(player, (zoneNumber*homeZoneWidth+50, (zoneNumber+1)*homeZoneWidth-50))
        zoneNumber += 1
    pygame.display.update()

def createInitialTerrain():
    global terrain

    terrain = np.zeros((mapHeight, displayWidth), dtype=np.int32)
    for i in range(displayWidth):
        terrain[mapHeight-1][i] = -1

    # getRandomFunction implemented into terrain array
    for col in range(displayWidth):
        # Sine function terrain
#        row = mapHeight - 200 + int(25*math.sin(col/50))

        # Flat terrain
        row = mapHeight - 100

        # Jagged random terrain
#        row = mapHeight - rand.randint(0, int(mapHeight*(2/3))) - 1
        terrain[row][col] = -1

    # fill everything under function
    for col in range(displayWidth):
        top = 0
        for row in range(mapHeight):
            if terrain[row][col] == -1:
                top = row
                break
        for row in range(top, mapHeight):
            terrain[row][col] = -1

def drawTerrain(xstart=0, xstop=1080):
    global terrain
    if xstart < 0:
        xstart = 0
    elif xstart > 1079:
        xstart = 1079
    if xstop < 1:
        xstop = 1
    elif xstop > 1080:
        xstop = 1080
    for col in range(xstart, xstop):
        pygame.draw.rect(gameDisplay, colors.SKY, (col, 0, 1, mapHeight))
    pygame.draw.rect(gameDisplay, colors.CONTROLBOARDBACKGROUND, (0, mapHeight, displayWidth, displayHeight))
    for col in range(xstart, xstop):
        for row in range(mapHeight):
            if terrain[row][col] == -1:
                pygame.draw.rect(gameDisplay, colors.getRandomGrassColor(), (col, row, 1, 1))

def drawControlBoard(player):
    pygame.draw.rect(gameDisplay, colors.CONTROLBOARDBACKGROUND, (0, mapHeight, displayWidth, displayHeight))
    text = pygame.font.SysFont('couriernew', 30)

    # Player Name
    TextSurf, TextRect = text_objects(player.name, text, player.RGBColor)
    TextRect.center = (80, 695)
    gameDisplay.blit(TextSurf, TextRect)

    # Wind
    TextSurf, TextRect = text_objects('Wind: ' + str(wind), pygame.font.SysFont('couriernew', 15), colors.BLACK)
    TextRect.center = (220, 685)
    gameDisplay.blit(TextSurf, TextRect)

    # Gravity
    TextSurf, TextRect = text_objects('Gravity: ' + str(gravity), pygame.font.SysFont('couriernew', 15), colors.BLACK)
    TextRect.center = (220, 705)
    gameDisplay.blit(TextSurf, TextRect)

    # Barrel Angle
    TextSurf, TextRect = text_objects(str(player.barrelAngle) + '°', text, colors.BLACK)
    TextRect.center = (385, 695)
    gameDisplay.blit(TextSurf, TextRect)

    # Power Bar
    pygame.draw.rect(gameDisplay, colors.BLACK, (425, 685, 200, 20))
    for i in range(2*player.power):
        pygame.draw.rect(gameDisplay, colors.getPowerBarColor(player.color, i), (425+i, 685, 1, 20))

    # Empty Weapon Slots
    for i in range(10):
        pygame.draw.rect(gameDisplay, colors.BLACK, (630+i*45, 675, 40, 40))

    # Weapons
    weaponsDir = 'weapons/'
    if operatingSystem == 'Windows':
        weaponsDir = 'weapons\\'

    for i in range(len(player.weapons)):
        gameDisplay.blit(player.weapons[i].image, (630+i*45, 675))
        TextSurf, TextRect = text_objects(str(player.weapons[i].timeUntilAvailable), text, player.RGBColor)
        TextRect.center = (652+i*45, 650)
        gameDisplay.blit(TextSurf, TextRect)

    currentSelection = 0
    for i in range(len(player.weapons)):
        if player.weapons[i] == player.currentWeapon:
            currentSelection = i
            break
    select = pygame.image.load(weaponsDir + 'weaponselect.png')
    gameDisplay.blit(select, (630+currentSelection*45, 675))

















#==============================================================================
# Primary Game Functions
#==============================================================================

def gameLoop():
    global pause
    global players
    global turn

    loadingScreen()
    print('Creating initial terrain')
    createInitialTerrain()

    # Get players
    print('Gathering player data')
    players = []
    textinput = TextInput()
    # TODO: Turn this into a game settings menu: planet, player num, gravity, terrain type (or intensity?)
    # TODO: Add Teams!!!!!
    while True:
        gameDisplay.fill(colors.WHITE)
        text = pygame.font.SysFont('couriernew', 35)
        TextSurf, TextRect = text_objects('How many players (2 min, 8 max)', text, colors.BLACK)
        TextRect.center = (displayWidth/2, displayHeight/2)
        gameDisplay.blit(TextSurf, TextRect)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                quitGame()
        if textinput.update(events):
            if textinput.get_text() in ['2', '3', '4', '5', '6', '7', '8']:
                numPlayers = int(textinput.get_text())
                break
        gameDisplay.blit(textinput.get_surface(), (displayWidth/2, displayHeight/2+35))
        pygame.display.update()
        clock.tick(30)

    loadingScreen()
    print('Creating player objects')
    for i in range(numPlayers):
        players.append(player('Player ' + str(i+1), colors.getColorFromPlayerNum(i), i+1))


    print('Drawing terrain')
    drawTerrain()
    print('Placing tanks')
    setTanks(players)
    print('Done')

    turn = 0
    while True:
        barrelChange = 0
        powerChange = 0
        endTurn = False
        players[turn].updateCurrentSelectedWeapon(1)
        drawTerrain(652, 1080)
        drawTanks(players)

        while True:

            # Control board Player ID
            drawControlBoard(players[turn])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quitGame()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        pause = True
                        paused()

                    # Rotate Barrel
                    elif event.key ==  pygame.K_LEFT:
                        barrelChange = -1
                    elif event.key == pygame.K_RIGHT:
                        barrelChange = 1

                    # Change Power
                    elif event.key == pygame.K_UP:
                        powerChange = 1
                    elif event.key == pygame.K_DOWN:
                        powerChange = -1

                    # Change Weapons
                    elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        players[turn].updateCurrentSelectedWeapon(1)
                    elif event.key == pygame.K_2 or event.key == pygame.K_KP1:
                        players[turn].updateCurrentSelectedWeapon(2)
                    elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        players[turn].updateCurrentSelectedWeapon(3)
                    elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        players[turn].updateCurrentSelectedWeapon(4)
                    elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        players[turn].updateCurrentSelectedWeapon(5)
                    elif event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        players[turn].updateCurrentSelectedWeapon(6)
                    elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        players[turn].updateCurrentSelectedWeapon(7)
                    elif event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        players[turn].updateCurrentSelectedWeapon(8)
                    elif event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        players[turn].updateCurrentSelectedWeapon(9)

                    # Move Tank
                    elif event.key == pygame.K_a:
                        pass
                    elif event.key == pygame.K_d:
                        pass

                    # Shoot
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        players[turn].shoot()
                        drawTanks(players)
                        endTurn = True
                        break

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        barrelChange = 0
                    elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        powerChange = 0

            if endTurn:
                break

            players[turn].moveBarrel(barrelChange)
            players[turn].changePower(powerChange)

            pygame.display.update()
            clock.tick(30)

        if len(players) == 1:
            break

        # Cooling weapons
        for i in range(len(players[turn].weapons)):
            players[turn].weapons[i].cool()

        turn += 1
        if turn >= len(players):
            turn = 0
        elif turn < 0:
            turn = 0

    gameOverScreen(players[0])

def gameOverScreen(winner):
    gameDisplay.fill(colors.WHITE)
    # TODO: Print game stats
    largeText = pygame.font.SysFont('couriernew', titleTextSize)
    TextSurf, TextRect = text_objects(winner.name, largeText)
    TextRect.center = (int(displayWidth/2), int(displayHeight/4))
    gameDisplay.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects('wins', largeText)
    TextRect.center = (int(displayWidth/2), int(displayHeight/2))
    gameDisplay.blit(TextSurf, TextRect)
    pygame.display.update()
    time.sleep(5)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitGame()
        button('CONTINUE', int(displayWidth/2)-((5/64)*displayWidth), int((3/4)*displayHeight), int((10/64)*displayWidth), int((5/48)*displayHeight), colors.GREEN, colors.BRIGHTGREEN, gameIntro)

        pygame.display.update()
        clock.tick(60)

def loadingScreen():
    loading = pygame.image.load('loadingScreen.png')
    gameDisplay.blit(loading, (0, 0))
    pygame.display.update()

def gameIntro():
    gameDisplay.fill(colors.WHITE)
    bg = pygame.image.load('tankBackground.jpg')
    gameDisplay.blit(bg, (0, 0))
    largeText = pygame.font.SysFont('couriernew', titleTextSize)
    smallText = pygame.font.SysFont('couriernew', buttonTextSize)
    TextSurf, TextRect = text_objects('Tanks', largeText)
    TextRect.center = (int(displayWidth/2), int(displayHeight/4))
    gameDisplay.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects('Ryan J. Slater', smallText)
    TextRect.center = ((displayWidth/2), (displayHeight/4)+int((1/12)*displayHeight))
    gameDisplay.blit(TextSurf, TextRect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitGame()
        button('PLAY', int((displayWidth/2)-(165/640)*displayWidth), int((3/4)*displayHeight), int((10/64)*displayWidth), int((5/48)*displayHeight), colors.GREEN, colors.BRIGHTGREEN, gameLoop)
        button('QUIT', int((displayWidth/2)+(65/640)*displayWidth), int((3/4)*displayHeight), int((10/64)*displayWidth), int((5/48)*displayHeight), colors.RED, colors.BRIGHTRED, quitGame)

        pygame.display.update()
        clock.tick(60)

def play(dw=1080, dh=720):
    global displayWidth
    global displayHeight
    global mapHeight
    global pause
    global gameDisplay
    global clock
    global options
    global gravity
    global wind

    pygame.init()
    displayWidth = dw
    displayHeight = dh
    mapHeight = displayHeight-50
    pause = False
    gravity = 9.8
    wind = 0
    gameDisplay = pygame.display.set_mode((displayWidth, displayHeight))
    pygame.display.set_caption('Tanks')
    clock = pygame.time.Clock()

    gameIntro()
    quitGame()

def TankGame():
    global titleTextSize
    global buttonTextSize
    titleTextSize = 115
    buttonTextSize = 30
    print('CWD: ' + os.getcwd())
    print('This File: ' + os.path.dirname(sys.argv[0]))
    if operatingSystem == 'Windows':
        print('Windows detected, changing CWD')
        os.chdir(os.path.dirname(sys.argv[0]))
        print('CWD: ' + os.getcwd())
    print()
    play()

if __name__ == '__main__':
    TankGame()

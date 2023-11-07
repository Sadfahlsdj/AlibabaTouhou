import pygame
import pygame.gfxdraw
import sys
import os
import math
import random
import numpy
from pygame.locals import *
from bullet import *
from player import *
import settings

pygame.init()
pygame.font.init()

"""TODO:
MAKE CODE MORE READABLE
attack 11: either reduce randomization and introduce another pattern, or increase density
attack idea: shots that leave trails that act as walls - done-ish (attack 13)
attack idea: https://discord.com/channels/824566586216022047/915467272330555392/1164376947632115776
            combine with attack 12 code, will make a flower pattern
attack idea: an attack like attack 13 that will force players to cross the boundaries 
    instead of just having random vertical shots to dodge
"""
fps = settings.fps
wh = 20
ww = 20
xlimit, ylimit = settings.xlimit, settings.ylimit
hole, holeMovement = 100, 20  # used for attack 2
a10XPos, a10YPos = xlimit / 2, ylimit / 5 # used for attack 10
a11XPos, a11YPos = xlimit / 2, ylimit / 5 # used for attack 11
(a12XPos, a12YPos, a12LeftX,
 a12LeftY, a12RightX, a12RightY) = xlimit / 2, ylimit / 5, 50, ylimit / 3, xlimit - 50, ylimit / 2
#used for attack 12
xvl, yvl, xvr, yvr = 4, 4, -4, 4 # used for attack 12 as well
screen = settings.screen
a14BigGroup = pygame.sprite.Group() #stores big shots where small shots originate from


def Attack0(spawncounter, walls, wall_group):  # random shots
    if spawncounter % int(fps / 5) == 0 and spawncounter >= 0:
        # every 10 ticks (0.2 seconds) next wave is spawned, adjust for balance
        # second condition is how bombs prevent bullet spawning
        for i in range(11):  # 11 bullets per wave, adjust for balance
            xrandompos = random.randint(0, xlimit - 50)
            yrandompos = 15 + random.randint(-30, 30)
            bu = Bullet(xrandompos, yrandompos, xrandompos, yrandompos, 4, 0, 0, False, False, 0, 0, 0,0, 255, 0, 0)
            walls.append(bu)
            bu.setXVel(random.randint(-1, 1))
            bu.setYVel(4)  # should be 4


def Attack1(spawncounter, walls, wall_group):  # moving safespot
    size = 10
    """if spawncounter < 250 or spawncounter > 500:
        size = 10
    else:
        size = 1"""
    if spawncounter % int(fps / 5) == 0 and spawncounter >= 0:
        global hole
        global holeMovement
        gap = 50  # gap in which to dodge in, change for balance
        for i in range(int(hole / 20)):
            xBulletPos = i * 20
            yBulletPos = 0
            bu = Bullet(xBulletPos, yBulletPos, xBulletPos, yBulletPos, size, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXVel(0)
            bu.setYVel(3)

            walls.append(bu)
            # bu.setxvel(0)
            # bu.setyvel(0)
        for i in range(int((hole + gap) / 20), xlimit):
            xBulletPos = i * 20
            yBulletPos = 60
            bu = Bullet(xBulletPos, yBulletPos, xBulletPos, yBulletPos, size, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXVel(0)
            bu.setYVel(3)
            walls.append(bu)
            # bu.setxvel(0)
            # bu.setyvel(0)
        hole += holeMovement

        if hole >= (xlimit - 60):
            holeMovement = -20
        if hole <= 60:
            holeMovement = 20


def Attack2(spawncounter, burstcounter, player, walls, wall_group):  # pseudotargeted walls
    playerX = player.getRect().x
    playerY = player.getRect().y
    if spawncounter % (int(fps / 4)) == 0 and spawncounter >= 0 and burstcounter % (int(2.5 * fps)) < (int(7 * fps / 4)):
        for i in range(int(xlimit/20)):
            xBulletPos = i * 20
            yBulletPos = 0
            bu = Bullet(xBulletPos, yBulletPos, xBulletPos, yBulletPos, 10, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXDiff(playerX - xBulletPos)
            bu.setYDiff(playerY - yBulletPos)
            bu.setXVel(bu.getXDiff() / 100.0)
            bu.setYVel(bu.getYDiff() / 100.0)
            walls.append(bu)
def Attack3(spawncounter, walls, wall_group):  # circular bursts of explosions
    if spawncounter % int(2.5 * fps) == 0 and spawncounter >= 0:
        for i in range(int(xlimit/40)):
            for j in range(17):
                xBulletPos = i * 40
                yBulletPos = 200
                bu = Bullet(xBulletPos, yBulletPos, xBulletPos, yBulletPos, 6, 0, 0, False, False, 0, 0, 0,0, 255, 0, 0)
                bu.setXVel(3 * math.sin(math.radians(j * 20)))
                bu.setYVel(3 * math.cos(math.radians(j * 20)))
                bu.setXVelSet(True)
                walls.append(bu)


def Attack4(spawncounter, attack4marker, walls, wall_group):
    # spiral shots from center, needs to be reworked badly
    if spawncounter % int(fps / 5) == 0 and spawncounter > 0:
        for i in range(4):
            for j in range(5):
                xBulletPos = xlimit / 2
                yBulletPos = ylimit / 2
                bu = Bullet(xBulletPos, yBulletPos, xBulletPos, yBulletPos, 6, 0, 0, False, False, 0, 0, 0, 0, spawncounter % 256,
                            (spawncounter + 50) % 256, (spawncounter + 100) % 256)
                bu.setXVel(3 * math.sin(math.radians((i * 6 + j) * 20) + attack4marker))
                bu.setYVel(3 * math.cos(math.radians((i * 6 + j) * 20) + attack4marker))
                bu.setXVelSet(True)
                walls.append(bu)

        for i in range(10): #anti safespot techniques
            bu = Bullet(50, i*25, 50, i*25, 30, 0, 0, False, False, 0, 0, 0,0, 255,0, 0)
            bu.setXVel(50)
            bu.setYVel(0)
            walls.append(bu)


def Attack5(spawncounter, walls, wall_group):  # slow shots from all directions
    bulletcount = 6  # number of bullets per wave, change for balance
    sc = int(2 * fps / 5)  # number of ticks between spawns, change for balance
    if spawncounter % sc == 0 and spawncounter > 0:
        for i in range(bulletcount):  # top bullets
            xRandomPos = random.randint(0, xlimit)
            yRandomPos = 0
            bu = Bullet(xRandomPos, yRandomPos, xRandomPos, yRandomPos,6, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            walls.append(bu)
            bu.setXVel(0)
            bu.setYVel(3)
    if spawncounter % sc == int(sc / 4) and spawncounter > 0:
        for i in range(bulletcount):  # bottom bullets
            xRandomPos = random.randint(0, xlimit)
            yRandomPos = ylimit
            bu = Bullet(xRandomPos, yRandomPos, xRandomPos, yRandomPos, 6, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            walls.append(bu)
            bu.setXVel(0)
            bu.setYVel(-3)
    if spawncounter % sc == int(sc / 2) and spawncounter > 0:
        for i in range(bulletcount):  # left bullets
            xRandomPos = 30
            yRandomPos = random.randint(0, ylimit)
            bu = Bullet(xRandomPos, yRandomPos, xRandomPos, yRandomPos, 6, 0, 0, False, False, 0, 0, 0, 0, 0, 0, 255)
            walls.append(bu)
            bu.setXVel(3)
            bu.setYVel(0)
    if spawncounter % sc == int(3 * sc / 4) and spawncounter > 0:
        for i in range(bulletcount):  # right bullets
            xRandomPos = xlimit
            yRandomPos = random.randint(0, ylimit)
            bu = Bullet(xRandomPos, yRandomPos, xRandomPos, yRandomPos, 6, 0, 0, False, False, 0, 0, 0, 0, 0, 0, 255)
            walls.append(bu)
            bu.setXVel(-3)
            bu.setYVel(0)


def Attack6(spawncounter, walls, wall_group):  # flower shaped bursts
    xPos = random.randint(0, xlimit)
    yPos = random.randint(0, int(ylimit / 3))
    if spawncounter % int(fps / 7) == 0 and spawncounter >= 0:
        r, g, b = random.randint(50, 220), random.randint(50, 220), random.randint(50, 220)
        for i in range(29):
            bu = Bullet(xPos, yPos, xPos, yPos, 6, 0, 0, False, False, 0, 0, 0, 0, r, g, b)
            bu.setXVel(3.5 * math.sin(math.radians((i * 12))))
            bu.setYVel(3.5 * math.cos(math.radians((i * 12))))
            bu.setXVelSet(True)
            walls.append(bu)


def Attack7(spawncounter, walls, player, wall_group):  # flower burst + targeted shots
    xPos = random.randint(0, xlimit)
    yPos = random.randint(0, int(ylimit / 3))
    if spawncounter % int(fps / 6) == 0 and spawncounter >= 0:
        r, g, b = random.randint(50, 220), random.randint(50, 220), random.randint(50, 220)
        for i in range(19):
            bu = Bullet(xPos, yPos, xPos, yPos, 6, 0, 0, False, False, 0, 0,0, 0,  r, g, b)
            bu.setXVel(3 * math.sin(math.radians((i * 18))))
            bu.setYVel(3 * math.cos(math.radians((i * 18))))
            bu.setXVelSet(True)

            walls.append(bu)
    playerX = player.getRect().x
    playerY = player.getRect().y
    if spawncounter % int(fps / 12) == 0 and spawncounter >= 0:
        xbulletpos = (3.5 * spawncounter) % xlimit
        ybulletpos = 50
        bu = Bullet(xbulletpos, ybulletpos, xbulletpos, ybulletpos, 8, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
        bu.setXDiff(playerX - xbulletpos)
        bu.setYDiff(playerY - ybulletpos)
        bu.setXVel(bu.getXDiff() / 100.0)
        bu.setYVel(bu.getYDiff() / 100.0)
        walls.append(bu)

def Attack8(spawncounter, attackduration, walls, wall_group):
    # shots originate in rotating patterns; straight downwards secondary pattern
    xpos = [3 * xlimit/12, 5 * xlimit/12, 7 * xlimit/12, 9 * xlimit/12]
    ypos = [ylimit/4, ylimit/2, ylimit/2, ylimit/4]
    spawnDelay = int(fps / 30) #makes shit easier for me
    if spawncounter % spawnDelay == 0 and spawncounter >= 0:
        for i in range(3):
            bu = Bullet(xpos[i], ypos[i], xpos[i], ypos[i], 5, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXVel((3 + spawncounter % 3) * math.sin(9 * (math.radians(spawncounter + 90*i))))
            bu.setYVel((3 + spawncounter % 3) * math.cos(9 * (math.radians(spawncounter + 90*i))))
            bu.setXVelSet(True)
            walls.append(bu)

    if spawncounter % int(2 * fps / 5) == 0 and spawncounter >= 0 and attackduration >= (7 * fps):
        for i in range(5):  # 5 bullets per wave, adjust for balance
            xrandompos = random.randint(0, xlimit)
            yrandompos = 60
            r, g, b = random.randint(50, 220), random.randint(50, 220), random.randint(50, 220)
            bu = Bullet(xrandompos, yrandompos, xrandompos, yrandompos, 5, 0, 0, False, False, 0, 0, 0, 0, r, g, b)
            walls.append(bu)
            bu.setXVel(0)
            bu.setYVel(4)  # should be 4
def Attack9(spawncounter, attackduration, walls, wall_group):
    # probably scrapped soon, just don't worry about it
    spawnTimeMarker = ((spawncounter // int(fps * 1.5)) + 1) % 8
    #print("spawntimemarker", spawnTimeMarker)
    if spawnTimeMarker < 1:
        spawnTimeMarker = 1
    sm = 6.2 + (spawnTimeMarker % 3) # speedmodifier, change for bullet speed
    if spawncounter % int(fps / 17) == 0:
        xpos = xlimit - (spawnTimeMarker % 8) * xlimit/8
        sm2 = 7 + (xpos % (xlimit/2)) / (xlimit/8)
        ypos = ylimit / 20
        for i in range(7):  # 8 bullets per wave, adjust for balance
            bu = Bullet(xpos, ypos, xpos, ypos, 2, 0, 0, False, False, 0, 0, spawnTimeMarker,
                        0, (spawnTimeMarker % 255), (spawnTimeMarker + 50) % 255, (spawnTimeMarker + 100) % 255)
            b2 = Bullet(xlimit - xpos, ypos, xlimit - xpos, ypos, 2, 0, 0, False, False, 0, 0, spawnTimeMarker,
                        0, (spawnTimeMarker % 255), (spawnTimeMarker + 50) % 255, (spawnTimeMarker + 100) % 255)
            bu.setXVel(random.uniform(-1 * sm2, sm2))
            bu.setYVel(math.sqrt((2 * sm2 ** 2) - bu.getXVel() ** 2))
            b2.setXVel(random.uniform(-1 * sm2, sm2))
            b2.setYVel(math.sqrt((2 * sm2 ** 2) - bu.getXVel() ** 2))
            walls.append(bu)
            walls.append(b2)
            #print("bullet xpos", xpos)

def Attack10(spawncounter, attackduration, walls, wall_group):
    #moving "center" that spawns multiple rings of shots
    global a10XPos
    global a10YPos
    if spawncounter % int(fps / 2) == 0 and spawncounter >= 0:
        r, g, b = random.randint(50, 220), random.randint(50, 220), random.randint(50, 220)
        for i in range(29):
            bu = Bullet(a10XPos, a10YPos, a10XPos, a10YPos, 6, 0, 0, False, False, 0, 0, 0, 0, 0, 0, 255)
            bu.setXVel(5 * math.sin(math.radians((i * 12))))
            bu.setYVel(5 * math.cos(math.radians((i * 12))))
            bu.setXVelSet(True)
            walls.append(bu)

        #entire next section keeps the "center" within the top third of the screen in y value
        #and within the screen in x value, and moves the center by somewhat random values
        if a10XPos < xlimit/10 or a10XPos > 9*xlimit/10:
            if a10XPos < xlimit/10:
                a10XPos += xlimit / 10
            else:
                a10XPos -= xlimit / 10
        else:
            a10XPos += random.randint(int(-xlimit / 10), int(xlimit / 10))
        if a10YPos < ylimit/20 or a10YPos > ylimit/3:
            if a10YPos < ylimit / 20:
                a10YPos += ylimit / 10
            else:
                a10YPos -= ylimit / 10
        else:
            a10YPos += random.randint(int(-ylimit / 10), int(ylimit / 10))
    #second ring
    if spawncounter % int(fps / 2) == 10 and spawncounter >= 0:
        r, g, b = random.randint(50, 220), random.randint(50, 220), random.randint(50, 220)
        for i in range(29):
            bu = Bullet(a10XPos, a10YPos, a10XPos, a10YPos, 6, 0, 0, False, False, 0, 0, 0, 0, 0, 0, 255)
            bu.setXVel(3.5 * math.sin(math.radians((i * 12)) + math.pi/12))
            bu.setYVel(3.5 * math.cos(math.radians((i * 12)) + math.pi/12))
            bu.setXVelSet(True)
            walls.append(bu)
    #third ring (big shots)
    if spawncounter % int(fps / 2) == int(fps / 3) and spawncounter >= 0:
        r, g, b = random.randint(50, 220), random.randint(50, 220), random.randint(50, 220)
        for i in range(24):
            bu = Bullet(a10XPos, a10YPos, a10XPos, a10YPos, 18, 0, 0, False, False, 0, 0, 0, 0, r, g, b)
            bu.setXVel(4 * math.sin(math.radians((i * 15))))
            bu.setYVel(4 * math.cos(math.radians((i * 15))))
            bu.setXVelSet(True)
            walls.append(bu)

def Attack11(spawncounter, attackduration, walls, wall_group):
    #sets of circular shots with bursts of random shots
    global a11XPos
    global a11YPos
    if spawncounter % int(fps * 2) <= int(2 * fps / 5) and spawncounter >= 0:
        #burst of circular shots
        for i in range(45):
            bu = Bullet(a11XPos, a11YPos, a11XPos, a11YPos, 4, 0, 0, False, False, 0, 0, 0, 0, 80, 80, 80)
            bu.setXVel(5.5 * math.sin(math.radians((i * 8))))
            bu.setYVel(5.5 * math.cos(math.radians((i * 8))))
            bu.setXVelSet(True)
            walls.append(bu)

        if spawncounter % int(fps * 2) == int(fps / 5):
            #burst of random shots
            for i in range(120):
                #using xdiff = 1 to differentiate these bullets from previous ones
                #randomization of velocity is done in main method
                bu = Bullet(a11XPos, a11YPos, a11XPos, a11YPos, 5, 0, 0, False, False, 1, 0, attackduration, 0, 255, 0, 0)
                bu.setXVel(2.5 * math.sin(math.radians((i*3))))
                bu.setYVel(2.5 * math.cos(math.radians((i*3))))
                bu.setXVelSet(True)
                walls.append(bu)
        if spawncounter % int(fps * 2) == int(2 * fps / 5):
            #change position of center, keeps it within bounds
            if a11XPos < xlimit/10 or a11XPos > 9*xlimit/10:
                if a11XPos < xlimit/10:
                    a11XPos += xlimit / 10
                else:
                    a11XPos -= xlimit / 10
            else:
                a11XPos += random.randint(int(-xlimit / 10), int(xlimit / 10))
            if a11YPos < ylimit/20 or a11YPos > ylimit/3:
                if a11YPos < ylimit / 20:
                    a11YPos += ylimit / 10
                else:
                    a11YPos -= ylimit / 10
            else:
                a11YPos += random.randint(int(-ylimit / 10), int(ylimit / 10))

def Attack12(spawncounter, attackduration, walls, wall_group):
    #circular patterns, rows of shots from side, spiral shots (see remilia's 3rd life bar spellcard)
    global a12XPos, a12YPos, a12LeftX, a12LeftY, a12RightX, a12RightY
    global xvl, yvl, xvr, yvr #x vel left, y vel left, x vel right, y vel right
    cr, cg, cb = 255, random.randint(0, 100), random.randint(0, 100) #circle r, g, b
    if spawncounter % int(fps / 5) == 0 and spawncounter % int(2.4 * fps) < int(2 * fps) and spawncounter >= 0:
        for i in range(36): #circular patterns
            bu = Bullet(a12XPos, a12YPos, a12XPos, a12YPos, 6, 0, 0, False, False, 0, 0, 0, 0, cr, cg, cb)
            bu.setXVel(3.5 * math.sin(math.radians((i * 10))))
            bu.setYVel(3.5 * math.cos(math.radians((i * 10))))
            bu.setXVelSet(True)
            walls.append(bu)

    if spawncounter % fps == 0 and spawncounter % int(2 * fps) < int(0.6 * fps) and spawncounter >= 0: #velocity for side rows
        xvl = 0.85 * random.randint(3, 5)
        yvl = 0.85 * math.sqrt(50 - (xvl ** 2))
        xvr = -0.85 * random.randint(3, 5)
        yvr = 0.85 * math.sqrt(50 - (xvl ** 2))
        #randomization of velocity done outside of secondary loop
    if spawncounter % int(fps / 5) == 0 and spawncounter % int(2 * fps) < int(0.6 * fps) and spawncounter >= 1:
        #left & right rows
        xv, yv = xvl, yvl
        xv2, yv2 = xvr, yvr
        for i in range(10):
            bu = Bullet(a12LeftX, ((xlimit / 6) - (xlimit / 30) * i) + a12LeftY, a12LeftX, ((xlimit / 6) - (xlimit / 30) * i) + a12LeftY,
                        5, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu2 = Bullet(a12RightX, ((xlimit / 6) - (xlimit / 30) * i) + a12RightY, a12LeftX, ((xlimit / 6) - (xlimit / 30) * i) + a12LeftY,
                         5, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXVel(xv)
            bu.setYVel(yv)
            bu2.setXVel(xv2)
            bu2.setYVel(yv2)
            walls.append(bu)
            walls.append(bu2)
    if spawncounter % int(2.4 * fps) == 0 and spawncounter >= 0:
        circleRadius = 100 #radius of circle that shots spawn around
        r, g, b = random.randint(20, 235), random.randint(20, 235), random.randint(20, 235)
        for i in range(360):  # orbiting shots
            xOffset = circleRadius * math.sin(math.radians(i))
            yOffset = circleRadius * math.cos(math.radians(i))
            if xOffset == 0: #hardcoding to prevent division by 0
                if yOffset < 0:
                    shotAngle = numpy.pi / 4
                elif yOffset > 0:
                    shotAngle = 3 * numpy.pi / 4
            else:
                shotAngle = numpy.arctan(yOffset / xOffset)
            bu = Bullet(a12XPos + (circleRadius * math.sin(math.radians(i * 5))), a12YPos + (circleRadius * math.cos(math.radians(i * 5))),
                        a12XPos + (circleRadius * math.sin(math.radians(i * 5))), a12YPos + (circleRadius * math.cos(math.radians(i * 5))),
                        6, 0, 0, False, True, a12XPos, a12YPos, spawncounter, 0, r + random.choice([-20, 20]), g + random.choice([-20, 20]), b + random.choice([-20, 20]))
            #xdiff, ydiff are coords of center
            #shotangle is angle from center
            #yvelset is true as a marker

            # next section determines the weird movement for after the spinning finishes
            baseVel = 0.01 * 1.1 ** (abs(i % 60 - 30) / 2.0)
            bu.setXVel(baseVel * (bu.rect.x - bu.getXDiff()))
            bu.setYVel(baseVel * (bu.rect.y - bu.getYDiff()))
            bu.setYVelSet(True)
            walls.append(bu)
    if spawncounter % int(2.3 * fps) == 0 and spawncounter >= 0:
        #position changing for "center" of attacks, keeps it in bounds
        if a12XPos < xlimit / 10 or a12XPos > 9 * xlimit / 10:
            if a12XPos < xlimit / 10:
                a12XPos += xlimit / 10
            else:
                a12XPos -= xlimit / 10
        else:
            a12XPos += random.randint(int(-xlimit / 10), int(xlimit / 10))
        if a12YPos < ylimit / 20 or a12YPos > ylimit / 3:
            if a12YPos < ylimit / 20:
                a12YPos += ylimit / 10
            else:
                a12YPos -= ylimit / 10
        else:
            a12YPos += random.randint(int(-ylimit / 10), int(ylimit / 10))

    #below is scrapped (changing center of side shots), just keeping it here in case
    """if spawncounter % 100 == 0 and spawncounter >= 0: #position changing for left shots
        print(a12lefty)
        if a12lefty > 4 * ylimit / 5 or a12lefty < ylimit / 5:
            if a12lefty > 4 * ylimit / 5:
                a12lefty -= ylimit / 5
            else:
                a12lefty += ylimit / 5
        else:
            a12lefty += random.choice([-1, 1]) * ylimit / 4"""

def Attack13(spawncounter, attackduration, player, walls, wall_group):
    #NEEDS WORK.
    #lines spawn that slowly restrict available space
    lineColor = (255, 0, 0)

    if attackduration > 3 * fps and attackduration % 48 > 10: #smallest grid
        for i in range(2):
            bu = Bullet((i + 1) * xlimit/3, 20, (i + 1) * xlimit/3, 0, 2, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu2 = Bullet(20, (i + 1) * ylimit/3, 0, (i + 1) * ylimit/3, 2, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXVel(0)
            bu.setYVel(2)
            bu2.setXVel(2)
            bu2.setYVel(0)
            walls.append(bu)
            walls.append(bu2)
    if attackduration > 6 * fps and attackduration % 48 > 10: #second grid
        for i in range(3):
            bu = Bullet((2*i + 1) * xlimit/6, 0, (2*i + 1) * xlimit/6, 0, 2, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu2 = Bullet(20, (2*i + 1) * ylimit/6, 0, (2*i + 1) * ylimit/6, 2, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXVel(0)
            bu.setYVel(2)
            bu2.setXVel(2)
            bu2.setYVel(0)
            walls.append(bu)
            walls.append(bu2)
    if attackduration > 9 * fps and attackduration % 48 > 10: #most restrictive grid
        for i in range(5):
            bu = Bullet((2*i + 1) * xlimit/12, 0, (2*i + 1) * xlimit/12, 0, 2, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu2 = Bullet(20, (2*i + 1) * ylimit/12, 0, (2*i + 1) * ylimit/12, 2, 0, 0, False, False, 0, 0, 0, 0, 255, 0, 0)
            bu.setXVel(0)
            bu.setYVel(2)
            bu2.setXVel(2)
            bu2.setYVel(0)
            walls.append(bu)
            walls.append(bu2)

    if spawncounter % int(fps / 8) == 0 and spawncounter >= 0 and spawncounter % (fps * 4) <= (fps * 2):
        #targeted shots from corners
        #targets an area thats kind of around the player
        for i in range(4):
            xPos = (((i // 2) + 1) % 2) * (9 * xlimit / 10) + random.uniform(5, xlimit / 20)
            yPos = (i % 2) * (9 * ylimit / 10) + random.uniform(5, ylimit / 20)
            #print(str(xPos), str(yPos))
            xDiff = (player.getRect().x) - xPos + random.uniform(-5, 5)
            yDiff = (player.getRect().y) - yPos + random.uniform(-5, 5)
            bu = Bullet(xPos, yPos, xPos, yPos, 2, 0, 0, False, False, xDiff, yDiff, 0, 0, 0, 0, 255)
            bu.setXVel(xDiff / (fps * 5))
            bu.setYVel(yDiff / (fps * 5))
            walls.append(bu)

    if spawncounter % int(fps / 3) == 0 and spawncounter >= 0:
        #random vertical shots
        #each vertical spread (1/12th of field) will have its own shots
        for i in range(12):
            r = 235 + random.randint(-20, 20)
            g = 235 + random.randint(-20, 20)
            b = 20 + random.randint(-20, 20)
            for j in range(2):
                xrandompos = random.randint(i * xlimit / 12, (i + 1) * xlimit / 12)
                yrandompos = random.randint(0, 30)
                bu = Bullet(xrandompos, yrandompos, xrandompos, yrandompos, 3, 0, 0, False, False, 0, 0, 0,0, r, g, b)
                walls.append(bu)
                bu.setXVel(0)
                bu.setYVel(2)

def Attack14(spawncounter, attackduration, player, walls, wall_group):
    global a14BigGroup
    centerX = player.getRect().x
    centerY = player.getRect().y
    circleRadius = 100  # radius of circle that shots spawn around
    if spawncounter % int(1.5 * fps) == 0 and spawncounter >= 0:
        r, g, b = random.randint(20, 235), random.randint(20, 235), random.randint(20, 235)
        for i in range(5):  # orbiting shots
            xOffset = circleRadius * math.sin(math.radians(i))
            yOffset = circleRadius * math.cos(math.radians(i))
            if xOffset == 0:  # hardcoding to prevent division by 0
                if yOffset < 0:
                    shotAngle = numpy.pi / 4
                elif yOffset > 0:
                    shotAngle = 3 * numpy.pi / 4
            else:
                shotAngle = numpy.arctan(yOffset / xOffset)
            bu = Bullet(centerX + (circleRadius * math.sin(math.radians(i * 72))),
                        centerY + (circleRadius * math.cos(math.radians(i * 72))),
                        centerX + (circleRadius * math.sin(math.radians(i * 72))),
                        centerY + (circleRadius * math.cos(math.radians(i * 72))),
                        10, 0, 0, False, True, centerX, centerY, attackduration, circleRadius, r + random.choice([-20, 20]),
                        g + random.choice([-20, 20]), b + random.choice([-20, 20]))
            #shotangle used to set starting radius
            # xdiff, ydiff are coords of center
            """baseVel = 0.01 * 1.1 ** (abs(i % 60 - 30) / 2.0)
            bu.setXVel(baseVel * (bu.rect.x - bu.getXDiff()))
            bu.setYVel(baseVel * (bu.rect.y - bu.getYDiff()))
            bu.setYVelSet(True)"""
            bu.setXVel(0)
            bu.setYVel(0)
            walls.append(bu)
            a14BigGroup.add(bu)
    for b in a14BigGroup:
        if b.getSpawntime() + fps <= attackduration <= b.getSpawntime() + 2*fps:
            if spawncounter % int(fps / 6) == 0 and spawncounter >= 0:
                buOutward = Bullet(b.getTrueX(), b.getTrueY(), b.getTrueX(), b.getTrueY(),6,
                0, 0, False, False, centerX, centerY, attackduration, circleRadius,
                    random.randint(200, 250), random.randint(80, 120), 0)
                buInward = Bullet(b.getTrueX(), b.getTrueY(), b.getTrueX(), b.getTrueY(), 4,
                                   0, 0, False, False, centerX, centerY, attackduration, circleRadius,
                                   random.randint(200, 250), random.randint(80, 120), 0)
                buOutward.setXVel((b.getTrueX() - b.getXDiff()) / fps)
                buOutward.setYVel((b.getTrueY() - b.getYDiff()) / fps)
                buInward.setXVel((b.getTrueX() - b.getXDiff()) / (-1 * fps))
                buInward.setYVel((b.getTrueY() - b.getYDiff()) / (-1 * fps))
                walls.append(buOutward)
                walls.append(buInward)
        if attackduration > (b.getSpawntime() + 8 * fps):
            b.kill()








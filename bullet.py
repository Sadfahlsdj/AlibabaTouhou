import pygame
import pygame.gfxdraw
import sys
import os
import math
import random
from pygame.locals import *

pygame.init()
pygame.font.init()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, trueX, trueY, size, xvel, yvel, xvelset, yvelset, xdiff, ydiff, spawntime, shotAngle, r, g, b):
        BulletImg = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.trueX = trueX
        self.trueY = trueY
        self.r = r
        self.g = g
        self.b = b
        self.shotAngle = shotAngle
        self.image = BulletImg #DO NOT CHANGE
        self.size = size
        self.spawntime = spawntime #used for attack 9
        self.x = self.x + self.size / 2
        self.y = self.y + self.size / 2
        self.radius = self.size / 2
        # self.image.fill((r, g, b))
        self.center = (x, y)  # rect stuff used for collision
        self.rect = self.image.get_rect(center=(self.center))
        pygame.gfxdraw.filled_circle(BulletImg, size, size, size, (r, g, b))
        self.xvel = xvel
        self.yvel = yvel
        self.xvelset = xvelset  # has x velocity been set for this bullet?
        self.yvelset = yvelset  # has y velocity been set for this bullet?
        self.xdiff = xdiff
        self.ydiff = ydiff

    def __iter__(self):
        return self  # makes my shit iterable
    def changeColor(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def getRadius(self):
        return self.radius

    def get_center(self):
        return (self.x, self.y)

    def getShotAngle(self):
        return self.shotAngle

    def setShotAngle(self, sa):
        self.shotAngle = sa

    def getTrueX(self):
        return self.trueX

    def setTrueX(self, tx):
        self.trueX = tx

    def getTrueY(self):
        return self.trueY

    def setTrueY(self, ty):
        self.trueY = ty

    def getXVel(self):
        return self.xvel  # get x velo

    def setXVel(self, vel):  # set x velocity
        self.xvel = vel

    def getYVel(self):
        return self.yvel

    def setYVel(self, vel):  # set y velocity
        self.yvel = vel

    def setYVelSet(self, v): # used to mark bullet as part of a group, as is xvelset stuff
        self.yvelset = v

    def getYVelSet(self):
        return self.yvelset

    def setXVelSet(self, v):
        self.xvelset = v

    def getXVelSet(self):
        return self.xvelset

    def setXDiff(self, v):  # used for attack 2, as are the next 3 functions
        #used in attack 12 to mark the center of where the bullet rotates around
        self.xdiff = v

    def getXDiff(self):
        return self.xdiff

    def setYDiff(self, v):
        self.ydiff = v

    def getYDiff(self):
        return self.ydiff

    def getSpawntime(self): #used for attack 9
        return self.spawntime

    def getRect(self): #do not change
        return self.rect


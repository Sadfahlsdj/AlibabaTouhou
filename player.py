import pygame
import pygame.gfxdraw
import sys
import os
import math
import random
from pygame.locals import *
pygame.init()
pygame.font.init()


class Player(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        self.radius = size/2
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        aimg = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(aimg, size, size, size, (0, 255, 0))
        self.image = aimg
        self.rect = self.image.get_rect(center=(x, y))

    def getRadius(self):
        return float(self.radius)
    def getCenter(self):
        return (self.x, self.y)
    def getRect(self):
        return self.rect



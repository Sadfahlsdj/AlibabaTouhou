import pygame
import pygame.gfxdraw
import sys
import os
import math
import random
from pygame.locals import *
import numpy
import attacks
import settings
from bullet import *
from player import *

pygame.init()
pygame.font.init()

pygame.display.set_caption("ALIBABA TOUHOU")  # window name

# DEFAULT TOUHOU CONTROLS, SHIFT FOR FOCUS X FOR BOMB ARROW MOVEMENT
# description for the unitiated - focus will slow down movespeed
# -bomb will clear all projectiles onscreen and prevent new ones for 3 seconds, 4 second cd, limited use

# LIVES R FUCKING HARDCODED, IF I EVER ADD A WAY TO GAIN MORE LIVES THEN MAKE SURE TO RE-HARDCODE THEM

# important - attacks are now in attacks.py, same w/ bullet.py and player.py

"""
make xlimit, ylimit, and fps a global variable instead of changing per file
TODO: CHANGE TO 60 FPS - done
REWRITE VELOCITY/POSITION TO USE FLOAT INSTEAD OF INT VALUES TO ALLOW FOR MORE COMPLEX PATTERNS
-done
check for hits after rendering current frame - done
maybe need to nerf attack 3
fix top left safespot in attack 4 - done, probably
make bullets & player circular, rewrite collision check - done
fix collisions for attack 10 - done
far down the line: make a cache of bullets near the player and only run collision checks on those in order
to improve speed at the cost of memory
the pseudocode for a cache would be like (according to birb)
reinitializing per tick:
cache = [pixels.x/scale][pixels.y/scale]

bullet tick:
cache[bullet.x/scale][bullet.y/scale].append(bullet)

player tick (for collisions):
foreach in cache[player.x/scale][player.y/scale] do collision check

pixels.x and .y being size of screen, scale being size of bullet sprite

alternatively: split window into static sectors, only do collision checks if bullet & player
are in the same sector"""


def findDistance(player, bullet):
    #possible issue due to top left bias
    playerx, playery = player.getRect().x + player.getRadius(), player.getRect().y + player.getRadius()
    bulletx, bullety = bullet.getRect().x + bullet.getRadius(), bullet.getRect().y + bullet.getRadius()
    return math.sqrt((playerx - bulletx) ** 2 + (playery - bullety) ** 2)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    fps = settings.fps
    bg = [255, 255, 255]
    xlimit, ylimit = settings.xlimit, settings.ylimit #600, 480 formerly
    screen = settings.screen
    ph, pw = 4, 4  # player height, player width
    wh, ww = 20, 20  # wall height, width

    player = Player(ph, xlimit/2, 4 * ylimit/5)  # initial position, height, width in that order
    player.move = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]  # just see below for movement logic
    #player.move = [pygame.K_j, pygame.K_l, pygame.K_i, pygame.K_k] #alt movement for birb
    # player.v = 5 #player velocity; moved to within the while loop
    byvel = 5  # bullet yvel initial value
    bxvel = 0  # just a definition, this is done at the bottom of the loop where velocity logic is actually done

    player_group = pygame.sprite.Group()
    player_group.add(player)

    walls = []
    wall_group = pygame.sprite.Group()  # this shit NEEDS to be declared outside the while loop or it spazzes
    spawncounter = 1  # ticking for spawning

    bombs = 3  # bomb count
    bombcd = 0  # bomb cooldown

    iframes = 0  # take a guess
    status = 0  # 0 for start screen, 1 for game, 2 for death, 3 for win
    startingatk = 0 #use for attack selector
    maxattack = 14 #highest attack value that exists
    attackchangeticks = 0 #so that attack only changes once per button press
    attack = 0  # 0 for random, 1 for moving safespot, 2 for rows of targeted shots;
    # 3 is for sets of circular explosions, 4 for flowers of mortality
    # 5 for slow moving shots from all directions
    # change the value in status==0 to test individual attacks
    hole = 100  # xpos where there will be a gap in shots; used for attack #1
    holemovement = 20  # used for attack #1
    attackduration = 0  # ticks up, used to end attacks
    adelay = fps * 3 #attack delay between attacks to get rid of lingering shots
    adcap = fps * 10  # registering up here for testing
    burstcounter = 0  # used for attack 2
    attack4marker = -1.8  # used for attack 4
    #vecX, vecY = 1, 1 #used for attack 12

    lives = 3  # lives count

    lifeimage = pygame.image.load("lifecounterimage.png").convert()
    playerimage = pygame.image.load("playerchar.png").convert()
    playerimage.set_colorkey((0, 0, 0))
    pygame.Surface.convert_alpha(playerimage) #these two lines make background transparent



    deadrandom = random.randint(0, 2)  # needs to be outside the loop; determines which string is displayed on death
    # exit logic
    loop = True
    while loop:
        #print(player.getRect().x - player.getRadius(), player.getRect().y - player.getRadius())
        if status == 0:
            screen.fill((0, 0, 0))
            if attackchangeticks > 0:
                attackchangeticks -= 1
            # print("dead")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
            key = pygame.key.get_pressed()
            if key[pygame.K_z]:  # begins game
                lives = 4  # change to higher than 3 for debugging
                bombs = 3
                status = 1
                #attack = 0  obsolete, attack changer is implemented
                attackduration = 0
                iframes = fps * 2
                hole = 100
                holemovement = 20
            if key[pygame.K_UP]:
                if attackchangeticks == 0:
                    if attack == maxattack:
                        attack = 0
                    else:
                        attack += 1
                attackchangeticks = 3
            if key[pygame.K_DOWN]:
                if attackchangeticks == 0:
                    if attack == 0:
                        attack = maxattack
                    else:
                        attack -= 1
                attackchangeticks = 3

            newfont = pygame.font.SysFont("Arial", 24)
            winstring = ["Abject Failure", "Wait... really?", "This sucks..."]

            textcolor = [255, 255, 255]
            introtext = newfont.render("Welcome to Alibaba Touhou", True, (textcolor))
            begintext = newfont.render("Z to begin", True, (textcolor))
            lvlselecttext = newfont.render("UP/DOWN arrow on this screen to select attack", True, (textcolor))
            lvlselectstring = "Attack: " + str(attack)
            lvlselecttext2 = newfont.render(lvlselectstring, True, (textcolor))
            tutorialtext1 = newfont.render("Arrow keys to move", True, textcolor)
            tutorialtext2 = newfont.render("Shift for focus mode (slows you down greatly)", True, textcolor)
            tutorialtext3 = newfont.render("X to bomb(clears projectiles), limited use", True, textcolor)
            screen.blit(introtext, (200, 25))
            screen.blit(begintext, (180, 125))
            screen.blit(tutorialtext1, (50, 225))
            screen.blit(tutorialtext2, (50, 325))
            screen.blit(tutorialtext3, (50, 425))
            screen.blit(lvlselecttext, (50, 525))
            screen.blit(lvlselecttext2, (50, 625))
            pygame.display.update()
            clock.tick(fps)

        if status == 1:
            for event in pygame.event.get():  # proper quitting
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # loop = 0
            if lives == 0:
                status = 2
                screen.fill((0, 0, 0))
            spawncounter += 1
            attackduration += 1

            if bombcd > 0:
                bombcd -= 1
            if iframes > 0:
                iframes -= 1

            for b in wall_group:
                coldistance = b.getRadius() * 2 + player.getRadius() * 2
                hit = findDistance(player, b) < coldistance
                # print(coldistance, findDistance(player, bullet))
                if hit:
                    b.kill()
                    for w in wall_group:
                        w.kill()
                    iframes = fps * 2
                    textcolor = (0, 255, 255)
                    font = pygame.font.SysFont("Arial", 72)
                    bombtext = font.render("hit", True, (textcolor))  # will only show for 1 tick, fix pending lol
                    screen.blit(bombtext, (xlimit - 200, ylimit - 50))
                    if lives == 3:  # to deal w/ the issue that getting hit takes off multiple lives rapidly
                        lives = 2
                    elif lives == 2:
                        lives = 1
                    elif lives == 1:
                        lives = 0

            # attacks below
            if attack == 0:
                adcap = fps * 15
                attacks.Attack0(spawncounter, walls, wall_group)
                if attackduration == adcap:
                    attack = 1
                    attackduration = 0
                    spawncounter = 0 - adelay
                    for w in wall_group:
                        w.kill()
            if attack == 1:
                adcap = fps * 15

                if attackduration == adcap:
                    attack = 2
                    attackduration = 0
                    burstcounter = 100
                    spawncounter = 0 - adelay
                    for w in wall_group:
                        w.kill()
                attacks.Attack1(spawncounter, walls, wall_group)
            if attack == 2:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 3
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                burstcounter += 1
                attacks.Attack2(spawncounter, burstcounter, player, walls, wall_group)
            if attack == 3:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 4
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack3(spawncounter, walls, wall_group)
            if attack == 4:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 5
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attack4marker += 0.01
                attacks.Attack4(spawncounter, attack4marker, walls, wall_group)
            if attack == 5:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 6
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack5(spawncounter, walls, wall_group)
            if attack == 6:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 7
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack6(spawncounter, walls, wall_group)
            if attack == 7:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 8
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack7(spawncounter, walls, player, wall_group)
            if attack == 8:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 9
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0
                attacks.Attack8(spawncounter, attackduration, walls, wall_group)
            if attack == 9:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 10
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack9(spawncounter, attackduration, walls, wall_group)
            if attack == 10:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 11
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack10(spawncounter, attackduration, walls, wall_group)
            if attack == 11:
                adcap = fps * 15
                if attackduration == adcap:
                    attack = 12
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack11(spawncounter, attackduration, walls, wall_group)
            if attack == 12:
                adcap = fps * 20
                if attackduration == adcap:
                    attack = 13
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack12(spawncounter, attackduration, walls, wall_group)
            if attack == 13:
                adcap = fps * 20
                if attackduration == adcap:
                    attack = 14
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack13(spawncounter, attackduration, player, walls, wall_group)
            if attack == 14:
                adcap = fps * 150
                if attackduration == adcap:
                    status = 3
                    for w in wall_group:
                        w.kill()
                    attackduration = 0
                    spawncounter = 0 - adelay
                attacks.Attack14(spawncounter, attackduration, player, walls, wall_group)
            for w in walls:
                wall_group.add(w)
                walls.remove(w)  # probably necessary? didnt check lol

            key = pygame.key.get_pressed()
            if key[pygame.K_LSHIFT]:  # focus button; press to slowdown
                player.v = int(fps / 30)
            else:
                player.v = int(fps / 15)

            # player movement done efficiently
            for i in range(2):  # left, right (a, d)
                if key[player.move[i]]:

                    player.rect.x += player.v * [-1, 1][i]

            for i in range(2):  # up, down (w, s)
                if key[player.move[2:4][i]]:

                    player.rect.y += player.v * [-1, 1][i]

            if key[pygame.K_x] and bombs > 0 and bombcd == 0:  # bomb
                bombcd = 200
                for w in wall_group:
                    pygame.sprite.Sprite.kill(w)
                bombs -= 1
                spawncounter = -3 * fps

            # keeps player within screen; 4 * radius is hardcoded guessing
            if player.rect.x < 0 - player.getRadius():
                player.rect.x = 0 - player.getRadius()
            if player.rect.x + player.getRadius() > xlimit - 4 * player.getRadius():
                player.rect.x = xlimit - 4 * player.getRadius()
            if player.rect.y < 0 - player.getRadius():
                player.rect.y = 0 - player.getRadius()
            if player.rect.y + player.getRadius() > ylimit - 4 * player.getRadius():
                player.rect.y = ylimit - 4 * player.getRadius()

            screen.fill(bg)
            newfont = pygame.font.SysFont("Arial", 24)
            adtext = "Seconds in current attack:" + str(int(adcap / fps - attackduration / fps)) # atk duration text
            atkdurationtext = newfont.render(adtext, True, (0, 200, 230))
            screen.blit(atkdurationtext, (10, 10))

            for w in wall_group:
                # w.setxvelset(False)
                # w.rect.y += byvel
                if attack == 4:
                    # w.setxvel(w.getxvel() + math.sin(math.radians(attackduration % 15 * 24)))
                    # w.setyvel(w.getyvel() + math.cos(math.radians(attackduration % 15 * 24)))
                    w.setXVel(w.getXVel() * 1.02 + 0.04)
                    w.setYVel(w.getYVel() * 1.01 + 0.03)
                if attack == 9:
                    #w.setXVel(w.getXVel() * 0.988)
                    #w.setYVel(w.getYVel() * 0.988)
                    if attackduration % (8*75) > (75 * w.getSpawntime()):
                        #check attack9's spawnTimeMarker, coefficient here should be the same
                        w.setXVel(0)
                        w.setYVel(0)
                        w.changeColor(0, 0, 255)
                    if attackduration % (8*75) > (75 * w.getSpawntime() + (3 * fps)):
                        #print("killed")
                        # check attack9's spawnTimeMarker, coefficient here should be same and then double respectively
                        w.kill()
                    #print(w.getSpawntime())
                    #print(attackduration)
                if attack == 11:
                    if w.getXDiff() == 1:
                        if attackduration == (w.getSpawntime() + fps):
                            w.setXVel(2 * random.uniform(-2, 2))
                            w.setYVel(2 * random.uniform(0, 3))
                if attack == 12:
                    #print(str(w.getYVelSet()))
                    if w.getYVelSet() == True:
                        #if attackduration < (w.getSpawntime() + 2 * fps):
                        #distance from center is always sqrt(50^2 + 50^2)
                        """distance = math.sqrt(100 ** 2 + 100 ** 2)
                        w.rect.x = distance * math.sin(w.getShotAngle()) + w.getXDiff()
                        w.rect.y = distance * math.cos(w.getShotAngle()) + w.getYDiff()"""
                        #circular motion
                        if spawncounter < (w.getSpawntime() + 2 * fps):
                            bulletX = w.getTrueX() - w.getXDiff()
                            bulletY = w.getTrueY() - w.getYDiff()
                            vecX = -0.05 * bulletY #x velocity
                            vecY = 0.05 * bulletX #y velocity
                            bulletX += vecX
                            bulletY += vecY
                            scale = 100 / math.sqrt((bulletX) ** 2 + (bulletY ** 2))
                            bulletX *= scale
                            bulletY *= scale
                            w.setTrueX(bulletX + w.getXDiff())
                            w.setTrueY(bulletY + w.getYDiff())
                            w.rect.x = w.getTrueX()
                            w.rect.y = w.getTrueY()

                        else:
                            #print("a")
                            #w.kill()
                            #w.rect.x += vecX / 100
                            #w.rect.y += vecY / 100
                            w.setTrueX(float(w.getTrueX() + w.getXVel()))
                            w.setTrueY(float(w.getTrueY() + w.getYVel()))
                            w.rect.x = w.getTrueX()
                            w.rect.y = w.getTrueY()

                if attack == 14 and w.getYVelSet():
                    #rotates while slowly moving inward
                    #inward rotation is done by lowering radius, rotation done thru physics
                    spdCoefficient = 0.015 #determines rotation speed
                    if w.getShotAngle() >= 20:
                        w.setShotAngle(w.getShotAngle() - 0.4)
                    bulletX = w.getTrueX() - w.getXDiff()
                    bulletY = w.getTrueY() - w.getYDiff()
                    vecX = (-1 * spdCoefficient * bulletY)  # x velocity
                    vecY = (spdCoefficient * bulletX)   # y velocity
                    bulletX += vecX
                    bulletY += vecY
                    scale = w.getShotAngle() / math.sqrt((bulletX) ** 2 + (bulletY ** 2))
                    bulletX *= scale
                    bulletY *= scale
                    w.setTrueX(bulletX + w.getXDiff())
                    w.setTrueY(bulletY + w.getYDiff())
                    w.rect.x = w.getTrueX()
                    w.rect.y = w.getTrueY()
                if not (attack == 12 and w.getYVelSet()):
                    w.setTrueX(w.getTrueX() + w.getXVel())
                    w.setTrueY(w.getTrueY() + w.getYVel())
                    w.rect.x = w.getTrueX()
                    w.rect.y = w.getTrueY()

                if w.rect.y > int(ylimit * 1.5):
                    w.kill()
                if w.rect.x < (-0.5 * xlimit):
                    w.kill()
                if w.rect.x > int(xlimit * 1.5):
                    w.kill()
                if w.rect.y < (-0.5 * ylimit):
                    w.kill()


            # first parameter takes a single sprite
            # second parameter takes sprite groups
            # third parameter is a do kill command if true
            # bullet is killed when colliding with player

            """hit = pygame.sprite.spritecollide(player, wall_group, True)

            if hit and iframes == 0:
                # if collision is detected call a function in your case destroy bullet
                #player.image.fill((255, 255, 255))
                for w in wall_group:
                    w.kill()
                iframes = 100
                textcolor = (0, 255, 255)
                font = pygame.font.SysFont("Arial", 72)
                bombtext = font.render("hit", True, (textcolor)) #will only show for 1 tick, fix pending lol
                screen.blit(bombtext, (300, 300))
                if lives == 3: #to deal w/ the issue that getting hit takes off multiple lives rapidly
                    lives = 2
                elif lives == 2:
                    lives = 1
                elif lives == 1:
                    lives = 0
                #player.loselife(iframes)"""
            #collision moved above higher
            screen.blit(playerimage, (player.rect.x - 10, player.rect.y - 20))
            player_group.draw(screen)
            wall_group.draw(screen)


            textcolor = (0, 255, 255)
            font = pygame.font.SysFont("Arial", 24)
            bombstring = "Bombs:" + str(bombs)
            livesstring = "Lives:" + str(lives)
            iframesstring = "Iframes:" + str(iframes)
            bombtext = font.render(bombstring, True, (textcolor))  # bomb text
            livestext = font.render(livesstring, True, (textcolor))
            iframestext = font.render(iframesstring, True, (textcolor))
            # comment out each individual print here, half of these are for testing
            screen.blit(bombtext, (xlimit-120, ylimit-200))
            screen.blit(livestext, (xlimit-120, 50))
            #screen.blit(lifeimage, (0, 0)) way too big
            # screen.blit(iframestext, (50, 50))

            pygame.display.update()
            clock.tick(fps)
        if status == 2:
            screen.fill((0, 0, 0))
            # print("dead")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
            key = pygame.key.get_pressed()
            if key[pygame.K_z]:  # goes back to game
                lives = 3
                status = 1
                attackduration = 0
                bombs = 3
                attack = 0
            if key[pygame.K_x]:
                status = 0
            newbg = [0, 0, 0]
            newfont = pygame.font.SysFont("Arial", 24)
            winstring = ["Abject Failure", "Wait... really?", "This sucks..."]

            textcolor = [255, 255, 255]
            introtext = newfont.render(winstring[deadrandom], True, (textcolor))
            begintext = newfont.render("Z to try again?", True, (textcolor))
            returntext = newfont.render("X to return to start", True, (textcolor))
            screen.blit(introtext, (200, 100))
            screen.blit(begintext, (180, 300))
            screen.blit(returntext, (180, 450))
            pygame.display.update()
            clock.tick(fps)
        if status == 3:
            screen.fill((0, 0, 0))
            # print("dead")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
            key = pygame.key.get_pressed()
            if key[pygame.K_z]:  # goes back to game
                lives = 3
                bombs = 3
                status = 1
                attack = 0
                attackduration = 0
                iframes = 100
            if key[pygame.K_x]:
                status = 0
            newbg = [0, 0, 0]
            newfont = pygame.font.SysFont("Arial", 24)
            winstring = "You really won?"

            textcolor = [255, 255, 255]
            introtext = newfont.render(winstring, True, (textcolor))
            begintext = newfont.render("Z to return to the gauntlet", True, (textcolor))
            returntext = newfont.render("X to return to start", True, (textcolor))
            screen.blit(introtext, (200, 100))
            screen.blit(begintext, (180, 300))
            screen.blit(returntext, (180, 450))
            pygame.display.update()
            clock.tick(fps)
        # lives = 3
        # notlost = True
    # print("dead")
    # pygame.quit()


if __name__ == '__main__':
    main()
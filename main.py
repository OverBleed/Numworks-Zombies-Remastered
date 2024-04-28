import pygame
import sys
from random import randint

pygame.init()
pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

pygame.display.set_caption("Numworks Zombies Remastered")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font("data/font.otf", 30)

clock = pygame.time.Clock()
pygame.mixer.music.set_volume(0.5)

pygame.mixer.music.load("data/metal_song.wav")

sfx = {
    "shotgun_shoot": pygame.mixer.Sound("data/sfx/shotgun/shotgun_shoot.wav"),
    "shotgun_reload": pygame.mixer.Sound("data/sfx/shotgun/shotgun_reload.wav"),
    "shotgun_rakk": pygame.mixer.Sound("data/sfx/shotgun/shotgun_rakk.wav")
}

sprites = {
    "player": "data/sprites/player.png",
    "zombie": "data/sprites/zombie.png",
    "bullet": "data/sprites/bullet.png",
    "shotgun": "data/sprites/shotgun.png"
}

bgColor = [120, 200, 250]
totalBgColor = bgColor[0] + bgColor[1] + bgColor[2]

keydown = {
    "UP": False,
    "RIGHT": False,
    "DOWN": False,
    "LEFT": False,
    "ENTER": False
}

class Entity:
    def __init__(self, size, spriteDirectory=None, pos=[150, 150], color=(0, 0, 0)):
        self.size = size # must be a list [x, y]
        self.spriteDirectory = spriteDirectory
        self.pos = pos
        self.color = color # only use when no sprites
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0]*5, self.size[1]*5)

    def display(self):
        if self.spriteDirectory != None:
            e_img = pygame.image.load(self.spriteDirectory)
            e_img = pygame.transform.scale(e_img, (self.size[0]*5, self.size[1]*5))
            e_img.set_colorkey((255, 255, 255))
            screen.blit(e_img, (self.pos[0], self.pos[1]))
        else:
            e_img = pygame.draw.rect(screen, self.color, self.rect)

    def updateVelocity(self, velocity=[0, 0]):
        self.pos[0] += velocity[0]
        self.pos[1] += velocity[1]
    
    def updateRect(self):
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0]*5, self.size[1]*5)

class Gun:
    def __init__(self, ammoCapacity, baseDamage, waitTimeMinutes, reloadTimeMinutes, sprite, shoot, reload, rakk):
        self.ammoCapacity = ammoCapacity
        self.baseDamage = baseDamage
        self.ammo = ammoCapacity # current ammo in magazine. Max by default

        self.waitTimeFrames = waitTimeMinutes * 60 # time to wait between every shot
        self.wait = 0 # current time to wait before firing

        self.reloadTimeSeconds = reloadTimeMinutes * 60 # time to reload
        self.waitReload = self.reloadTimeSeconds # time left while reloading

        self.sprite = sprite
        self.img = pygame.image.load(self.sprite)
        self.img.set_colorkey((255, 255, 255))
        self.rect = self.img.get_rect()

        self.shoot_sfx = shoot
        self.reload_sfx = reload
        self.rakk_sfx = rakk

        self.canShoot = True
        self.isReloading = False

    def shoot(self, bulletIndex):
        if self.canShoot == True and keydown["ENTER"] == True:
            self.shoot_sfx.play()
            self.ammo -= 1 # removes 1 bullet from magazine

            # process of shooting the bullet
            bullets.append(Entity((2, 2), "data/sprites/bullet.png", [self.rect.centerx, self.rect.centery], (255, 0, 0)))
            bulletDirection.append(playerDirection)
            bullets[bulletIndex].rect.center = player.rect.center

            self.wait = self.waitTimeFrames
            self.canShoot = False

            self.rakk_sfx.play()

    def canShootFunc(self):
        self.wait -= 1
        if self.isReloading: self.waitReload -= 1

        if self.wait <= 0 and self.ammo > 0: 
            self.canShoot = True
        
        if self.waitReload <= 0:
            self.rakk_sfx.play()
            self.ammo = self.ammoCapacity
            self.waitReload = self.reloadTimeSeconds
            self.isReloading = False

    def reload(self):
        if self.isReloading == False:
            self.reload_sfx.play()
            self.isReloading = True

    def display(self):
        self.img = pygame.image.load(self.sprite)
        self.img.set_colorkey((255, 255, 255))
        self.rect = self.img.get_rect()
        self.rect.size = (self.rect.size[0]*2.5, self.rect.size[1]*2.5)

        if playerDirection == "u":
            self.img = pygame.transform.rotate(self.img, 90)
            self.rect.size = (self.rect.size[1], self.rect.size[0])
            self.rect.midbottom = player.rect.midtop

        elif playerDirection == "r":
            self.rect.midleft = player.rect.midright

        elif playerDirection == "d":
            self.img = pygame.transform.rotate(self.img, -90)
            self.rect.size = (self.rect.size[1], self.rect.size[0])
            self.rect.midtop = player.rect.midbottom

        elif playerDirection == "l":
            self.img = pygame.transform.flip(self.img, True, False)
            self.rect.midright = player.rect.midleft

        self.img = pygame.transform.scale(self.img, self.rect.size)
        screen.blit(self.img, self.rect)

        

weapons = {
    "shotgun": Gun(7, 5, 1, 3, sprites["shotgun"], sfx["shotgun_shoot"], sfx["shotgun_reload"], sfx["shotgun_rakk"])
}

player = Entity((6, 9), sprites["player"], [150, 150])
playerDirection = "r" #u, d, r, l for respectively up, down, right, left
gunEquipped = weapons["shotgun"]
score = 0
alive = True
PLAYER_MAX_SPEED = 7

bullets = []
bulletNumber = 0
bulletDirection = []
bulletDamage = []
BULLET_SPEED = 9

enemies = []
enemiesHealth = []
ZOMBIE_SPEED = 0.75
enemiesSpawnAreas = [[[0, SCREEN_WIDTH], [-50, -50]], [[SCREEN_WIDTH+50, SCREEN_WIDTH+50], [0, SCREEN_HEIGHT]], [[0, SCREEN_WIDTH], [SCREEN_HEIGHT+50, SCREEN_HEIGHT+50]], [[-50, -50], [0, SCREEN_HEIGHT]]] # top, right, bottom, left

def initEnemies():
    for i in range(24):
        enemies.append(Entity((6, 9), sprites["zombie"], [-50, -50]))
        enemiesHealth.append(10)
        enemySpawn(i)

def displayScore():
    scoreSurf = font.render("Score: " + str(score), False, (0, 0, 0))
    screen.blit(scoreSurf, (0, 0))

def displayAmmo():
    ammoLeftSurf = font.render(str(gunEquipped.ammo) + "/" + str(gunEquipped.ammoCapacity), False, (0, 0, 0))
    screen.blit(ammoLeftSurf, (0, 35))

def playerMovement():
    global playerVelocity, playerDirection
    global bulletNumber

    if keydown["UP"]:
        player.updateVelocity([0, -PLAYER_MAX_SPEED])
        playerDirection = "u"
    if keydown["RIGHT"]:
        player.updateVelocity([PLAYER_MAX_SPEED, 0])
        playerDirection = "r"
    if keydown["DOWN"]:
        player.updateVelocity([0, PLAYER_MAX_SPEED])
        playerDirection = "d"
    if keydown["LEFT"]:
        player.updateVelocity([-PLAYER_MAX_SPEED, 0])
        playerDirection = "l"

def bulletMovement(index):
    global bulletNumber

    if bulletDirection[index] == "u": bullets[index].pos[1] -= BULLET_SPEED
    if bulletDirection[index] == "r": bullets[index].pos[0] += BULLET_SPEED
    if bulletDirection[index] == "d": bullets[index].pos[1] += BULLET_SPEED 
    if bulletDirection[index] == "l": bullets[index].pos[0] -= BULLET_SPEED

    # despawns bullets when they go outside of the screen. need to make it work
    # if bullets[index].pos[0] > SCREEN_WIDTH + 20 or bullets[index].pos[0] < 0 or bullets[index].pos[1] > SCREEN_HEIGHT + 20 or bullets[index].pos[1] < 0:
    
def enemySpawn(index):
    global enemiesHealth

    area = randint(0, 3)
    randomSpawnX = randint(enemiesSpawnAreas[area][0][0], enemiesSpawnAreas[area][0][1])
    randomSpawnY = randint(enemiesSpawnAreas[area][1][0], enemiesSpawnAreas[area][1][1])
    enemiesHealth[index] = 1 + score/100

    enemies[index].pos[0] = randomSpawnX
    enemies[index].pos[1] = randomSpawnY

def enemyMovement(index):
    if enemies[index].rect.left <= player.rect.left: enemies[index].updateVelocity([ZOMBIE_SPEED, 0])
    else: enemies[index].updateVelocity([-ZOMBIE_SPEED, 0])
    if enemies[index].rect.top < player.rect.top: enemies[index].updateVelocity([0, ZOMBIE_SPEED])
    else: enemies[index].updateVelocity([0, -ZOMBIE_SPEED])

def changeBackgroundColor():
    bgColor[0] += randint(-2, 2)
    if bgColor[0] > 254: bgColor[0] = 254
    elif bgColor[0] < 100: bgColor[0] = 100

    bgColor[1] += randint(-2, 2)
    if bgColor[1] > 254: bgColor[1] = 254
    elif bgColor[1] < 100: bgColor[1] = 100

    bgColor[2] += randint(-2, 2)
    if bgColor[2] > 254: bgColor[2] = 254
    elif bgColor[2] < 100: bgColor[2] = 100

initEnemies()

pygame.mixer.music.play(-1)

def run():
    global alive, bulletNumber, score

    while alive:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: keydown["UP"] = True
                    if event.key == pygame.K_RIGHT: keydown["RIGHT"] = True
                    if event.key == pygame.K_DOWN: keydown["DOWN"] = True
                    if event.key == pygame.K_LEFT: keydown["LEFT"] = True
                    if event.key == pygame.K_KP_ENTER:
                        keydown["ENTER"] = True
                        if gunEquipped.ammo > 0: gunEquipped.shoot(bulletNumber - 1)
                        else: gunEquipped.reload()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP: keydown["UP"] = False
                    if event.key == pygame.K_RIGHT: keydown["RIGHT"] = False
                    if event.key == pygame.K_DOWN: keydown["DOWN"] = False
                    if event.key == pygame.K_LEFT: keydown["LEFT"] = False
                    if event.key == pygame.K_KP_ENTER: keydown["ENTER"] = False
                

            screen.fill(bgColor)
            changeBackgroundColor()

            playerMovement()
            
            player.display()
            player.updateRect()
            displayScore()
            displayAmmo()

            gunEquipped.canShootFunc()
            gunEquipped.display()


            # detects collisions and shows bullet. Doesn't need to be in a function
            for i in range(len(bullets)):
                bullets[i].updateRect()
                bullets[i].display()
                bulletMovement(i)
                
                for j in range(len(enemies)):
                    if bullets[i].rect.colliderect(enemies[j]):
                        score += 1
                        enemiesHealth[j] -= gunEquipped.baseDamage
                        
                        if enemiesHealth[j] <= 0:
                            score += 100
                            enemySpawn(j)

            for i in range(len(enemies)):
                enemies[i].updateRect()
                enemyMovement(i)
                enemies[i].display()

                if enemies[i].rect.colliderect(player):
                    alive = False
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("data/sad_music.wav")
                    pygame.mixer.music.play(-1, 0, 1500)

            pygame.display.update()
            clock.tick(60)

def death():
    global score, alive, bulletNumber, bulletDirection
    global bullets, enemies, enemiesHealth

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP_ENTER:
                score = 0
                alive = True
                bulletNumber = 0
                bullets = []
                bulletDirection = []
                enemies = []
                enemiesHealth = []
                initEnemies()

                player.pos = [150, 150]
                gunEquipped.ammo = gunEquipped.ammoCapacity
                gunEquipped.isReloading = False

                keydown["UP"] = False
                keydown["RIGHT"] = False
                keydown["DOWN"] = False
                keydown["LEFT"] = False
                keydown["ENTER"] = False

                pygame.mixer.stop()
                pygame.mixer.music.load("data/metal_song.wav")
                pygame.mixer.music.play(-1, 0, 1500)

                run()

    screen.fill((255, 0, 0))
    screen.blit(font.render("You died", False, (0, 0, 0)), (SCREEN_WIDTH/2 - 120, SCREEN_HEIGHT/2))
    screen.blit(font.render("Press ENTER to try again", False, (0, 0, 0)), (SCREEN_WIDTH/2 - 360, SCREEN_HEIGHT/2 + 35))
    displayScore()

    pygame.display.update()
    clock.tick(20)

while True:
    run()

    death()
import pygame
import sys

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 440

pygame.display.set_caption("Numworks Zombies Remastered")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

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

    def display(self):
        if self.spriteDirectory != None:
            e_img = pygame.image.load(self.spriteDirectory)
            e_img = pygame.transform.scale(e_img, (self.size[0]*5, self.size[1]*5))
            e_img.set_colorkey((255, 255, 255))
            screen.blit(e_img, (self.pos[0], self.pos[1]))
        else:
            e_img = pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0], self.pos[1], self.size[0]*5, self.size[1]*5))


    def updateVelocity(self, velocity=[0, 0]):
        self.pos[0] += velocity[0]
        self.pos[1] += velocity[1]


player = Entity((6, 9), "data/sprites/player_right.png", [150, 150])
playerDirection = "r" #u, d, r, l for respectively up, down, right, left
PLAYER_MAX_SPEED = 7

bullets = []
bulletNumber = 0

enemies = []
enemies.append(Entity((6, 9), "data/sprites/zombie.png", [50, 50]))


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
    if keydown["ENTER"]:
        bulletNumber += 1
        shootBullet(bulletNumber - 1)

def shootBullet(bulletIndex):
    bullets.append(Entity((2, 2), None, [player.pos[0], player.pos[1]], (255, 0, 0)))
    for i in range(bulletNumber-1):
        bullets[bulletNumber-1].display()

while True:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: keydown["UP"] = True
            if event.key == pygame.K_RIGHT: keydown["RIGHT"] = True
            if event.key == pygame.K_DOWN: keydown["DOWN"] = True
            if event.key == pygame.K_LEFT: keydown["LEFT"] = True
            if event.key == pygame.K_KP_ENTER: keydown["ENTER"] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP: keydown["UP"] = False
            if event.key == pygame.K_RIGHT: keydown["RIGHT"] = False
            if event.key == pygame.K_DOWN: keydown["DOWN"] = False
            if event.key == pygame.K_LEFT: keydown["LEFT"] = False
            if event.key == pygame.K_KP_ENTER: keydown["ENTER"] = False
            

    playerMovement()

    player.display()

    pygame.display.update()
    clock.tick(60)
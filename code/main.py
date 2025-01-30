from random import randint
import pygame
from os.path import join
from pygame.math import Vector2

#initialize pygame
pygame.init()

#variables
WINDOW_WIDTH, WINDOW_HEIGTH = 1180, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGTH))
pygame.display.set_caption('Space Shooter')
clock = pygame.time.Clock()
running = True
delta_time = 0
meteor_spawn_time = 300

#imports
star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()
player_surface = pygame.image.load(join('images', 'player.png')).convert_alpha()
meteor_surface = pygame.image.load(join('images', 'meteor.png')).convert_alpha()

#classes
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2,WINDOW_HEIGTH/2))
        self.speed = 300
        self.player_direction = Vector2(0,0)
        self.laser_surface = pygame.image.load(join('images', 'laser.png'))
        #cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 100

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time > self.laser_shoot_time + self.cooldown_duration:
                self.can_shoot = True
   
    def update(self,dt):
        global running
        self.laser_timer()

        #check for collision
        if pygame.sprite.spritecollide(self, meteor_sprites, False):
            running = False

        #player input constant press
        pressed_keys = pygame.key.get_pressed()
        self.player_direction.x = int(pressed_keys[pygame.K_d]) - int(pressed_keys[pygame.K_a])
        self.player_direction.y = int(pressed_keys[pygame.K_s]) - int(pressed_keys[pygame.K_w])
        self.player_direction = self.player_direction.normalize() if self.player_direction else self.player_direction
        if self.rect.bottom + self.player_direction.y < WINDOW_HEIGTH and self.rect.top + self.player_direction.y > 0:
            self.rect.center += self.player_direction * self.speed * dt
       
        #player input once press 
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(self.laser_surface, self.rect.midtop, [all_sprites, laser_sprites])
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

class StarSprite(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH), randint(0,WINDOW_HEIGTH)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, images, pos, groups):
        super().__init__(groups)
        self.image = images
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, delta):
        if pygame.sprite.spritecollide(self, meteor_sprites, True):
            self.kill()

        self.rect.centery -= 400 * delta
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH), -50))
        self.velocity = Vector2(randint(-50,50),randint(100,400))
        self.alive_time = 0
        self.create_time = pygame.time.get_ticks()


    def update(self, delta_time):
        # collision = pygame.sprite.spritecollide(self, meteor_sprites, False)
        # for meteor in collision:
        #     if meteor != self:
        #         meteor.velocity *= -1
        #         self.velocity *= -1

        self.rect.center += self.velocity * delta_time
        if pygame.time.get_ticks() > self.alive_time + self.create_time and (self.rect.x > WINDOW_WIDTH + 50 or self.rect.x < -50 or self.rect.y > WINDOW_HEIGTH + 50):
            self.kill()

class GUI():
    def __init__(self):
        self.font = pygame.font.Font('images\Oxanium-Bold.ttf', 50)
        self.elapsed_time = 0
        self.total_delta = 0

    def update(self, delta_time):
        self.total_delta += delta_time 
        if self.total_delta > self.elapsed_time:
            self.elapsed_time += 1
           
        self.score_text_surface = self.font.render(str(self.elapsed_time), False, 'white', None, )
        self.score_text_rect = self.score_text_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGTH-50))
        self.border_rect = pygame.FRect(self.score_text_rect.x, self.score_text_rect.y, self.score_text_rect.w, self.score_text_rect.h)


        pygame.draw.rect(display_surface, 'white', self.border_rect, 2, -2)
        print(self.score_text_rect) 
 
    def draw(self):
        display_surface.blit(self.score_text_surface, self.score_text_rect)

#functions
def update_sprites(delta_time):
    all_sprites.update(delta_time)
    meteor_sprites.update(delta_time)

def draw_sprites():
    all_sprites.draw(display_surface)
    meteor_sprites.draw(display_surface)

#initiaize sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(0):
    StarSprite(all_sprites, star_surface)
player_class = PlayerSprite(player_surface, all_sprites)
gui_class = GUI()

#custom events - meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, meteor_spawn_time)

#event loop
while running:
    #background tasks
    delta_time = clock.tick() / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 

        if event.type == meteor_event:
            Meteor(meteor_sprites, meteor_surface)

    display_surface.fill('grey12')
    update_sprites(delta_time)
    draw_sprites()
    gui_class.update(delta_time)
    gui_class.draw()

    pygame.display.update()


#if the loop breaks quit the game
pygame.quit()
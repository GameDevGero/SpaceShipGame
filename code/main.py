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
meteor_spawn_time = 200

#imports
star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()
player_surface = pygame.image.load(join('images', 'player.png')).convert_alpha()
meteor_surface = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
explosion_sequence = [pygame.image.load(join('images','explosion',f'{str(i)}.png')).convert_alpha() for i in range(20)]

game_music = pygame.mixer.Sound(join('audio','music.wav'))
game_music.set_volume(0.5)
game_music.play()

laser_sound = pygame.mixer.Sound(join('audio','shoot.wav'))
laser_sound.set_volume(0.2)

explosion_sound = pygame.mixer.Sound(join('audio','explosion.wav'))
explosion_sound.set_volume(0.3)

#classes
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2,WINDOW_HEIGTH/2))
        self.speed = 300
        self.player_direction = Vector2(0,0)
        self.laser_surface = pygame.image.load(join('images', 'laser.png'))
        
        #stamina_meter
        self.stamina = 100

        #mask
        self.player_mask = pygame.mask.from_surface(self.image)

    def laser_timer(self,dt):
        if self.stamina < 100:
            self.stamina += 5 * dt
   
    def update(self,dt):
        global running
        self.laser_timer(dt)

        #check for collision
        if pygame.sprite.spritecollide(self, meteor_sprites, False, pygame.sprite.collide_mask):
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
        if recent_keys[pygame.K_SPACE] and self.stamina > 10:
            Laser(self.laser_surface, self.rect.midtop, [all_sprites, laser_sprites])
            self.stamina -= 5

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
        laser_sound.play()
        
    def update(self, delta):
        if pygame.sprite.spritecollide(self, meteor_sprites, True, pygame.sprite.collide_mask):
            Explosion(all_sprites,self.rect.centerx, self.rect.top)
            self.kill()

        self.rect.centery -= 400 * delta
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.original_surface = surf
        self.image = self.original_surface
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH), -50))
        self.velocity = Vector2(randint(-50,50),randint(100,400))
        self.alive_time = 0
        self.create_time = pygame.time.get_ticks()
        self.meteor_rotation = 0
        self.meteor_rotation_anmount = randint(-100, 100)


    def update(self, delta_time):
        # collision = pygame.sprite.spritecollide(self, meteor_sprites, False)
        # for meteor in collision:
        #     if meteor != self:
        #         meteor.velocity *= -1
        #         self.velocity *= -1


        self.meteor_rotation += self.meteor_rotation_anmount*delta_time
        self.image = pygame.transform.rotozoom(self.original_surface, self.meteor_rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

        self.rect.center += self.velocity * delta_time
        if pygame.time.get_ticks() > self.alive_time + self.create_time and (self.rect.x > WINDOW_WIDTH + 50 or self.rect.x < -50 or self.rect.y > WINDOW_HEIGTH + 50):
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self,group,pos_x,pos_y):
        super().__init__(group) 
        self.image = explosion_sequence[0]
        self.rect = self.image.get_frect(center = (pos_x, pos_y))
        self.sequence_counter = 0
        explosion_sound.play()

    def update(self, delta_time):
        self.image = explosion_sequence[self.sequence_counter]
        self.sequence_counter += 1
        if self.sequence_counter > 19:
            self.kill()
        
class GUI():
    def __init__(self):
        self.font = pygame.font.Font('images\Oxanium-Bold.ttf', 50)
        self.elapsed_time = 0
        self.total_delta = 0

    def update(self, delta_time, stamina): 
        self.total_delta += delta_time 
        if self.total_delta > self.elapsed_time:
            self.elapsed_time += 1
       
        #score
        self.score_text_surface = self.font.render(str(self.elapsed_time), False, 'white', None, )
        self.score_text_rect = self.score_text_surface.get_frect(center = (WINDOW_WIDTH/2, 75)) 
        self.border_rect = self.score_text_rect.inflate(40,10).move(0,-8)

        #stamina meter
        self.meter_border_rect = pygame.FRect(50,50,200,25)
        self.meter_rect = self.meter_border_rect.scale_by(stamina/100-0.05, 0.9).move(((100-stamina)*-1), 0)

    def draw(self):
        display_surface.blit(self.score_text_surface, self.score_text_rect)
        pygame.draw.rect(display_surface, 'white', self.border_rect, 8, 5)   
        pygame.draw.rect(display_surface, 'brown3', self.meter_rect, 12, 0)  
        pygame.draw.rect(display_surface,'gold', self.meter_border_rect, 7, 10)

#functions
def update_sprites(delta_time):
    all_sprites.update(delta_time)
    meteor_sprites.update(delta_time)

def draw_sprites():
    all_sprites.draw(display_surface)
    meteor_sprites.draw(display_surface)

def play_sound(sound):
    sound.play()

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
    gui_class.update(delta_time, player_class.stamina)
    gui_class.draw()
    update_sprites(delta_time)
    draw_sprites()

    pygame.display.update()


#if the loop breaks quit the game
pygame.quit()
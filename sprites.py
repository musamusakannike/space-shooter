
import pygame
import random
import math
from settings import *
from asset_manager import asset_manager

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # Choosing a blue ship
        self.original_image = asset_manager.get_image('ships_spaceships_001_png')
        if not self.original_image:
             # Fallback if image not found, create a placeholder
            self.original_image = pygame.Surface((50, 40))
            self.original_image.fill(BLUE)
        
        # Rotate if necessary (sprites might be facing up or down)
        # Assuming sprites face up by default. If they face right, rotate -90.
        # Let's assume standard up-facing for now.
        
        self.image = pygame.transform.scale(self.original_image, (50, 40)) # Scale down a bit
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        
        self.direction = pygame.math.Vector2()
        self.speed = PLAYER_SPEED
        self.last_shot_time = 0
        self.shoot_delay = 250 # ms

        self.health = 100
        self.max_health = 100
        self.score = 0

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        
        # Normalize to avoid faster diagonal movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Shooting
        if keys[pygame.K_SPACE]:
            self.shoot()

    def move(self):
        self.rect.center += self.direction * self.speed
        
        # Constrain to screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            # Create bullet
            # Use 'groups' passed from GameManager, but we need access to them.
            # Best way: pass groups to shoot method or have a callback?
            # Or assume GameManager sets a static reference or pass bullet_group in __init__
            # For simplicity, let's look for a 'bullet_groups' attribute or similar.
            # Actually, best practice: Player doesn't need to know about groups if we return bullets,
            # but standard pygame way is to add to groups.
            # Let's make Player accept bullet_group in __init__ or have a callback.
            pass # Handled by return or callback in update? 
            # Let's use a callback for flexibility
            if hasattr(self, 'create_bullet_callback'):
                self.create_bullet_callback(self.rect.centerx, self.rect.top)
                self.last_shot_time = current_time

    def update(self):
        self.input()
        self.move()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, groups, is_player=True):
        super().__init__(groups)
        self.is_player = is_player
        
        img_name = 'missiles_spacemissiles_001_png' if is_player else 'missiles_spacemissiles_004_png'
        self.original_image = asset_manager.get_image(img_name)
        if not self.original_image:
            self.original_image = pygame.Surface((10, 20))
            self.original_image.fill(YELLOW if is_player else RED)

        self.image = pygame.transform.scale(self.original_image, (10, 20))
        # Flip collision rect?
        if not is_player:
            self.image = pygame.transform.rotate(self.image, 180)

        self.rect = self.image.get_rect(center=pos)
        self.speed = BULLET_SPEED if is_player else -BULLET_SPEED # Wait, enemy bullets go DOWN (+y)
        self.direction = -1 if is_player else 1

    def update(self):
        self.rect.y += self.direction * self.speed
        
        # Remove if off screen
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, enemy_type='basic'):
        super().__init__(groups)
        self.enemy_type = enemy_type
        
        # Select image based on type
        if enemy_type == 'basic':
            img_name = 'ships_spaceships_004_png' # A reddish ship maybe
            self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
            self.health = 1
        elif enemy_type == 'tank':
            img_name = 'ships_spaceships_008_png' # A bigger ship
            self.speed = ENEMY_SPEED_MIN
            self.health = 3
        elif enemy_type == 'fast':
            img_name = 'ships_spaceships_006_png'
            self.speed = ENEMY_SPEED_MAX + 2
            self.health = 1
        else:
            img_name = 'ships_spaceships_004_png'
            self.speed = ENEMY_SPEED_MIN
            self.health = 1

        self.original_image = asset_manager.get_image(img_name)
        if not self.original_image:
            self.original_image = pygame.Surface((40, 40))
            self.original_image.fill(RED)
            
        self.image = pygame.transform.scale(self.original_image, (50, 50))
        self.image = pygame.transform.rotate(self.image, 180) # Face down
        
        # Random x position
        x_pos = random.randint(50, SCREEN_WIDTH - 50)
        self.rect = self.image.get_rect(midbottom=(x_pos, 0))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        # Random meteor
        meteor_idx = random.randint(1, 4)
        img_name = f'meteors_spacemeteors_00{meteor_idx}_png'
        self.original_image = asset_manager.get_image(img_name)
        
        if not self.original_image:
             self.original_image = pygame.Surface((40, 40))
             self.original_image.fill((100, 100, 100))

        scale = random.randint(30, 80)
        self.image = pygame.transform.scale(self.original_image, (scale, scale))
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH-50), -50))
        
        self.speed_y = random.uniform(METEOR_SPEED_MIN, METEOR_SPEED_MAX)
        self.speed_x = random.uniform(-1, 1)
        self.rot_speed = random.uniform(-2, 2)
        self.rotation = 0

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Simple rotation (might be expensive effectively, but okay for PC)
        # self.rotation += self.rot_speed
        # self.image = pygame.transform.rotate(self.original_image, self.rotation)
        # self.rect = self.image.get_rect(center=self.rect.center)
        # Rotation with pygame sprite rects is tricky (jitter), skipping for stable MVP first
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # Using effects
        self.frames = []
        # Let's verify what effects we have. Based on list, spaceEffects_001 to 018.
        # Maybe 008-012 look like explosions?
        # Let's load a sequence.
        # Assuming spaceEffects_008 to 012 might be explosion or similar.
        # Actually checking the list:
        # 51: Sprites/Effects/spaceEffects_008.png
        # ...
        # Use a generic expanding circle or one of the sprites if unsure.
        # I'll use spaceEffects_010.png as a simple poof for now, or just a few frames if I knew them.
        self.image = asset_manager.get_image('effects_spaceeffects_010_png')
        if not self.image:
             self.image = pygame.Surface((20, 20))
             self.image.fill(WHITE)
        
        self.rect = self.image.get_rect(center=pos)
        self.timer = pygame.time.get_ticks()
        self.duration = 200 # ms

    def update(self):
        if pygame.time.get_ticks() - self.timer > self.duration:
            self.kill()


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
        self.base_speed = PLAYER_SPEED
        self.last_shot_time = 0
        self.shoot_delay = 250 # ms
        self.base_shoot_delay = 250

        self.health = 100
        self.max_health = 100
        self.score = 0
        
        # Power-up states
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 5000
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 8000
        self.reverse_controls = False
        self.reverse_timer = 0
        self.reverse_duration = 5000
        
        # Bullets tracking for story mode
        self.bullets_fired = 0
        self.bullets_remaining = -1  # -1 means unlimited

    def input(self):
        keys = pygame.key.get_pressed()
        
        # Handle reverse controls debuff
        if self.reverse_controls:
            self.direction.x = int(keys[pygame.K_LEFT] or keys[pygame.K_a]) - int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
            self.direction.y = int(keys[pygame.K_UP] or keys[pygame.K_w]) - int(keys[pygame.K_DOWN] or keys[pygame.K_s])
        else:
            self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
            self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        
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
        
        # Check bullet limit for story mode
        if self.bullets_remaining == 0:
            return
            
        if current_time - self.last_shot_time > self.shoot_delay:
            if hasattr(self, 'create_bullet_callback'):
                self.create_bullet_callback(self.rect.centerx, self.rect.top)
                self.last_shot_time = current_time
                self.bullets_fired += 1
                
                if self.bullets_remaining > 0:
                    self.bullets_remaining -= 1
    
    def apply_powerup(self, power_type):
        """Apply power-up effect"""
        current_time = pygame.time.get_ticks()
        
        if power_type == 'health':
            self.health = min(self.health + 30, self.max_health)
        elif power_type == 'speed_boost':
            self.speed = self.base_speed * 1.5
        elif power_type == 'invincibility':
            self.invincible = True
            self.invincible_timer = current_time
        elif power_type == 'rapid_fire':
            self.shoot_delay = self.base_shoot_delay // 2
        elif power_type == 'shield':
            self.shield_active = True
            self.shield_timer = current_time
    
    def apply_powerdown(self, debuff_type):
        """Apply power-down effect"""
        current_time = pygame.time.get_ticks()
        
        if debuff_type == 'slow':
            self.speed = self.base_speed * 0.5
        elif debuff_type == 'weak_bullets':
            self.shoot_delay = self.base_shoot_delay * 2
        elif debuff_type == 'reverse_controls':
            self.reverse_controls = True
            self.reverse_timer = current_time
    
    def update_powerup_timers(self):
        """Update power-up timers and reset effects"""
        current_time = pygame.time.get_ticks()
        
        # Invincibility
        if self.invincible and current_time - self.invincible_timer > self.invincible_duration:
            self.invincible = False
        
        # Shield
        if self.shield_active and current_time - self.shield_timer > self.shield_duration:
            self.shield_active = False
        
        # Reverse controls
        if self.reverse_controls and current_time - self.reverse_timer > self.reverse_duration:
            self.reverse_controls = False

    def update(self):
        self.input()
        self.move()
        self.update_powerup_timers()

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

class EnemyShooter(pygame.sprite.Sprite):
    def __init__(self, groups, enemy_type='shooter'):
        super().__init__(groups)
        self.enemy_type = enemy_type
        
        img_name = 'ships_spaceships_007_png'
        self.speed = random.uniform(1.5, 3.0)
        self.health = 2
        
        self.original_image = asset_manager.get_image(img_name)
        if not self.original_image:
            self.original_image = pygame.Surface((40, 40))
            self.original_image.fill(RED)
            
        self.image = pygame.transform.scale(self.original_image, (50, 50))
        self.image = pygame.transform.rotate(self.image, 180)
        
        x_pos = random.randint(50, SCREEN_WIDTH - 50)
        self.rect = self.image.get_rect(midbottom=(x_pos, 0))
        
        self.last_shot_time = 0
        self.shoot_delay = random.randint(1500, 3000)
        self.create_bullet_callback = None
        self.move_pattern = random.choice(['straight', 'zigzag'])
        self.direction = random.choice([-1, 1])
        
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            if self.create_bullet_callback:
                self.create_bullet_callback(self.rect.centerx, self.rect.bottom)
                self.last_shot_time = current_time
                self.shoot_delay = random.randint(1500, 3000)
    
    def update(self):
        self.rect.y += self.speed
        
        if self.move_pattern == 'zigzag':
            self.rect.x += self.direction * 2
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.direction *= -1
        
        self.shoot()
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class EnemyRocket(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        
        img_name = 'missiles_spacemissiles_016_png'
        self.original_image = asset_manager.get_image(img_name)
        if not self.original_image:
            self.original_image = pygame.Surface((30, 60))
            self.original_image.fill((200, 50, 50))
            
        self.image = pygame.transform.scale(self.original_image, (40, 70))
        self.image = pygame.transform.rotate(self.image, 180)
        
        x_pos = random.randint(50, SCREEN_WIDTH - 50)
        self.rect = self.image.get_rect(midbottom=(x_pos, 0))
        
        self.speed = random.uniform(3, 5)
        self.health = 3
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, groups, power_type='health'):
        super().__init__(groups)
        self.power_type = power_type
        
        # Map power types to sprites and colors
        power_configs = {
            'health': ('parts_spaceparts_066_png', (50, 255, 100)),
            'speed_boost': ('parts_spaceparts_072_png', (100, 200, 255)),
            'invincibility': ('parts_spaceparts_057_png', (255, 215, 0)),
            'rapid_fire': ('parts_spaceparts_055_png', (255, 150, 50)),
            'shield': ('parts_spaceparts_052_png', (150, 150, 255)),
        }
        
        img_name, self.color = power_configs.get(power_type, ('parts_spaceparts_066_png', (255, 255, 255)))
        self.original_image = asset_manager.get_image(img_name)
        
        if not self.original_image:
            self.original_image = pygame.Surface((30, 30))
            self.original_image.fill(self.color)
        
        self.image = pygame.transform.scale(self.original_image, (35, 35))
        self.rect = self.image.get_rect(center=pos)
        
        self.speed = 2
        self.float_offset = 0
        self.float_speed = 3
        
    def update(self):
        self.rect.y += self.speed
        self.float_offset += self.float_speed * 0.1
        self.rect.x += math.sin(self.float_offset) * 2
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerDown(pygame.sprite.Sprite):
    def __init__(self, pos, groups, debuff_type='slow'):
        super().__init__(groups)
        self.debuff_type = debuff_type
        
        debuff_configs = {
            'slow': ('parts_spaceparts_088_png', (150, 50, 50)),
            'weak_bullets': ('parts_spaceparts_086_png', (200, 100, 50)),
            'reverse_controls': ('parts_spaceparts_091_png', (180, 50, 180)),
        }
        
        img_name, self.color = debuff_configs.get(debuff_type, ('parts_spaceparts_088_png', (150, 50, 50)))
        self.original_image = asset_manager.get_image(img_name)
        
        if not self.original_image:
            self.original_image = pygame.Surface((30, 30))
            self.original_image.fill(self.color)
        
        self.image = pygame.transform.scale(self.original_image, (35, 35))
        self.rect = self.image.get_rect(center=pos)
        
        self.speed = 2.5
        self.pulse = 0
        
    def update(self):
        self.rect.y += self.speed
        self.pulse += 0.2
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = asset_manager.get_image('effects_spaceeffects_010_png')
        if not self.image:
             self.image = pygame.Surface((20, 20))
             self.image.fill(WHITE)
        
        self.rect = self.image.get_rect(center=pos)
        self.timer = pygame.time.get_ticks()
        self.duration = 200

    def update(self):
        if pygame.time.get_ticks() - self.timer > self.duration:
            self.kill()

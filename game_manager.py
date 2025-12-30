
import pygame
import sys
from settings import *
from sprites import Player, Bullet, Enemy, Meteor, Explosion
from ui import UI

class GameManager:
    def __init__(self, surface):
        self.display_surface = surface
        self.ui = UI(self.display_surface)
        
        # Sprite Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group() # Meteors, Enemies
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        # Game State
        self.game_active = False
        self.game_mode = 'endless' # 'endless' or 'levels'
        self.current_level = 1
        self.level_enemy_count = 0
        self.enemies_spawned = 0
        
        # Timers
        self.enemy_spawn_timer = pygame.event.custom_type()
        self.meteor_spawn_timer = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_spawn_timer, 1500)
        pygame.time.set_timer(self.meteor_spawn_timer, 2000)

        # Player
        self.player = None

    def start_game(self, mode='endless'):
        self.game_active = True
        self.game_mode = mode
        self.current_level = 1
        
        # Reset groups
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.all_sprites.empty()
        
        # Create Player
        self.player = Player([self.visible_sprites, self.all_sprites])
        self.player.create_bullet_callback = self.create_player_bullet
        
        if mode == 'levels':
            self.start_level(1)

    def start_level(self, level):
        self.current_level = level
        self.enemies_for_level = 5 + (level * 2) # Example progression
        self.enemies_spawned = 0
        print(f"Starting Level {level}")

    def create_player_bullet(self, x, y):
        Bullet((x, y), [self.visible_sprites, self.player_bullets, self.all_sprites], is_player=True)

    def create_enemy(self):
        # Spawning logic
        if self.game_mode == 'levels':
            if self.enemies_spawned < self.enemies_for_level:
                Enemy([self.visible_sprites, self.obstacle_sprites, self.all_sprites])
                self.enemies_spawned += 1
        else: # Endless
             Enemy([self.visible_sprites, self.obstacle_sprites, self.all_sprites])

    def create_meteor(self):
        Meteor([self.visible_sprites, self.obstacle_sprites, self.all_sprites])

    def check_collisions(self):
        if not self.player: return

        # Player Bullets vs Enemies/Meteors
        hits = pygame.sprite.groupcollide(self.obstacle_sprites, self.player_bullets, True, True)
        if hits:
            for hit_sprite in hits:
                Explosion(hit_sprite.rect.center, [self.visible_sprites, self.all_sprites])
                self.player.score += 100
                if self.game_mode == 'levels':
                    # Check if level complete
                    if self.enemies_spawned >= self.enemies_for_level and len(self.obstacle_sprites) == 0:
                        self.start_level(self.current_level + 1)

        # Player vs Obstacles
        collide_sprites = pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True)
        if collide_sprites:
            for sprite in collide_sprites:
                self.player.health -= 20
                Explosion(sprite.rect.center, [self.visible_sprites, self.all_sprites])
                if self.player.health <= 0:
                    self.game_over()

    def game_over(self):
        self.game_active = False
        # Maybe show explosion on player
        Explosion(self.player.rect.center, [self.visible_sprites, self.all_sprites])

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_active:
                if event.key == pygame.K_ESCAPE:
                    self.game_active = False # Pause/Back to menu
            else:
                if event.key == pygame.K_RETURN:
                    self.start_game(mode='endless')
                elif event.key == pygame.K_l:
                    self.start_game(mode='levels')
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                     # Restart if game over (game_active is False but player exists with <= 0 health)
                     if self.player and self.player.health <= 0:
                         self.start_game(self.game_mode)

        if self.game_active:
            if event.type == self.enemy_spawn_timer:
                self.create_enemy()
            if event.type == self.meteor_spawn_timer:
                self.create_meteor()

    def update(self):
        if self.game_active:
            self.all_sprites.update()
            self.check_collisions()
        else:
            # Check menu inputs are handled in events
            pass

    def draw(self):
        if self.game_active:
            self.visible_sprites.draw(self.display_surface)
            self.ui.display_hud(self.player)
        else:
            if hasattr(self, 'player') and self.player and self.player.health <= 0:
               self.ui.show_game_over(self.player.score)
            else:
               self.ui.show_menu()

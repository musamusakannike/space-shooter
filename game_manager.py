
import pygame
import sys
from settings import *
from sprites import Player, Bullet, Enemy, Meteor, Explosion
from ui import UI
from effects import ParticleSystem

class GameManager:
    def __init__(self, surface):
        self.display_surface = surface
        self.ui = UI(self.display_surface)
        
        # Setup UI callbacks
        self.ui.create_menu_buttons({
            'endless': lambda: self.start_game('endless'),
            'levels': lambda: self.start_game('levels'),
            'quit': self.quit_game
        })
        
        self.ui.create_game_over_buttons({
            'restart': lambda: self.start_game(self.game_mode),
            'menu': self.return_to_menu
        })
        
        # Sprite Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group() # Meteors, Enemies
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        # Game State
        self.game_active = False
        self.game_state = 'menu'  # 'menu', 'playing', 'game_over'
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

        # Audio
        try:
            self.collision_sound = pygame.mixer.Sound(COLLISION_SOUND_PATH)
        except Exception as e:
            print(f"Failed to load collision sound: {e}")
            self.collision_sound = None

    def start_game(self, mode='endless'):
        self.game_active = True
        self.game_state = 'playing'
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
                if self.collision_sound: self.collision_sound.play()
                Explosion(hit_sprite.rect.center, [self.visible_sprites, self.all_sprites])
                
                # Add score with popup
                points = 100
                self.player.score += points
                self.ui.add_score_popup(hit_sprite.rect.centerx, hit_sprite.rect.centery, points)
                
                # Particle explosion
                self.ui.particle_system.emit_explosion(
                    hit_sprite.rect.centerx, 
                    hit_sprite.rect.centery,
                    PARTICLE_COUNT_EXPLOSION,
                    (255, 150, 50)
                )
                
                if self.game_mode == 'levels':
                    # Check if level complete
                    if self.enemies_spawned >= self.enemies_for_level and len(self.obstacle_sprites) == 0:
                        self.start_level(self.current_level + 1)

        # Player vs Obstacles
        collide_sprites = pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True)
        if collide_sprites:
            for sprite in collide_sprites:
                if self.collision_sound: self.collision_sound.play()
                self.player.health -= 20
                Explosion(sprite.rect.center, [self.visible_sprites, self.all_sprites])
                
                # Visual feedback for damage
                self.ui.trigger_screen_shake(SCREEN_SHAKE_TRAUMA)
                self.ui.trigger_damage_flash()
                
                # Particle explosion
                self.ui.particle_system.emit_explosion(
                    sprite.rect.centerx,
                    sprite.rect.centery,
                    PARTICLE_COUNT_EXPLOSION,
                    (255, 50, 50)
                )
                
                if self.player.health <= 0:
                    self.game_over()

    def game_over(self):
        self.game_active = False
        self.game_state = 'game_over'
        # Maybe show explosion on player
        Explosion(self.player.rect.center, [self.visible_sprites, self.all_sprites])
        # Big explosion effect
        self.ui.particle_system.emit_explosion(
            self.player.rect.centerx,
            self.player.rect.centery,
            PARTICLE_COUNT_EXPLOSION * 2,
            (255, 100, 0)
        )
        self.ui.trigger_screen_shake(SCREEN_SHAKE_TRAUMA * 2)
    
    def return_to_menu(self):
        """Return to main menu"""
        self.game_active = False
        self.game_state = 'menu'
    
    def quit_game(self):
        """Quit the game"""
        pygame.quit()
        sys.exit()

    def handle_event(self, event):
        # Pass events to UI for button handling
        self.ui.handle_event(event, self.game_state)
        
        if event.type == pygame.KEYDOWN:
            if self.game_active:
                if event.key == pygame.K_ESCAPE:
                    self.return_to_menu()

        if self.game_active:
            if event.type == self.enemy_spawn_timer:
                self.create_enemy()
            if event.type == self.meteor_spawn_timer:
                self.create_meteor()

    def update(self):
        # Always update UI animations
        dt = 1 / FPS  # Delta time
        self.ui.update(dt, self.game_state)
        
        if self.game_active:
            self.all_sprites.update()
            self.check_collisions()

    def draw(self):
        if self.game_state == 'playing':
            # Draw starfield background
            self.ui.particle_system.draw(self.display_surface)
            
            # Draw game sprites
            self.visible_sprites.draw(self.display_surface)
            
            # Draw HUD
            self.ui.display_hud(self.player)
            
            # Draw flash effect
            self.ui.flash_effect.draw(self.display_surface)
            
        elif self.game_state == 'game_over':
            # Draw final game state
            self.ui.particle_system.draw(self.display_surface)
            self.visible_sprites.draw(self.display_surface)
            self.ui.show_game_over(self.player.score if self.player else 0)
            
        else:  # menu
            self.ui.show_menu()

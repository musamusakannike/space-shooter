
import pygame
import sys
import random
from settings import *
from sprites import Player, Bullet, Enemy, Meteor, Explosion, EnemyShooter, EnemyRocket, PowerUp, PowerDown
from ui import UI
from effects import ParticleSystem
from story_mode import StoryMode

class GameManager:
    def __init__(self, surface):
        self.display_surface = surface
        self.ui = UI(self.display_surface)
        self.fullscreen_callback = None  # Will be set by main game
        
        # Story mode system
        self.story_mode = StoryMode()
        
        # Setup UI callbacks
        self.ui.create_menu_buttons({
            'endless': lambda: self.start_game('endless'),
            'story': self.show_story_select,
            'fullscreen': self.toggle_fullscreen,
            'quit': self.quit_game
        })
        
        self.ui.create_game_over_buttons({
            'restart': lambda: self.start_game(self.game_mode),
            'menu': self.return_to_menu
        })
        
        # Sprite Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.powerdowns = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        # Game State
        self.game_active = False
        self.game_state = 'menu'  # 'menu', 'story_select', 'playing', 'game_over', 'story_complete'
        self.game_mode = 'endless'
        self.current_story_id = None
        self.enemies_spawned = 0
        self.wave_enemies_remaining = 0
        self.story_start_time = 0
        
        # Timers
        self.enemy_spawn_timer = pygame.event.custom_type()
        self.meteor_spawn_timer = pygame.event.custom_type()
        self.powerup_spawn_timer = pygame.event.custom_type()
        self.powerdown_spawn_timer = pygame.event.custom_type()
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

    def start_game(self, mode='endless', story_id=None):
        self.game_active = True
        self.game_state = 'playing'
        self.game_mode = mode
        
        # Reset groups
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.powerups.empty()
        self.powerdowns.empty()
        self.all_sprites.empty()
        
        # Create Player
        self.player = Player([self.visible_sprites, self.all_sprites])
        self.player.create_bullet_callback = self.create_player_bullet
        
        if mode == 'story' and story_id:
            self.start_story(story_id)
    
    def start_story(self, story_id):
        """Initialize a story mode game"""
        if self.story_mode.start_story(story_id):
            self.current_story_id = story_id
            self.enemies_spawned = 0
            self.story_start_time = pygame.time.get_ticks()
            
            story = self.story_mode.current_story
            
            # Apply story challenges to player
            for challenge in story.challenges:
                if challenge.type == 'limited_bullets':
                    self.player.bullets_remaining = challenge.value
                elif challenge.type == 'shoot_cooldown':
                    self.player.shoot_delay = challenge.value
            
            # Set up timers for story mode
            pygame.time.set_timer(self.powerup_spawn_timer, story.power_up_spawn_rate)
            pygame.time.set_timer(self.powerdown_spawn_timer, story.power_down_spawn_rate)
            
            # Start first wave
            self.start_wave()
    
    def start_wave(self):
        """Start the current wave in story mode"""
        wave = self.story_mode.get_current_wave()
        if wave:
            self.wave_enemies_remaining = wave.enemy_count
            self.enemies_spawned = 0
            
            # Adjust spawn timer based on wave
            pygame.time.set_timer(self.enemy_spawn_timer, wave.spawn_interval)
            pygame.time.set_timer(self.meteor_spawn_timer, 3000 if wave.meteor_count > 0 else 0)

    def create_player_bullet(self, x, y):
        Bullet((x, y), [self.visible_sprites, self.player_bullets, self.all_sprites], is_player=True)
    
    def create_enemy_bullet(self, x, y):
        """Create enemy bullet"""
        Bullet((x, y), [self.visible_sprites, self.enemy_bullets, self.all_sprites], is_player=False)

    def create_enemy(self):
        """Create enemies based on game mode"""
        if self.game_mode == 'story':
            wave = self.story_mode.get_current_wave()
            if wave and self.enemies_spawned < wave.enemy_count:
                # Select random enemy type from wave
                enemy_type = random.choice(wave.enemy_types)
                
                if enemy_type == 'shooter':
                    enemy = EnemyShooter([self.visible_sprites, self.obstacle_sprites, self.all_sprites])
                    enemy.create_bullet_callback = self.create_enemy_bullet
                elif enemy_type == 'rocket':
                    EnemyRocket([self.visible_sprites, self.obstacle_sprites, self.all_sprites])
                else:
                    Enemy([self.visible_sprites, self.obstacle_sprites, self.all_sprites], enemy_type)
                
                self.enemies_spawned += 1
        else:
            # Endless mode
            Enemy([self.visible_sprites, self.obstacle_sprites, self.all_sprites])

    def create_meteor(self):
        Meteor([self.visible_sprites, self.obstacle_sprites, self.all_sprites])
    
    def create_powerup(self):
        """Spawn a random power-up"""
        power_types = ['health', 'speed_boost', 'invincibility', 'rapid_fire', 'shield']
        power_type = random.choice(power_types)
        x_pos = random.randint(50, SCREEN_WIDTH - 50)
        PowerUp((x_pos, -30), [self.visible_sprites, self.powerups, self.all_sprites], power_type)
    
    def create_powerdown(self):
        """Spawn a random power-down"""
        debuff_types = ['slow', 'weak_bullets', 'reverse_controls']
        debuff_type = random.choice(debuff_types)
        x_pos = random.randint(50, SCREEN_WIDTH - 50)
        PowerDown((x_pos, -30), [self.visible_sprites, self.powerdowns, self.all_sprites], debuff_type)

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
                
                # Story mode wave tracking
                if self.game_mode == 'story':
                    self.wave_enemies_remaining -= 1
                    if self.wave_enemies_remaining <= 0 and self.enemies_spawned >= self.story_mode.get_current_wave().enemy_count:
                        self.story_mode.advance_wave()
                        wave = self.story_mode.get_current_wave()
                        if wave:
                            self.start_wave()
                        else:
                            self.story_complete()

        # Player vs Obstacles (with shield/invincibility check)
        if not self.player.invincible:
            collide_sprites = pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True)
            if collide_sprites:
                for sprite in collide_sprites:
                    if self.collision_sound: self.collision_sound.play()
                    
                    # Shield absorbs damage
                    if self.player.shield_active:
                        self.player.shield_active = False
                        damage = 10
                    else:
                        damage = 20
                    
                    self.player.health -= damage
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
        
        # Enemy bullets vs Player
        if not self.player.invincible:
            bullet_hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if bullet_hits:
                for bullet in bullet_hits:
                    if self.player.shield_active:
                        self.player.shield_active = False
                        damage = 5
                    else:
                        damage = 10
                    
                    self.player.health -= damage
                    self.ui.trigger_damage_flash()
                    
                    if self.player.health <= 0:
                        self.game_over()
        
        # Player vs Power-ups
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.player.apply_powerup(powerup.power_type)
            self.ui.add_score_popup(powerup.rect.centerx, powerup.rect.centery, f"+{powerup.power_type.upper()}", (50, 255, 100))
            self.ui.particle_system.emit_explosion(
                powerup.rect.centerx,
                powerup.rect.centery,
                10,
                powerup.color
            )
        
        # Player vs Power-downs
        powerdown_hits = pygame.sprite.spritecollide(self.player, self.powerdowns, True)
        for powerdown in powerdown_hits:
            self.player.apply_powerdown(powerdown.debuff_type)
            self.ui.add_score_popup(powerdown.rect.centerx, powerdown.rect.centery, f"-{powerdown.debuff_type.upper()}", (255, 50, 50))
            self.ui.particle_system.emit_explosion(
                powerdown.rect.centerx,
                powerdown.rect.centery,
                10,
                powerdown.color
            )

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
    
    def story_complete(self):
        """Handle story completion"""
        self.game_active = False
        self.game_state = 'story_complete'
        
        # Add completion bonus
        if self.story_mode.current_story:
            self.player.score += self.story_mode.current_story.completion_reward
    
    def show_story_select(self):
        """Show story selection screen"""
        self.game_state = 'story_select'
    
    def return_to_menu(self):
        """Return to main menu"""
        self.game_active = False
        self.game_state = 'menu'
    
    def quit_game(self):
        """Quit the game"""
        pygame.quit()
        sys.exit()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.fullscreen_callback:
            self.fullscreen_callback()

    def handle_event(self, event):
        # Pass events to UI for button handling
        self.ui.handle_event(event, self.game_state)
        
        if event.type == pygame.KEYDOWN:
            # Handle narrative advancement
            if self.game_mode == 'story' and self.story_mode.show_narrative:
                if event.key == pygame.K_SPACE:
                    self.story_mode.advance_narrative()
                    return
            
            # Handle story select back button
            if self.game_state == 'story_select':
                if event.key == pygame.K_ESCAPE:
                    self.return_to_menu()
            
            if self.game_active:
                if event.key == pygame.K_ESCAPE:
                    self.return_to_menu()

        if self.game_active:
            if event.type == self.enemy_spawn_timer:
                self.create_enemy()
            if event.type == self.meteor_spawn_timer:
                self.create_meteor()
            if event.type == self.powerup_spawn_timer:
                self.create_powerup()
            if event.type == self.powerdown_spawn_timer:
                self.create_powerdown()

    def update(self):
        # Always update UI animations
        dt = 1 / FPS  # Delta time
        self.ui.update(dt, self.game_state)
        
        # Don't update game if narrative is showing
        if self.game_mode == 'story' and self.story_mode.show_narrative:
            return
        
        if self.game_active:
            self.all_sprites.update()
            self.check_collisions()
            
            # Check story mode challenges
            if self.game_mode == 'story' and self.story_mode.current_story:
                # Check time limit
                for challenge in self.story_mode.current_story.challenges:
                    if challenge.type == 'time_limit':
                        # Account for pause time from narrative
                        elapsed = (pygame.time.get_ticks() - self.story_start_time - self.story_mode.total_pause_time) // 1000
                        remaining = challenge.value - elapsed
                        self.story_mode.update_challenge('time_limit', remaining)
                        
                        if remaining <= 0:
                            self.game_over()
                
                # Check if out of bullets
                if self.player.bullets_remaining == 0:
                    # Check if there are still enemies
                    if len(self.obstacle_sprites) > 0:
                        self.game_over()

    def draw(self):
        if self.game_state == 'playing':
            # Draw starfield background
            self.ui.particle_system.draw(self.display_surface)
            
            # Draw game sprites
            self.visible_sprites.draw(self.display_surface)
            
            # Draw HUD based on mode
            if self.game_mode == 'story':
                self.ui.display_story_hud(self.player, self.story_mode)
                
                # Show narrative if active
                if self.story_mode.show_narrative:
                    self.ui.display_narrative(self.story_mode.current_story.narrative)
            else:
                self.ui.display_hud(self.player)
            
            # Draw flash effect
            self.ui.flash_effect.draw(self.display_surface)
            
        elif self.game_state == 'story_select':
            # Create story buttons if not already created
            if not self.ui.story_buttons:
                stories = self.story_mode.get_all_stories()
                self.ui.create_story_buttons(stories, lambda sid: self.start_game('story', sid))
            
            self.ui.show_story_select(self.story_mode.get_all_stories())
            
        elif self.game_state == 'story_complete':
            # Draw final game state
            self.ui.particle_system.draw(self.display_surface)
            self.visible_sprites.draw(self.display_surface)
            self.ui.show_story_complete(
                self.story_mode.current_story,
                self.player.score if self.player else 0
            )
            
        elif self.game_state == 'game_over':
            # Draw final game state
            self.ui.particle_system.draw(self.display_surface)
            self.visible_sprites.draw(self.display_surface)
            self.ui.show_game_over(self.player.score if self.player else 0)
            
        else:  # menu
            self.ui.show_menu()

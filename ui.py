
import pygame
import math
from settings import *
from effects import *

class Button:
    """Modern button with hover and click effects"""
    def __init__(self, text, x, y, width, height, callback=None, font_size=36):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback = callback
        self.font = pygame.font.SysFont('arial', font_size, bold=True)
        
        self.hovered = False
        self.pressed = False
        self.scale = 1.0
        self.target_scale = 1.0
        
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
    
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            self.target_scale = BUTTON_HOVER_SCALE if self.hovered else 1.0
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.pressed = True
                self.target_scale = BUTTON_CLICK_SCALE
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and event.button == 1:
                self.pressed = False
                if self.hovered and self.callback:
                    self.callback()
                self.target_scale = BUTTON_HOVER_SCALE if self.hovered else 1.0
    
    def update(self, dt):
        """Update button animation"""
        # Smooth scale transition
        self.scale += (self.target_scale - self.scale) * 10 * dt
    
    def draw(self, surface):
        """Draw button with effects"""
        # Calculate scaled dimensions
        scaled_width = int(self.width * self.scale)
        scaled_height = int(self.height * self.scale)
        scaled_rect = pygame.Rect(
            self.x - scaled_width // 2,
            self.y - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Draw glow effect when hovered
        if self.hovered:
            glow_surf = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
            glow_rect = glow_surf.get_rect(center=(self.x, self.y))
            pygame.draw.rect(glow_surf, (*UI_PRIMARY, 50), glow_surf.get_rect(), border_radius=15)
            surface.blit(glow_surf, glow_rect)
        
        # Draw button background with gradient effect
        button_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        
        # Create gradient
        for i in range(scaled_height):
            progress = i / scaled_height
            color = color_lerp(UI_SECONDARY, UI_PRIMARY, progress)
            pygame.draw.line(button_surf, color, (0, i), (scaled_width, i))
        
        # Draw border
        pygame.draw.rect(button_surf, UI_PRIMARY, button_surf.get_rect(), 3, border_radius=10)
        
        surface.blit(button_surf, scaled_rect)
        
        # Draw text
        text_surf = self.font.render(self.text, True, UI_TEXT)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)

class UI:
    def __init__(self, surface):
        self.display_surface = surface
        self.font = pygame.font.SysFont('arial', 30)
        self.menu_font = pygame.font.SysFont('arial', 70, bold=True)
        self.title_font = pygame.font.SysFont('arial', 90, bold=True)
        
        # Visual effects
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.flash_effect = FlashEffect()
        self.text_popups = []
        
        # Initialize starfield
        self.particle_system.emit_star_field(SCREEN_WIDTH, SCREEN_HEIGHT, PARTICLE_COUNT_STARS)
        
        # Menu buttons
        self.menu_buttons = []
        self.game_over_buttons = []
        
        # Animation state
        self.title_pulse = 0
        self.menu_fade_alpha = 0
        self.score_display = 0
        self.score_target = 0
        
        # Health bar animation
        self.health_display = 100
        self.health_target = 100

    def create_menu_buttons(self, callbacks):
        """Create menu buttons with callbacks"""
        self.menu_buttons = [
            Button("START ENDLESS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 300, 60, callbacks.get('endless')),
            Button("STORY MODE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, 300, 60, callbacks.get('story')),
            Button("TOGGLE FULLSCREEN", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160, 300, 60, callbacks.get('fullscreen')),
            Button("QUIT", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 240, 300, 60, callbacks.get('quit')),
        ]
        
        # Story selection buttons (created dynamically)
        self.story_buttons = []
    
    def create_story_buttons(self, stories, start_story_callback):
        """Create story selection buttons"""
        self.story_buttons = []
        start_y = SCREEN_HEIGHT // 2 - 100
        
        for i, story in enumerate(stories):
            button = Button(
                f"STORY {story.id}: {story.title}",
                SCREEN_WIDTH // 2,
                start_y + (i * 100),
                500,
                70,
                lambda sid=story.id: start_story_callback(sid),
                font_size=32
            )
            self.story_buttons.append(button)
        
        # Add back button
        back_button = Button(
            "BACK TO MENU",
            SCREEN_WIDTH // 2,
            start_y + (len(stories) * 100) + 50,
            300,
            60,
            lambda: None  # Will be handled separately
        )
        self.story_buttons.append(back_button)
    
    def create_game_over_buttons(self, callbacks):
        """Create game over buttons"""
        self.game_over_buttons = [
            Button("RESTART", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, 250, 60, callbacks.get('restart')),
            Button("MAIN MENU", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180, 250, 60, callbacks.get('menu')),
        ]

    def handle_event(self, event, game_state):
        """Handle UI events"""
        if game_state == 'menu':
            for button in self.menu_buttons:
                button.handle_event(event)
        elif game_state == 'story_select':
            for button in self.story_buttons:
                button.handle_event(event)
        elif game_state == 'game_over' or game_state == 'story_complete':
            for button in self.game_over_buttons:
                button.handle_event(event)

    def update(self, dt, game_state='menu'):
        """Update UI animations"""
        self.particle_system.update(dt)
        self.screen_shake.update(dt)
        self.flash_effect.update(dt)
        
        # Update text popups
        self.text_popups = [popup for popup in self.text_popups if popup.update(dt)]
        
        # Update buttons
        if game_state == 'menu':
            for button in self.menu_buttons:
                button.update(dt)
        elif game_state == 'story_select':
            for button in self.story_buttons:
                button.update(dt)
        elif game_state == 'game_over' or game_state == 'story_complete':
            for button in self.game_over_buttons:
                button.update(dt)
        
        # Pulse animation for title
        self.title_pulse += dt * PULSE_SPEED
        
        # Smooth score counter
        if self.score_display < self.score_target:
            self.score_display += (self.score_target - self.score_display) * 5 * dt
            if abs(self.score_target - self.score_display) < 1:
                self.score_display = self.score_target
        
        # Smooth health bar
        if abs(self.health_display - self.health_target) > 0.5:
            self.health_display += (self.health_target - self.health_display) * 8 * dt

    def add_score_popup(self, x, y, points, color=None):
        """Add a floating score popup"""
        if color is None:
            color = UI_ACCENT
        
        # Handle both numeric and string points
        text = f"+{points}" if isinstance(points, int) else str(points)
        self.text_popups.append(TextPopup(text, x, y, color, 36))

    def trigger_damage_flash(self):
        """Trigger red flash for damage"""
        self.flash_effect.trigger(UI_DANGER, 0.15)
    
    def trigger_screen_shake(self, intensity=SCREEN_SHAKE_TRAUMA):
        """Trigger screen shake"""
        self.screen_shake.add_trauma(intensity)

    def show_text(self, text, pos, font, color=WHITE, center=False):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(topleft=pos)
        if center:
            text_rect.center = pos
        self.display_surface.blit(text_surf, text_rect)

    def draw_gradient_rect(self, rect, color1, color2, vertical=True):
        """Draw a rectangle with gradient"""
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        if vertical:
            for i in range(rect.height):
                progress = i / rect.height
                color = color_lerp(color1, color2, progress)
                pygame.draw.line(surf, color, (0, i), (rect.width, i))
        else:
            for i in range(rect.width):
                progress = i / rect.width
                color = color_lerp(color1, color2, progress)
                pygame.draw.line(surf, (*color, 255), (i, 0), (i, rect.height))
        
        self.display_surface.blit(surf, rect.topleft)

    def display_hud(self, player):
        """Enhanced HUD with animations"""
        # Update targets
        self.health_target = player.health
        self.score_target = player.score
        
        # Health Bar with gradient
        bar_width = 300
        bar_height = 30
        bar_x = 20
        bar_y = 20
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.display_surface, (30, 30, 30), bg_rect, border_radius=5)
        
        # Health fill with gradient based on health level
        health_percent = self.health_display / player.max_health
        fill_width = int(bar_width * health_percent)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            
            # Choose gradient colors based on health
            if health_percent > 0.6:
                color1, color2 = HEALTH_GRADIENT_HIGH, color_lerp(HEALTH_GRADIENT_HIGH, HEALTH_GRADIENT_MID, 0.5)
            elif health_percent > 0.3:
                color1, color2 = HEALTH_GRADIENT_MID, color_lerp(HEALTH_GRADIENT_MID, HEALTH_GRADIENT_LOW, 0.5)
            else:
                color1, color2 = HEALTH_GRADIENT_LOW, (150, 0, 0)
            
            self.draw_gradient_rect(fill_rect, color1, color2, vertical=False)
        
        # Border
        pygame.draw.rect(self.display_surface, UI_PRIMARY, bg_rect, 3, border_radius=5)
        
        # Health text
        health_text = f"HP: {int(self.health_display)}"
        self.show_text(health_text, (bar_x + 10, bar_y + 5), self.font, UI_TEXT)
        
        # Score with glow effect
        score_text = f"SCORE: {int(self.score_display)}"
        score_surf = self.font.render(score_text, True, UI_ACCENT)
        score_rect = score_surf.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        
        # Glow
        glow_surf = self.font.render(score_text, True, (*UI_ACCENT, 100))
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_rect = score_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            self.display_surface.blit(glow_surf, glow_rect)
        
        self.display_surface.blit(score_surf, score_rect)
        
        # Draw text popups
        for popup in self.text_popups:
            popup.draw(self.display_surface)

    def show_menu(self):
        """Enhanced menu with animations"""
        # Draw starfield
        self.particle_system.draw(self.display_surface)
        
        # Title with pulse effect
        pulse = math.sin(self.title_pulse * math.pi) * 0.1 + 1.0
        title_text = "SPACE SHOOTER"
        
        # Draw title glow
        glow_font = pygame.font.SysFont('arial', int(90 * pulse), bold=True)
        glow_surf = glow_font.render(title_text, True, (*UI_PRIMARY, 150))
        glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        
        for offset in [(4, 4), (-4, 4), (4, -4), (-4, -4), (0, 4), (0, -4), (4, 0), (-4, 0)]:
            offset_rect = glow_rect.copy()
            offset_rect.x += offset[0]
            offset_rect.y += offset[1]
            self.display_surface.blit(glow_surf, offset_rect)
        
        # Draw title
        title_surf = self.title_font.render(title_text, True, UI_TEXT)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.display_surface.blit(title_surf, title_rect)
        
        # Draw buttons
        for button in self.menu_buttons:
            button.draw(self.display_surface)

    def show_game_over(self, score, stats=None):
        """Enhanced game over screen"""
        # Draw starfield
        self.particle_system.draw(self.display_surface)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.display_surface.blit(overlay, (0, 0))
        
        # Game Over title
        game_over_surf = self.title_font.render("GAME OVER", True, UI_DANGER)
        game_over_rect = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        
        # Glow effect
        glow_surf = self.title_font.render("GAME OVER", True, (*UI_DANGER, 100))
        for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
            glow_rect = game_over_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            self.display_surface.blit(glow_surf, glow_rect)
        
        self.display_surface.blit(game_over_surf, game_over_rect)
        
        # Final Score
        score_text = f"FINAL SCORE: {int(self.score_display)}"
        score_surf = self.menu_font.render(score_text, True, UI_ACCENT)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.display_surface.blit(score_surf, score_rect)
        
        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(self.display_surface)
    
    def show_story_select(self, stories):
        """Display story selection screen"""
        # Draw starfield
        self.particle_system.draw(self.display_surface)
        
        # Title
        title_text = "SELECT YOUR MISSION"
        title_surf = self.title_font.render(title_text, True, UI_PRIMARY)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.display_surface.blit(title_surf, title_rect)
        
        # Draw story buttons
        for button in self.story_buttons:
            button.draw(self.display_surface)
        
        # Draw story descriptions
        start_y = SCREEN_HEIGHT // 2 - 100
        for i, story in enumerate(stories):
            desc_y = start_y + (i * 100) + 45
            desc_text = story.subtitle
            desc_surf = pygame.font.SysFont('arial', 20).render(desc_text, True, UI_TEXT_DIM)
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH // 2, desc_y))
            self.display_surface.blit(desc_surf, desc_rect)
    
    def show_story_complete(self, story, score):
        """Display story completion screen"""
        # Draw starfield
        self.particle_system.draw(self.display_surface)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.display_surface.blit(overlay, (0, 0))
        
        # Mission Complete title
        complete_surf = self.title_font.render("MISSION COMPLETE!", True, UI_SUCCESS)
        complete_rect = complete_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        
        # Glow effect
        glow_surf = self.title_font.render("MISSION COMPLETE!", True, (*UI_SUCCESS, 100))
        for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
            glow_rect = complete_rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            self.display_surface.blit(glow_surf, glow_rect)
        
        self.display_surface.blit(complete_surf, complete_rect)
        
        # Story title
        story_surf = self.menu_font.render(story.title, True, UI_PRIMARY)
        story_rect = story_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.display_surface.blit(story_surf, story_rect)
        
        # Final Score
        score_text = f"FINAL SCORE: {int(self.score_display)}"
        score_surf = self.menu_font.render(score_text, True, UI_ACCENT)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.display_surface.blit(score_surf, score_rect)
        
        # Bonus
        bonus_text = f"COMPLETION BONUS: +{story.completion_reward}"
        bonus_surf = self.font.render(bonus_text, True, UI_SUCCESS)
        bonus_rect = bonus_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.display_surface.blit(bonus_surf, bonus_rect)
        
        # Draw buttons
        for button in self.game_over_buttons:
            button.draw(self.display_surface)
    
    def display_story_hud(self, player, story_mode):
        """Display HUD for story mode with challenges and wave info"""
        # Standard HUD
        self.display_hud(player)
        
        # Story-specific info
        if story_mode.current_story:
            story = story_mode.current_story
            
            # Wave indicator
            wave_num = story_mode.current_wave_index + 1
            total_waves = len(story.waves)
            wave_text = f"WAVE {wave_num}/{total_waves}"
            wave_surf = self.font.render(wave_text, True, UI_PRIMARY)
            wave_rect = wave_surf.get_rect(center=(SCREEN_WIDTH // 2, 20))
            self.display_surface.blit(wave_surf, wave_rect)
            
            # Challenges display
            y_offset = 60
            for challenge in story.challenges:
                if challenge.type in story_mode.challenges_status:
                    status = story_mode.challenges_status[challenge.type]
                    
                    if challenge.type == 'limited_bullets':
                        text = f"AMMO: {player.bullets_remaining}"
                        color = UI_DANGER if player.bullets_remaining < 10 else UI_TEXT
                    elif challenge.type == 'time_limit':
                        # Account for pause time from narrative
                        elapsed = (pygame.time.get_ticks() - story_mode.story_start_time - story_mode.total_pause_time) // 1000
                        remaining = max(0, challenge.value - elapsed)
                        text = f"TIME: {remaining}s"
                        color = UI_DANGER if remaining < 30 else UI_TEXT
                    elif challenge.type == 'shoot_cooldown':
                        text = f"FIRE RATE: SLOW"
                        color = UI_TEXT_DIM
                    else:
                        continue
                    
                    challenge_surf = pygame.font.SysFont('arial', 24).render(text, True, color)
                    challenge_rect = challenge_surf.get_rect(topleft=(20, y_offset))
                    self.display_surface.blit(challenge_surf, challenge_rect)
                    y_offset += 30
            
            # Power-up status indicators
            status_y = SCREEN_HEIGHT - 100
            if player.invincible:
                inv_surf = pygame.font.SysFont('arial', 20, bold=True).render("INVINCIBLE", True, (255, 215, 0))
                self.display_surface.blit(inv_surf, (SCREEN_WIDTH - 150, status_y))
                status_y += 25
            
            if player.shield_active:
                shield_surf = pygame.font.SysFont('arial', 20, bold=True).render("SHIELD", True, (150, 150, 255))
                self.display_surface.blit(shield_surf, (SCREEN_WIDTH - 150, status_y))
                status_y += 25
            
            if player.reverse_controls:
                rev_surf = pygame.font.SysFont('arial', 20, bold=True).render("REVERSED!", True, (255, 50, 50))
                self.display_surface.blit(rev_surf, (SCREEN_WIDTH - 150, status_y))
    
    def display_narrative(self, narrative_text):
        """Display story narrative text"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.display_surface.blit(overlay, (0, 0))
        
        # Narrative box
        box_width = 800
        box_height = 400
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        # Background
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.display_surface, (20, 20, 40), box_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, UI_PRIMARY, box_rect, 3, border_radius=10)
        
        # Display narrative lines
        line_height = 40
        start_y = box_y + 50
        
        for i, line in enumerate(narrative_text):
            line_surf = self.font.render(line, True, UI_TEXT)
            line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * line_height))
            self.display_surface.blit(line_surf, line_rect)
        
        # Continue prompt
        prompt_text = "Press SPACE to continue..."
        prompt_surf = pygame.font.SysFont('arial', 24).render(prompt_text, True, UI_TEXT_DIM)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, box_y + box_height - 40))
        self.display_surface.blit(prompt_surf, prompt_rect)

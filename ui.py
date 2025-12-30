
import pygame
from settings import *

class UI:
    def __init__(self, surface):
        self.display_surface = surface
        self.font = pygame.font.SysFont('arial', 30)
        self.menu_font = pygame.font.SysFont('arial', 50)

    def show_text(self, text, pos, font, color=WHITE, center=False):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(topleft=pos)
        if center:
            text_rect.center = pos
        self.display_surface.blit(text_surf, text_rect)

    def display_hud(self, player):
        # Health Bar
        health_rect = pygame.Rect(10, 10, player.health * 2, 20)
        pygame.draw.rect(self.display_surface, RED, health_rect)
        pygame.draw.rect(self.display_surface, WHITE, (10, 10, player.max_health * 2, 20), 2)
        
        # Score
        self.show_text(f'Score: {player.score}', (SCREEN_WIDTH - 200, 10), self.font)

    def show_menu(self):
        self.display_surface.fill(BLACK)
        self.show_text("SPACE SHOOTER", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4), self.menu_font, center=True)
        self.show_text("Press ENTER to Start Endless Mode", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.font, center=True)
        self.show_text("Press L for Level Mode", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), self.font, center=True)
        self.show_text("Press Q to Quit", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100), self.font, center=True)
        pygame.display.flip()

    def show_game_over(self, score):
        self.display_surface.fill(BLACK)
        self.show_text("GAME OVER", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3), self.menu_font, color=RED, center=True)
        self.show_text(f"Final Score: {score}", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.font, center=True)
        self.show_text("Press R to Restart or Q to Quit", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60), self.font, center=True)
        pygame.display.flip()

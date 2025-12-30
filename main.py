
import pygame
import sys
from settings import *
from asset_manager import asset_manager
from game_manager import GameManager

class Game:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize Audio
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(BG_MUSIC_PATH)
            pygame.mixer.music.play(loops=-1)
            print("Background music started.")
        except Exception as e:
            print(f"Error loading music: {e}")
        
        # Load assets
        print("Loading assets...")
        asset_manager.load_images()
        print("Assets loaded.")

        # Initialize Game Manager
        self.game_manager = GameManager(self.screen)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Pass events to Game Manager
            self.game_manager.handle_event(event)

    def update(self):
        self.game_manager.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.game_manager.draw()
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
    game.quit()

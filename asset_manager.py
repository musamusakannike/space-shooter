
import pygame
import os
from settings import *

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def load_images(self, directory=SPRITES_DIR):
        """Recursively loads all images from the specified directory."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(root, file)
                    # Create a key based on the relative path from SPRITES_DIR, without extension
                    # e.g., Sprites/Ships/spaceShips_001.png -> ships_spaceships_001
                    rel_path = os.path.relpath(file_path, directory)
                    key = rel_path.replace(os.sep, '_').replace('.', '_').lower()
                    
                    try:
                        image = pygame.image.load(file_path).convert_alpha()
                        self.images[key] = image
                    except pygame.error as e:
                        print(f"Failed to load image: {file_path}. Error: {e}")

    def get_image(self, name):
        return self.images.get(name)

    def scale_image(self, name, size):
        if name in self.images:
            self.images[name] = pygame.transform.scale(self.images[name], size)

asset_manager = AssetManager()

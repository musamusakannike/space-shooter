import pygame
import os
import sys
from settings import BG_MUSIC_PATH, COLLISION_SOUND_PATH

def verify_audio():
    print(f"Checking audio file at: {BG_MUSIC_PATH}")
    print(f"Checking collision sound at: {COLLISION_SOUND_PATH}")
    
    if not os.path.exists(BG_MUSIC_PATH):
        print("FAIL: Audio file not found!")
    
    if not os.path.exists(COLLISION_SOUND_PATH):
        print("FAIL: Collision sound not found!")

    try:
        pygame.init()
        pygame.mixer.init()
        print("Pygame mixer initialized.")
        
        pygame.mixer.music.load(BG_MUSIC_PATH)
        print("Music loaded successfully.")
        
        collision_sound = pygame.mixer.Sound(COLLISION_SOUND_PATH)
        print("Collision sound loaded successfully.")

        pygame.mixer.music.play()
        collision_sound.play()
        if pygame.mixer.music.get_busy():
            print("SUCCESS: Music is playing.")
        else:
            print("WARNING: Music started but get_busy() returned False (might be too short or issue).")
            
        pygame.mixer.music.stop()
        pygame.quit()
        
    except Exception as e:
        print(f"FAIL: Error during audio verification: {e}")

if __name__ == "__main__":
    verify_audio()

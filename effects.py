
import pygame
import random
import math
from settings import *

class Particle:
    """Individual particle for particle systems"""
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        self.alpha = 255
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        # Fade out over lifetime
        self.alpha = int(255 * (1 - self.age / self.lifetime))
        return self.age < self.lifetime
    
    def draw(self, surface):
        if self.alpha > 0:
            color_with_alpha = (*self.color[:3], self.alpha)
            # Create a surface with per-pixel alpha
            particle_surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
            surface.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    """Manages multiple particles for various effects"""
    def __init__(self):
        self.particles = []
    
    def emit_star_field(self, width, height, count=100):
        """Create a starfield background"""
        for _ in range(count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            vx = 0
            vy = random.uniform(0.5, 2.0)
            color = random.choice([
                (255, 255, 255),
                (200, 200, 255),
                (255, 255, 200),
            ])
            size = random.uniform(0.5, 2.0)
            lifetime = float('inf')  # Stars don't die
            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
    
    def emit_explosion(self, x, y, count=20, color=(255, 100, 0)):
        """Create an explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2, 5)
            lifetime = random.uniform(0.3, 0.8)
            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
    
    def emit_trail(self, x, y, color=(100, 200, 255)):
        """Create a trail effect for bullets or ships"""
        vx = random.uniform(-20, 20)
        vy = random.uniform(-20, 20)
        size = random.uniform(1, 3)
        lifetime = random.uniform(0.2, 0.5)
        self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
    
    def update(self, dt):
        """Update all particles and remove dead ones"""
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Wrap stars around screen
        for p in self.particles:
            if p.lifetime == float('inf'):  # Stars
                if p.y > SCREEN_HEIGHT:
                    p.y = 0
                    p.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)

class ScreenShake:
    """Handles screen shake effects"""
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.trauma = 0
        self.trauma_power = 2
        self.max_offset = 20
    
    def add_trauma(self, amount):
        """Add trauma (0-1 range)"""
        self.trauma = min(1.0, self.trauma + amount)
    
    def update(self, dt):
        """Update shake offset based on trauma"""
        if self.trauma > 0:
            # Decay trauma over time
            self.trauma = max(0, self.trauma - dt * 2)
            
            # Calculate shake based on trauma
            shake = self.trauma ** self.trauma_power
            self.offset_x = self.max_offset * shake * random.uniform(-1, 1)
            self.offset_y = self.max_offset * shake * random.uniform(-1, 1)
        else:
            self.offset_x = 0
            self.offset_y = 0
    
    def apply(self, pos):
        """Apply shake offset to a position"""
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)

class FlashEffect:
    """Screen flash effect for damage or other events"""
    def __init__(self):
        self.active = False
        self.alpha = 0
        self.color = (255, 255, 255)
        self.duration = 0
        self.elapsed = 0
    
    def trigger(self, color=(255, 0, 0), duration=0.1):
        """Trigger a flash effect"""
        self.active = True
        self.color = color
        self.duration = duration
        self.elapsed = 0
        self.alpha = 150
    
    def update(self, dt):
        """Update flash effect"""
        if self.active:
            self.elapsed += dt
            # Fade out
            self.alpha = int(150 * (1 - self.elapsed / self.duration))
            if self.elapsed >= self.duration:
                self.active = False
                self.alpha = 0
    
    def draw(self, surface):
        """Draw flash overlay"""
        if self.active and self.alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*self.color, self.alpha))
            surface.blit(flash_surf, (0, 0))

class TextPopup:
    """Floating text popup for score, combos, etc."""
    def __init__(self, text, x, y, color=(255, 255, 0), font_size=30):
        self.text = text
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.font = pygame.font.SysFont('arial', font_size, bold=True)
        self.lifetime = 1.0
        self.age = 0
        self.alpha = 255
    
    def update(self, dt):
        """Update popup animation"""
        self.age += dt
        # Float upward
        self.y = self.start_y - (self.age * 50)
        # Fade out
        self.alpha = int(255 * (1 - self.age / self.lifetime))
        return self.age < self.lifetime
    
    def draw(self, surface):
        """Draw popup text"""
        if self.alpha > 0:
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(self.alpha)
            text_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(text_surf, text_rect)

def lerp(a, b, t):
    """Linear interpolation between a and b"""
    return a + (b - a) * t

def ease_out_cubic(t):
    """Cubic easing out function"""
    return 1 - pow(1 - t, 3)

def ease_in_out_cubic(t):
    """Cubic easing in-out function"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2

def color_lerp(color1, color2, t):
    """Interpolate between two colors"""
    return tuple(int(lerp(color1[i], color2[i], t)) for i in range(3))
